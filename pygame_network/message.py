import logging
from collections import namedtuple
from weakref import WeakKeyDictionary, WeakValueDictionary
import enet

__all__ = ('MessageFactory', 'MessageError')
_logger = logging.getLogger(__name__)
s_lib = None


class MessageError(Exception):
    pass


class MessageFactory(object):
    """Class allowing to register new message types and pack/unpack them.

    example:
        chat_msg = MessageFactory.register('chat_msg', ('player', 'msg'),
                                          enet.PACKET_FLAG_RELIABLE)
        MessageFactory.pack(chat_msg('Tom', 'Test message'))
    """
    _message_names = {}  # mapping name -> message
    _message_types = WeakValueDictionary()  # mapping type_id -> message
    _message_params = WeakKeyDictionary()  # mapping message -> type_id, send par
    _type_id_cnt = 0
    _frozen = False
    _hash = None

    def __init__(self):
        # override class variables with instance variables
        cls = self.__class__
        self._message_names = cls._message_names.copy()
        self._message_types = cls._message_types.copy()
        self._message_params = cls._message_params.copy()
        self._type_id_cnt = cls._type_id_cnt
        self._frozen = False
        self._hash = None

    @classmethod
    def register(cls, name, field_names=tuple(), channel=0, flags=enet.PACKET_FLAG_RELIABLE):
        """Register new message type

        MessageFactory.register(name, field_names, channel, flags): return class

        name - name of message class
        field_names - names of message fields

        Warning: All packets must be registered in THE SAME ORDER in client and
        server, BEFORE creating any connection.

        Returns namedtuple class.
        """
        if cls._frozen == True:
            raise MessageError("Can't register new messages after "\
                              "connection establishment")
        type_id = cls._type_id_cnt = cls._type_id_cnt + 1
        packet = namedtuple(name, field_names)
        cls._message_names[name] = packet
        cls._message_types[type_id] = packet
        cls._message_params[packet] = (type_id, channel, flags)
        return packet

    @classmethod
    def pack(cls, message_id, message):
        """Pack data to string

        MessageFactory.pack(packet_id, packet_obj): return string

        message_id - identifier of message
        message - object of class created by register

        Returns message packed in string, ready to send.
        """
        type_id = cls._message_params[message.__class__][0]
        message = (type_id, message_id) + message
        cls._message_cnt = message_id
        data = s_lib.pack(message)
        _logger.debug("Packing message (length: %d)", len(data))
        return data

    @classmethod
    def unpack(cls, data):
        """Unpack data from string, return message_id and message

        MessageFactory.unpack(data): return (message_id, message)

        data - packed message data as a string
        """
        _logger.debug("Unpacking message (length: %d)", len(data))
        message = s_lib.unpack(data)
        try:
            type_id, packet_id = message[:2]
            return packet_id, cls._message_types[type_id](*message[2:])
        except KeyError:
            _logger.warning('Unknown message type_id: %s', type_id)
        except:
            _logger.warning('Message unpacking error: %s', message)
        return None, None

    @classmethod
    def get_by_name(cls, name):
        """Returns message class with given name

        MessageFactory.get_by_name(name): return class

        name - name of message

        Returns namedtuple class.
        """
        return cls._message_names[name]

    @classmethod
    def get_by_type(cls, type_id):
        """Returns message class with given type_id

        MessageFactory.get_by_type(name): return class

        type_id - type identifier of message

        Returns namedtuple class.
        """
        return cls._message_types[type_id]

    @classmethod
    def get_params(cls, message):
        """Return tuple containing type_id, channel and sending flags

        MessageFactory.get_params(message): return (int, int, int)

        message - message class created by register
        """
        return cls._message_params[message]

    @classmethod
    def get_hash(cls):
        if cls._frozen:
            if cls._hash is None:
                ids = cls._message_types.keys()
                ids.sort()
                l = list()
                l.append(s_lib.__name__)
                for i in ids:
                    p = cls._message_types[i]
                    l.append((i, p.__name__, p._fields))
                # should be the same on 32 & 64 platforms
                cls._hash = hash(tuple(l)) & 0xffffffff
            return cls._hash
        else:
            _logger.warning('Attempt to get hash of not frozen MessageFactory')


update_remoteobject = MessageFactory.register('update_remoteobject', (
    'type_id',
    'obj_id',
    'variables'
), 1, 0)
chat_msg = MessageFactory.register('chat_msg', (
    'player',
    'msg'
))
