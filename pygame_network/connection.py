from weakref import WeakKeyDictionary, proxy
from functools import partial
import enet
from packet import PacketManager

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
        name = 'net_' + packet.__class__.__name__
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
        self.peer.disconnect()

    def disconnect_later(self):
        self.peer.disconnect_later()

    def add_receiver(self, receiver):
        self._receivers.append(receiver)
        receiver.connection = proxy(self)

    @property
    def state(self):
        return self.peer.state

    @property
    def address(self):
        return self.peer.address


class Receiver(object):
    def on_connect(self):
        pass

    def on_disconnect(self):
        pass

    def on_recive(self, channel, packet_id, packet):
        pass
