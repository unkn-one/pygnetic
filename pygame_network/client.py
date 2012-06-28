import logging
from weakref import WeakKeyDictionary, WeakValueDictionary
from functools import partial
from inspect import getmembers
import enet
from packet import PacketManager
import event

_logger = logging.getLogger(__name__)


class Client(object):
    def __init__(self, connections_limit=1, channel_limit=0, in_bandwidth=0, out_bandwidth=0):
        self.host = enet.Host(None, connections_limit, channel_limit, in_bandwidth, out_bandwidth)
        self._peers = {}

    def connect(self, address, port, channels=2, packet_manager=PacketManager):
        # Can't register packets after connection
        packet_manager._frozen = True
        address = enet.Address(address, port)
        peer = self.host.connect(address, channels, packet_manager.get_hash())
        connection = Connection(peer, packet_manager)
        self._peers[peer.connectID] = connection  # TODO: Test connectID more
        return connection

    def step(self):
        host = self.host
        event = host.service(0)
        while event is not None:
            if event.type == enet.EVENT_TYPE_CONNECT:
                _logger.info('Connected to %s', event.peer.address)
            elif event.type == enet.EVENT_TYPE_DISCONNECT:
                _logger.info('Disconnected from %s', event.peer.address)
            elif event.type == enet.EVENT_TYPE_RECEIVE:
                _logger.info('Received data from %s', event.peer.address)
                self._peers[event.peer.connectID]._receive(event.packet.data)
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
        self.connection = peer
        self._packet_cnt = 0
        self._packet_manager = packet_manager

    def __del__(self):
        self.connection.disconnect_now()

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
        if self.connection.send(channel, enet.Packet(data, flags)):
            return packet_id

    def _receive(self, data):
        packet_id, packet = self._packet_manager.unpack(data)
        print 'packet #%d: %s' % (packet_id, packet)

    def reset(self):
        self.connection.reset()

    def disconnect(self):
        self.connection.disconnect()


class Receiver(object):
    def __init__(self, *args, **kwargs):
        super(Receiver, self).__init__(*args, **kwargs)
        ReceiverManager.register(self)


class ReceiverManager(object):
    _rcvr_objs = WeakKeyDictionary()

    @classmethod
    def register(cls, obj):
        # get names of supported packets by available methods
        cls._rcvr_objs[obj] = tuple(
            name[4:]
            for name, _ in getmembers(obj, callable)
            if name.startswith('net_')
        )

    @classmethod
    def notify_all(cls, packet):
        name = packet.__name__
        for obj, packets in cls._rcvr_objs.iteritems():
            if name in packets:
                getattr(obj, 'net_' + name)(packet)
