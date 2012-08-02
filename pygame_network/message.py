import logging
from collections import namedtuple
from weakref import WeakKeyDictionary, WeakValueDictionary

__all__ = ('MessageFactory', 'MessageError')
_logger = logging.getLogger(__name__)
s_lib = None


class MessageError(Exception):
    pass


class MessageFactory(object):
    """Class allowing to register new message types and pack/unpack them.

    example:
        chat_msg = MessageFactory.register('chat_msg', ('player', 'msg'))
        data = MessageFactory.pack(chat_msg('Tom', 'Test message'))
        received_msg = MessageFactory.unpack(data)
        player = received_msg.player
        msg = received_msg.msg
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
    def register(cls, name, field_names=tuple(), **kwargs):
        """Register new message type

        MessageFactory.register(name, field_names[, **kwargs]): return class

        name - name of message class
        field_names - names of message fields
        args - additional arguments for sending message

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
        cls._message_params[packet] = (type_id, kwargs)
        return packet

    @classmethod
    def pack(cls, message, sys_data=[]):
        """Pack data to string

        MessageFactory.pack(packet_id, packet_obj): return string

        message - object of class created by register

        Returns message packed in string, ready to send.
        """
        type_id = cls._message_params[message.__class__][0]
        message = (type_id,) + tuple(sys_data) + message
        data = s_lib.pack(message)
        _logger.debug("Packing message (length: %d)", len(data))
        return data

    @classmethod
    def unpack(cls, data, sys_data=[]):
        """Unpack data from string, return message_id and message

        MessageFactory.unpack(data): return (message_id, message)

        data - packed message data as a string
        """
        _logger.debug("Unpacking message (length: %d)", len(data))
        message = s_lib.unpack(data)
        sys_data_l = len(sys_data)
        try:
            type_id = message[0]
            sys_data[:] = message[1:1 + sys_data_l]
            return cls._message_types[type_id](*message[1 + sys_data_l:])
        except KeyError:
            _logger.warning('Unknown message type_id: %s', type_id)
        except:
            _logger.warning('Message unpacking error: %s', message)
        return None

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
        """Return tuple containing type_id, and sending keyword args

        MessageFactory.get_params(message): return (int, dict)

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
), channel=1, flags=0)
chat_msg = MessageFactory.register('chat_msg', (
    'player',
    'msg'
))
