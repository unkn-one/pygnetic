__all__ = ('Connection',
           'STATE_ACKNOWLEDGING_CONNECT',
           'STATE_ACKNOWLEDGING_DISCONNECT',
           'STATE_CONNECTED',
           'STATE_CONNECTING',
           'STATE_CONNECTION_PENDING',
           'STATE_CONNECTION_SUCCEEDED',
           'STATE_DISCONNECTED',
           'STATE_DISCONNECTING',
           'STATE_DISCONNECT_LATER',
           'STATE_ZOMBIE')

import logging
from weakref import proxy
from functools import partial
import enet
from packet import PacketManager

_logger = logging.getLogger(__name__)

# dummy events
def _connected_event(connection): pass
def _disconnected_event(connection): pass
def _received_event(connection, channel, packet, packet_id): pass
def _response_event(connection, channel, packet, packet_id): pass

STATE_ACKNOWLEDGING_CONNECT = enet.PEER_STATE_ACKNOWLEDGING_CONNECT
STATE_ACKNOWLEDGING_DISCONNECT = enet.PEER_STATE_ACKNOWLEDGING_DISCONNECT
STATE_CONNECTED = enet.PEER_STATE_CONNECTED
STATE_CONNECTING = enet.PEER_STATE_CONNECTING
STATE_CONNECTION_PENDING = enet.PEER_STATE_CONNECTION_PENDING
STATE_CONNECTION_SUCCEEDED = enet.PEER_STATE_CONNECTION_SUCCEEDED
STATE_DISCONNECTED = enet.PEER_STATE_DISCONNECTED
STATE_DISCONNECTING = enet.PEER_STATE_DISCONNECTING
STATE_DISCONNECT_LATER = enet.PEER_STATE_DISCONNECT_LATER
STATE_ZOMBIE = enet.PEER_STATE_ZOMBIE


class Connection(object):
    """Class allowing to send packets

    It's created by by Client or Server, shouldn't be created manually.

    Sending is possible in two ways:
    * using net_<packet_name> methods, where <packet_name>
      is name of packet registered in PacketManager
    * using send method with packet as argument

    Attributes:
        parent - proxy to Client / Server instance
        peer - Enet peer instance
    """

    def __init__(self, parent, peer, packet_manager=PacketManager):
        self.parent = proxy(parent)
        self.peer = peer
        self._packet_cnt = 0
        self._packet_manager = packet_manager
        self._receivers = []

    def __del__(self):
        self.peer.disconnect_now()

    def __getattr__(self, name):
        parts = name.split('_', 1)
        if len(parts) == 2 and parts[0] == 'net' and\
                parts[1] in self._packet_manager._packet_names:
            p = partial(self._send, self._packet_manager.get_by_name(parts[1]))
            p.__doc__ = "Send %s packet to remote host\n\n"\
                "Host.net_%s: return packet_id" % \
                (parts[1], self._packet_manager._packet_names[parts[1]].__doc__)
            # add new method so __getattr__ is no longer needed
            setattr(self, name, p)
            return p
        else:
            raise AttributeError("'%s' object has no attribute '%s'" %
                                 (type(self).__name__, name))

    def send(self, packet, *args, **kwargs):
        """Send packet to remote host

        Connection.send(packet, *args, **kwargs): return int

        packet - class created by PacketManager.register or packet name

        args and kwargs are used to initialize packet object.
        Returns packet id which can be used to retrieve response from
        Pygame event queue if sending was successful.
        """
        if isinstance(packet, basestring):
            packet = self._packet_manager.get_by_name(packet)
        self._send(packet, *args, **kwargs)

    def _send(self, packet, *args, **kwargs):
        _, channel, flags = self._packet_manager.get_params(packet)
        flags = kwargs.get('flags', flags)
        channel = kwargs.get('channel', channel)
        packet_id = self._packet_cnt = self._packet_cnt + 1
        packet = packet(*args, **kwargs)
        data = self._packet_manager.pack(packet_id, packet)
        if self.peer.send(channel, enet.Packet(data, flags)) == 0:
            return packet_id

    def _receive(self, data, channel):
        packet_id, packet = self._packet_manager.unpack(data)
        name = packet.__class__.__name__
        _logger.info('Received %s packet', name)
        name = 'net_' + name
        _received_event(self, channel, packet, packet_id)
        for r in self._receivers:
            getattr(r, name, r.on_recive)(channel, packet_id, packet)

    def _connect(self):
        _connected_event(self)
        for r in self._receivers:
            r.on_connect()

    def _disconnect(self):
        _disconnected_event(self)
        for r in self._receivers:
            r.on_disconnect()

    def disconnect(self):
        """Request a disconnection.
        """
        self.peer.disconnect()

    def disconnect_later(self):
        """Request a disconnection from a peer, but only after all queued
        outgoing packets are sent.
        """
        self.peer.disconnect_later()

    def disconnect_now(self):
        """Force an immediate disconnection.
        """
        self.peer.disconnect_now()

    def add_receiver(self, receiver):
        """Add new Receiver to handle packets.

        Connection.add_receiver(receiver)

        receiver - instance of Receiver subclass
        """
        self._receivers.append(receiver)
        receiver.connection = proxy(self)

    @property
    def state(self):
        """Connection state."""
        return self.peer.state

    @property
    def address(self):
        """Connection address."""
        return self.peer.address
