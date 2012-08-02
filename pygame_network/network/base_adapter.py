import re
import logging
from weakref import proxy
from functools import partial
from ..message import MessageFactory
from .. import event

__all__ = ('Connection', 'State')
_logger = logging.getLogger(__name__)


class State(object):
    (CONNECTED,
    CONNECTING,
    DISCONNECTED,
    DISCONNECTING) = range(4)


class Connection(object):
    """Class allowing to send messages

    It's created by by Client or Server, shouldn't be created manually.

    Sending is possible in two ways:
    * using net_<message_name> methods, where <message_name>
      is name of message registered in MessageFactory
    * using send method with message as argument

    """

    def __init__(self, parent, message_factory=MessageFactory):
        self.parent = proxy(parent)
        self._message_cnt = 0
        self._message_factory = message_factory
        self._handlers = []

    def __getattr__(self, name):
        parts = name.split('_', 1)
        if len(parts) == 2 and parts[0] == 'net' and\
                parts[1] in self._message_factory._message_names:
            p = partial(self._send_message, self._message_factory.get_by_name(parts[1]))
            p.__doc__ = "Send %s message to remote host\n\nHost.net_%s" % (
                parts[1],
                self._message_factory._message_names[parts[1]].__doc__
            )
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
            message = self._message_factory.get_by_name(message)
        self._send_message(message, *args, **kwargs)

    def _send_message(self, message, *args, **kwargs):
        name = message.__name__
        params = self._message_factory.get_params(message)[1]
        try:
            message_ = message(*args, **kwargs)
        except TypeError, e:
            e, f = re.findall(r'\d', e.message)
            raise TypeError('%s takes exactly %d arguments (%d given)' %
                (message.__doc__, int(e) - 1, int(f) - 1))
        data = self._message_factory.pack(message_)
        _logger.info('Sent %s message to %s:%s', name, *self.address)
        return self._send_data(data, **params)

    def _receive(self, data, channel=0):
        message = self._message_factory.unpack(data)
        name = message.__class__.__name__
        _logger.info('Received %s message from %s:%s', name, *self.address)
        event.received(self, message, channel)
        for h in self._handlers:
            getattr(h, 'net_' + name, h.on_recive)(message, channel)

    def _connect(self):
        _logger.info('Connected to %s:%s', *self.address)
        event.connected(self)
        for h in self._handlers:
            h.on_connect()

    def _disconnect(self):
        _logger.info('Disconnected from %s:%s', *self.address)
        event.disconnected(self)
        for h in self._handlers:
            h.on_disconnect()

    def disconnect(self, *args):
        """Request a disconnection."""
        pass

    def add_handler(self, handler):
        """Add new Handler to handle messages.

        Connection.add_handler(handler)

        handler - instance of Receiver subclass
        """
        self._handlers.append(handler)
        handler.connection = proxy(self)

    @property
    def state(self):
        """Connection state."""
        return State.DISCONNECTED

    @property
    def address(self):
        """Connection address."""
        return None, None


class Server(object):
    message_factory = MessageFactory
    handler_cls = None

    def __init__(self, address='', port=0, connections_limit=4, *args, **kwargs):
        _logger.debug('Server created %s, connections limit: %d', address, connections_limit)
        self.message_factory._frozen = True
        _logger.debug('MessageFactory frozen')
        self.peers = {}

    def step(self, timeout=0):
        pass

    def connections(self, exclude=None):
        if exclude is None:
            return self.peers.itervalues()
        else:
            return (c for c in self.peers.itervalues() if c not in exclude)

    def handlers(self, exclude=None):
        if exclude is None:
            return (c._handlers[0] for c in self.peers.itervalues())
        else:
            return (c._handlers[0] for c in self.peers.itervalues() if c not in exclude)

