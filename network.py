from threading import Thread, Event
from collections import namedtuple
import weakref
import enet
try:
    raise ImportError
    import msgpack
    _packer = msgpack.Packer()
    _unpacker = msgpack.Unpacker()
    pack = _packer.pack
    unpack = _unpacker.unpack
except ImportError:
    import json
    _packer = json.JSONEncoder()
    _unpacker = json.JSONDecoder()
    pack = _packer.encode
    unpack = _unpacker.decode

__all__ = ('PacketManager', 'Host', 'RemoteObject')

class Host(object):
    peer = None
    channel = None

    def __getattr__(self, name):
        parts = name.split('_', 1)
        if len(parts) == 2 and parts[0] == 'net' and len(parts[1]) > 0:
            return lambda *args, **kwargs: self.send(parts[1], *args, **kwargs)
        else:
            raise AttributeError("'%s' object has no attribute '%s'" % (type(self).__name__, name))

    def send(self, packet, *args, **kwargs):
        return PacketManager.send(self.peer, self.channel, packet, *args, **kwargs)

class RemoteObject(object):
    synch = ()

    def __init__(self, *args, **kwargs):
        super(RemoteObject, self).__init__(*args, **kwargs)
        self._changed = False

    def _synch_var(self):
        return ((k,v) for k,v in self.__dict__.iteritems() if k in self.synch)

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        object.__setattr__(self, '_changed', self._changed or name in self.synch)

class Player(RemoteObject):
    synch = ('x', 'y')
    def __init__(self):
        super(Player, self).__init__()
        self.name = 'test'
        self.x = self.y = 0

class PacketManager(object):
    packets = {}
    packets_params = weakref.WeakKeyDictionary()
    type_id_cnt = 0
    packet_cnt = 0

    @staticmethod
    def register(name, field_names, flags = enet.PACKET_FLAG_RELIABLE):
        type_id = PacketManager.type_id_cnt + 1
        cls = namedtuple(name, field_names)
        PacketManager.packets[name] = cls
        PacketManager.packets_params[cls] = (type_id, flags)
        PacketManager.type_id_cnt = type_id
        return cls

    @staticmethod
    def send(peer, channel, packet, *args, **kwargs):
        if isinstance(packet, basestring):
            packet = PacketManager.packets[packet](*args, **kwargs)
        packet_id = (PacketManager.packet_cnt + 1) % 256
        type_id, flags = PacketManager.packets_params[packet.__class__]
        packet = (type_id, packet_id) + packet
        print pack(packet)
        #e_packet = enet.Packet(pack(packet), flags)
        #peer.send(channel, e_packet)
        PacketManager.packet_cnt = packet_id
        return packet_id
