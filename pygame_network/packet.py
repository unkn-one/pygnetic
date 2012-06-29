import logging
from collections import namedtuple
from weakref import WeakKeyDictionary, WeakValueDictionary
import enet
try:
    import msgpack
    _packer = msgpack.Packer()
    _unpacker = msgpack.Unpacker()
    _pack = _packer.pack
    _unpack = lambda data: _unpacker.feed(data) or _unpacker.unpack()
except ImportError:
    import json
    _packer = json.JSONEncoder()
    _unpacker = json.JSONDecoder()
    _pack = _packer.encode
    _unpack = _unpacker.decode

_logger = logging.getLogger(__name__)

__all__ = ('PacketManager', 'PacketError')


class PacketError(Exception):
    pass


class PacketManager(object):
    """Class allowing to register new packet types and pack/unpack them.

    example:
        chat_msg = PacketManager.register('chat_msg', ('player', 'msg'),
                                          enet.PACKET_FLAG_RELIABLE)
        PacketManager.pack(chat_msg('Tom', 'Test message'))
    """
    _packet_names = {}  # mapping name -> packet
    _packet_types = WeakValueDictionary()  # mapping type_id -> packet
    _packet_params = WeakKeyDictionary()  # mapping packet -> type_id, send par
    _type_id_cnt = 0
    _frozen = False

    def __init__(self):
        # override class variables with instance variables
        cls = self.__class__
        self._packet_names = cls._packet_names.copy()
        self._packet_types = cls._packet_types.copy()
        self._packet_params = cls._packet_params.copy()
        self._type_id_cnt = cls._type_id_cnt
        self._frozen = False

    @classmethod
    def register(cls, name, field_names, channel=0, flags=enet.PACKET_FLAG_RELIABLE):
        """Register new packet type

        PacketManager.register(name, field_names, channel, flags): return class

        name - name of packet class
        field_names - names of packet fields

        Warning: All packets must be registered in THE SAME ORDER in client and
        server, BEFORE creating any connection.

        Returns namedtuple class.
        """
        if cls._frozen == True:
            raise PacketError("Can't register new packets after "\
                              "connection establishment")
        type_id = cls._type_id_cnt + 1
        packet = namedtuple(name, field_names)
        cls._packet_names[name] = packet
        cls._packet_types[type_id] = packet
        cls._packet_params[packet] = (type_id, channel, flags)
        cls._type_id_cnt = type_id
        return packet

    @classmethod
    def pack(cls, packet_id, packet):
        """Pack data to string

        PacketManager.pack(packet_id, packet_obj): return string

        packet_id - identifier of packet
        packet - object of class created by register

        Returns packet packed in string, ready to send.
        """
        type_id = cls._packet_params[packet.__class__][0]
        packet = (type_id, packet_id) + packet
        cls._packet_cnt = packet_id
        return _pack(packet)

    @classmethod
    def unpack(cls, data):
        """Unpack data from string, return packet_id and packet

        PacketManager.unpack(data): return (packet_id, packet)

        data - packet data as a string
        """
        packet = _unpack(data)
        try:
            type_id, packet_id = packet[:2]
            return packet_id, cls._packet_types[type_id](*packet[2:])
        except KeyError:
            _logger.warning('Unknown packet type_id: %s', type_id)
        except:
            _logger.warning('Packet unpacking error: %s', packet)
        return None, None

    @classmethod
    def get_by_name(cls, name):
        """Returns packet class with given name

        PacketManager.get_by_name(name): return class

        name - name of packet
        """
        return cls._packet_names[name]

    @classmethod
    def get_by_type(cls, type_id):
        """Returns packet class with given type_id

        PacketManager.get_by_type(name): return class

        type_id - type identifier of packet
        """
        return cls._packet_types[type_id]

    @classmethod
    def get_params(cls, packet):
        """Return tuple containing type_id, channel and sending flags

        PacketManager.get_params(packet): return (int, int, int)

        packet - packet class created by register
        """
        return cls._packet_params[packet]

    @classmethod
    def get_hash(cls):
        if cls._frozen:
            ids = cls._packet_types.keys()
            ids.sort()
            l = list()
            for i in ids:
                p = cls._packet_types[i]
                l.append((i, p.__name__, p._fields))
            return hash(tuple(l)) & 0xffffffff
            # should be the same on 32 & 64 platforms
        else:
            _logger.warning('Attempt to get hash of not frozen PacketManager')


connect_request = PacketManager.register('connect_request', (
    'packets_hash',
))
update_remoteobject = PacketManager.register('update_remoteobject', (
    'type_id',
    'obj_id',
    'variables'
), 1, 0)
chat_msg = PacketManager.register('chat_msg', (
    'player',
    'msg'
))
