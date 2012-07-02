import logging
from weakref import WeakKeyDictionary, WeakValueDictionary
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


class Client(object):
    def __init__(self, connections_limit=1, channel_limit=0, in_bandwidth=0, out_bandwidth=0):
        self.host = enet.Host(None, connections_limit, channel_limit, in_bandwidth, out_bandwidth)
        self._peers = {}
        self._peer_cnt = 0

    def connect(self, address, port, channels=2, packet_manager=PacketManager):
        peer_id = self._peer_cnt = self._peer_cnt + 1
        peer_id = str(peer_id)
        # Can't register packets after connection
        packet_manager._frozen = True
        address = enet.Address(address, port)
        peer = self.host.connect(address, channels, packet_manager.get_hash())
        peer.data = peer_id
        connection = Connection(peer, packet_manager)
        self._peers[peer_id] = connection
        return connection

    def step(self, timeout=0):
        if len(self._peers) == 0:
            return
        host = self.host
        event = host.service(timeout)
        while event is not None:
            if event.type == enet.EVENT_TYPE_CONNECT:
                self._peers[event.peer.data]._connect()
                _logger.info('Connected to %s', event.peer.address)
            elif event.type == enet.EVENT_TYPE_DISCONNECT:
                self._peers[event.peer.data]._disconnect()
                _logger.info('Disconnected from %s', event.peer.address)
                del self._peers[event.peer.data]
            elif event.type == enet.EVENT_TYPE_RECEIVE:
                self._peers[event.peer.data]._receive(event.packet.data, event.channelID)
                _logger.info('Received data from %s', event.peer.address)
            event = host.check_events()


class Connection(object):
    """Class allowing to send messages and packets

    peer - connection to send packet over
    channel - channel of connection

    example:
        client = Client()
        # chat_msg packet is defined in packets module
        client.net_chat_msg('Tom', 'Test message')
        # alternative
        client.send(packets.chat_msg('Tom', 'Test message'))
    """

    def __init__(self, peer, packet_manager=PacketManager):
        self.peer = peer
        self._packet_cnt = 0
        self._packet_manager = packet_manager

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

        Client.send(packet, *args, **kwargs): return int

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
        _received_event(self, channel, packet, packet_id)
        ReceiverManager.on_recive(self, channel, packet_id, packet)

    def _connect(self):
        _connected_event(self)
        ReceiverManager.on_connect(self)

    def _disconnect(self):
        _disconnected_event(self)
        ReceiverManager.on_disconnect(self)

    def disconnect(self):
        self.peer.disconnect()

    def disconnect_later(self):
        self.peer.disconnect_later()

    @property
    def state(self):
        return self.peer.state

    @property
    def address(self):
        return self.peer.address


class ReceiverManager(object):
    _receivers = WeakKeyDictionary()

    @classmethod
    def register(cls, obj):
        cls._receivers[obj] = None

    @classmethod
    def on_recive(cls, connection, channel, packet_id, packet):
        name = packet.__class__.__name__
        for obj in cls._receivers:
            if obj.connection == connection:
                getattr(obj, 'net_' + name, obj.on_recive)(channel, packet_id, packet)

    @classmethod
    def on_connect(cls, connection):
        for obj in cls._receivers:
            if obj.connection == connection:
                obj.on_connect()

    @classmethod
    def on_disconnect(cls, connection):
        for obj in cls._receivers:
            if obj.connection == connection:
                obj.on_disconnect()


class Receiver(object):
    connection = None

    def __init__(self, *args, **kwargs):
        super(Receiver, self).__init__(*args, **kwargs)
        ReceiverManager.register(self)

    def on_connect(self):
        pass

    def on_disconnect(self):
        pass

    def on_recive(self, channel, packet_id, packet):
        pass
