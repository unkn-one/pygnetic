import re
import logging
from weakref import proxy
from functools import partial
import message
import event

_logger = logging.getLogger(__name__)


class Connection(object):
    """Class allowing to send messages

    It's created by by Client or Server, shouldn't be created manually.

    Sending is possible in two ways:
    * using net_<message_name> methods, where <message_name>
      is name of message registered in MessageFactory
    * using send method with message as argument

    Attributes:
        parent - proxy to Client / Server instance
        address - connection address
        connected - True if connected
        data_sent - amount of data sent
        data_received - amount of data received
        messages_sent - amount of messages sent
        messages_received - amount of messages received
    """

    def __init__(self, parent, message_factory, *args, **kwargs):
        super(Connection, self).__init__(*args, **kwargs)
        self.parent = proxy(parent)
        self.message_factory = message_factory
        self.message_factory.reset_context(self)
        self.handlers = []
        self.data_sent = 0
        self.data_received = 0
        self.messages_sent = 0
        self.messages_received = 0

    def __getattr__(self, name):
        parts = name.split('_', 1)
        if (len(parts) == 2 and parts[0] == 'net' and
                parts[1] in self.message_factory._message_names):
            p = partial(self._send_message,
                self.message_factory.get_by_name(parts[1]))
            p.__doc__ = "Send %s message to remote host\n\nHost.net_%s" % (
                parts[1],
                self.message_factory._message_names[parts[1]].__doc__)
            # add new method so __getattr__ is no longer needed
            setattr(self, name, p)
            return p
        else:
            raise AttributeError("'%s' object has no attribute '%s'" %
                                 (type(self).__name__, name))

    def send(self, message, *args, **kwargs):
        """Send message to remote host

        Connection.send(message, *args, **kwargs): return int

        message - class created by MessageFactory.register or message name

        args and kwargs are used to initialize message object.
        Returns message id which can be used to retrieve response from
        Pygame event queue if sending was successful.
        """
        if isinstance(message, basestring):
            message = self.message_factory.get_by_name(message)
        self._send_message(message, *args, **kwargs)

    def _send_message(self, message, *args, **kwargs):
        name = message.__name__
        params = self.message_factory.get_params(message)[1]
        try:
            message_ = message(*args, **kwargs)
        except TypeError, e:
            e, f = re.findall(r'[^_a-z](\d+)', e.message, re.I)
            raise TypeError('%s takes exactly %d arguments (%d given)' %
                (message.__doc__, int(e) - 1, int(f) - 1))
        data = self.message_factory.pack(message_)
        _logger.info('Sent %s message to %s', name, self.address)
        self.data_sent += len(data)
        self.messages_sent += 1
        return self._send_data(data, **params)

    def _receive(self, data, **kwargs):
        for message in self.message_factory.unpack_all(data, self):
            name = message.__class__.__name__
            _logger.info('Received %s message from %s', name, self.address)
            event.received(self, message)
            for h in self.handlers:
                getattr(h, 'net_' + name, h.on_recive)(message, **kwargs)

    def _connect(self):
        _logger.info('Connected to %s', self.address)
        event.connected(self)
        for h in self.handlers:
            h.on_connect()

    def _disconnect(self):
        _logger.info('Disconnected from %s', self.address)
        event.disconnected(self)
        for h in self.handlers:
            h.on_disconnect()

    def disconnect(self, *args):
        """Request a disconnection."""
        pass

    def add_handler(self, handler):
        """Add new Handler to handle messages.

        Connection.add_handler(handler)

        handler - instance of Receiver subclass
        """
        self.handlers.append(handler)
        handler.connection = proxy(self)

    @property
    def address(self):
        """Connection address."""
        return '', ''
