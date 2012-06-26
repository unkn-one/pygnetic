import logging
from collections import namedtuple
from weakref import WeakKeyDictionary, WeakValueDictionary
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

    @classmethod
    def register(cls, name, field_names, **kwargs):
        """Register new packet type

        PacketManager.register(name, field_names, **kwargs): return class

        name - name of packet class
        field_names - names of packet fields
        kwargs - keyword arguments for sending with enet

        Warning: All packets must be registered in THE SAME ORDER in client and
        server, BEFORE creating Client / Server objects.

        Returns namedtuple class.
        """
        if cls._frozen == True:
            raise PacketError("Can't register new packets after "\
                              "connection establishment")
        type_id = cls._type_id_cnt + 1
        packet = namedtuple(name, field_names)
        cls._packet_names[name] = packet
        cls._packet_types[type_id] = packet
        cls._packet_params[packet] = (type_id, kwargs)
        cls._type_id_cnt = type_id
        return packet

    @classmethod
    def pack(cls, packet_id, packet, *args, **kwargs):
        """Pack data to string

        PacketManager.pack(packet_id, packet, *args, **kwargs): return string

        packet_id - identifier of packet
        packet - object of class created by register or name of packet

        When packet is name, args and kwargs are used to initialize
        packet object. Returns packet packed in string, ready to send.
        """
        if isinstance(packet, basestring):
            packet = cls._packets[packet](*args, **kwargs)
        type_id = cls._packets_params[packet.__class__].type_id
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
        """
        return cls._packet_names[name]

    @classmethod
    def get_by_type(cls, type_id):
        """Returns packet class with given type_id

        PacketManager.get_by_type(name): return class
        """
        return cls._packet_types[type_id]

    @classmethod
    def get_params(cls, packet):
        """Return tuple containing type_id and sending keyword arguments

        PacketManager.get_params(packet): return (int, dict)
        """
        return cls._packet_params[packet.__class__]


connect_request = PacketManager.register('connect_request', (
    'packets_hash',
))
update_remoteobject = PacketManager.register('update_remoteobject', (
    'type_id',
    'obj_id',
    'variables'
))
chat_msg = PacketManager.register('chat_msg', (
    'player',
    'msg'
), enet.PACKET_FLAG_RELIABLE)
