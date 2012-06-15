from collections import namedtuple
from weakref import WeakKeyDictionary
import enet
try:
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

class PacketManager(object):
    packets = {}
    packets_params = WeakKeyDictionary()
    type_id_cnt = 0
    packet_cnt = 0

    @classmethod
    def register(cls, name, field_names, flags=enet.PACKET_FLAG_RELIABLE):
        type_id = cls.type_id_cnt + 1
        packet = namedtuple(name, field_names)
        cls.packets[name] = packet
        cls.packets_params[packet] = (type_id, flags)
        cls.type_id_cnt = type_id
        return packet

    @classmethod
    def send(cls, peer, channel, packet, *args, **kwargs):
        override_flags = kwargs.pop('flags', None)
        if isinstance(packet, basestring):
            packet = cls.packets[packet](*args, **kwargs)
        packet_id = (cls.packet_cnt + 1) % 256
        type_id, flags = cls.packets_params[packet.__class__]
        flags = flags if override_flags is None else override_flags
        packet = (type_id, packet_id) + packet
        print 'msg:', packet, 'len:', len(pack(packet))
        #e_packet = enet.Packet(pack(packet), flags)
        #peer.send(channel, e_packet)
        PacketManager.packet_cnt = packet_id
        return packet_id

update_remoteobject = PacketManager.register('update_remoteobject', ('type_id', 'obj_id', 'variables'))
chat_msg = PacketManager.register('chat_msg', ('player', 'msg'), enet.PACKET_FLAG_RELIABLE)