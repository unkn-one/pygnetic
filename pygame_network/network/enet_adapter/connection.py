import logging
from weakref import proxy
from functools import partial
import enet
from ...message import MessageFactory
from ... import event

__all__ = ('Connection', 'State')
_logger = logging.getLogger(__name__)


class State(object):
    ACKNOWLEDGING_CONNECT = enet.PEER_STATE_ACKNOWLEDGING_CONNECT
    ACKNOWLEDGING_DISCONNECT = enet.PEER_STATE_ACKNOWLEDGING_DISCONNECT
    CONNECTED = enet.PEER_STATE_CONNECTED
    CONNECTING = enet.PEER_STATE_CONNECTING
    CONNECTION_PENDING = enet.PEER_STATE_CONNECTION_PENDING
    CONNECTION_SUCCEEDED = enet.PEER_STATE_CONNECTION_SUCCEEDED
    DISCONNECTED = enet.PEER_STATE_DISCONNECTED
    DISCONNECTING = enet.PEER_STATE_DISCONNECTING
    DISCONNECT_LATER = enet.PEER_STATE_DISCONNECT_LATER
    ZOMBIE = enet.PEER_STATE_ZOMBIE


class Connection(object):
    """Class allowing to send messages

    It's created by by Client or Server, shouldn't be created manually.

    Sending is possible in two ways:
    * using net_<message_name> methods, where <message_name>
      is name of message registered in MessageFactory
    * using send method with message as argument

    Attributes:
        parent - proxy to Client / Server instance
        peer - Enet peer instance
    """

    def __init__(self, parent, peer, message_factory=MessageFactory):
        self.parent = proxy(parent)
        self.peer = peer
        self._message_cnt = 0
        self._message_factory = message_factory
        self._handlers = []

    def __del__(self):
        self.peer.disconnect_now()

    def __getattr__(self, name):
        parts = name.split('_', 1)
        if len(parts) == 2 and parts[0] == 'net' and\
                parts[1] in self._message_factory._message_names:
            p = partial(self._send, self._message_factory.get_by_name(parts[1]))
            p.__doc__ = "Send %s message to remote host\n\n"\
                "Host.net_%s: return message_id" % \
                (parts[1], self._message_factory._message_names[parts[1]].__doc__)
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
        self._send(message, *args, **kwargs)

    def _send(self, message, *args, **kwargs):
        _, channel, flags = self._message_factory.get_params(message)
        flags = kwargs.get('flags', flags)
        channel = kwargs.get('channel', channel)
        message_id = self._message_cnt = self._message_cnt + 1
        name = message.__name__
        message = message(*args, **kwargs)
        data = self._message_factory.pack(message_id, message)
        if self.peer.send(channel, enet.Packet(data, flags)) == 0:
            _logger.info('Sent %s message on channel %d', name, channel)
            return message_id

    def _receive(self, data, channel):
        message_id, message = self._message_factory.unpack(data)
        name = message.__class__.__name__
        _logger.info('Received %s message on channel %d', name, channel)
        name = 'net_' + name
        event.received(self, channel, message, message_id)
        for r in self._handlers:
            getattr(r, name, r.on_recive)(channel, message_id, message)

    def _connect(self):
        event.connected(self)
        for r in self._handlers:
            r.on_connect()

    def _disconnect(self):
        event.disconnected(self)
        for r in self._handlers:
            r.on_disconnect()

    def disconnect(self):
        """Request a disconnection.
        """
        self.peer.disconnect()

    def disconnect_later(self):
        """Request a disconnection from a peer, but only after all queued
        outgoing messages are sent.
        """
        self.peer.disconnect_later()

    def disconnect_now(self):
        """Force an immediate disconnection.
        """
        self.peer.disconnect_now()

    def add_handler(self, handler):
        """Add new Receiver to handle messages.

        Connection.add_handler(handler)

        handler - instance of Receiver subclass
        """
        self._handlers.append(handler)
        handler.connection = proxy(self)

    @property
    def state(self):
        """Connection state."""
        return self.peer.state

    @property
    def address(self):
        """Connection address."""
        return self.peer.address
