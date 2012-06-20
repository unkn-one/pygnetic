from collections import namedtuple
from weakref import WeakKeyDictionary
import enet
try:
    import msgpack
    _packer = msgpack.Packer()
    _unpacker = msgpack.Unpacker()
    _pack = _packer.pack
    _unpack = _unpacker.unpack
except ImportError:
    import json
    _packer = json.JSONEncoder()
    _unpacker = json.JSONDecoder()
    _pack = _packer.encode
    _unpack = _unpacker.decode


class PacketManager(object):
    """Class allowing to register new packet types and send them.

    example:
        chat_msg = PacketManager.register('chat_msg', ('player', 'msg'),
                                          enet.PACKET_FLAG_RELIABLE)
        PacketManager.send(peer, 0, chat_msg('Tom', 'Test message'))
    """
    _packets = {}
    _packets_params = WeakKeyDictionary()
    _type_id_cnt = 0
    _packet_cnt = 0

    @classmethod
    def register(cls, name, field_names, flags=enet.PACKET_FLAG_RELIABLE):
        """Register new packet type

        PacketManager.register(name, field_names, flags): return class

        name - name of packet class
        field_names - names of packet fields
        flags - enet flags used when sending packet

        Returns namedtuple class.
        """
        type_id = cls._type_id_cnt + 1
        packet = namedtuple(name, field_names)
        cls._packets[name] = packet
        cls._packets_params[packet] = (type_id, flags)
        cls._type_id_cnt = type_id
        return packet

    @classmethod
    def send(cls, peer, channel, packet, *args, **kwargs):
        """Send packet

        PacketManager.send(peer, channel, packet, \*args, \*\*kwargs): return int

        peer - connection to send packet over
        channel - channel of connection
        packet - object of class created by register or name of packet

        When packet is name, args and kwargs are used to initialize
        packet object. Returns packet id which can be used to retrieve response
        from Pygame event queue.
        """
        override_flags = kwargs.pop('flags', None)
        if isinstance(packet, basestring):
            packet = cls._packets[packet](*args, **kwargs)
        packet_id = (cls._packet_cnt + 1) % 256
        type_id, flags = cls._packets_params[packet.__class__]
        flags = flags if override_flags is None else override_flags
        packet = (type_id, packet_id) + packet
        print 'msg:', packet, 'len:', len(_pack(packet))
        #e_packet = enet.Packet(_pack(packet), flags)
        #peer.send(channel, e_packet)
        cls._packet_cnt = packet_id
        return packet_id

    @classmethod
    def get_packet(cls, name):
        """Returns packet class with given name

        PacketManager.get_packet(name): return class
        """
        return cls._packets[name]

update_remoteobject = PacketManager.register('update_remoteobject', ('type_id', 'obj_id', 'variables'))
chat_msg = PacketManager.register('chat_msg', ('player', 'msg'), enet.PACKET_FLAG_RELIABLE)
