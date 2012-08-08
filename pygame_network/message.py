import logging
from collections import namedtuple
from weakref import WeakKeyDictionary, WeakValueDictionary
import serialization

__all__ = ('MessageFactory', 'MessageError')
_logger = logging.getLogger(__name__)


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
    def __init__(self):
        self._message_names = {}  # mapping name -> message
        self._message_types = WeakValueDictionary()  # mapping type_id -> message
        self._message_params = WeakKeyDictionary()  # mapping message -> type_id, send par
        self._type_id_cnt = 0
        self._frozen = False
        self._hash = None

    def register(self, name, field_names=tuple(), **kwargs):
        """Register new message type

        MessageFactory.register(name, field_names[, **kwargs]): return class

        name - name of message class
        field_names - names of message fields
        args - additional arguments for sending message

        Warning: All packets must be registered in THE SAME ORDER in client and
        server, BEFORE creating any connection.

        Returns namedtuple class.
        """
        if self._frozen == True:
            raise MessageError("Can't register new messages after "
                               "connection establishment")
        type_id = self._type_id_cnt = self._type_id_cnt + 1
        packet = namedtuple(name, field_names)
        self._message_names[name] = packet
        self._message_types[type_id] = packet
        self._message_params[packet] = (type_id, kwargs)
        return packet

    def pack(self, message):
        """Pack data to string

        MessageFactory.pack(packet_id, packet_obj): return string

        message - object of class created by register

        Returns message packed in string, ready to send.
        """
        type_id = self._message_params[message.__class__][0]
        message = (type_id,) + message
        data = serialization.pack(message)
        _logger.debug("Packing message (length: %d)", len(data))
        return data

    def set_frozen(self):
        self._frozen = True

    def reset_context(self, context):
        context._unpacker = serialization.unpacker()

    def _process_message(self, message):
        try:
            type_id = message[0]
            return self._message_types[type_id](*message[1:])
        except KeyError:
            _logger.error('Unknown message type_id: %s', type_id)
        except:
            _logger.error('Message unpacking error: %s', message)

    def unpack(self, data):
        """Unpack data from string and buffer, return message

        MessageFactory.unpack(data): return message

        data - packed message data as a string
        """
        _logger.debug("Unpacking message (length: %d)", len(data))
        try:
            message = serialization.unpack(data)
        except:
            _logger.error('Data corrupted')
            self._reset_unpacker()  # prevent from corrupting next data
            return
        return self._process_message(message)

    def unpack_all(self, data, context):
        """Unpack all data from string and buffer, return message generator

        MessageFactory.unpack(data): return message generator

        data - packed data as a string
        """
        _logger.debug("Unpacking data (length: %d)", len(data))
        context._unpacker.feed(data)
        try:
            for message in context._unpacker:
                yield self._process_message(message)
        except:
            _logger.error('Data corrupted')
            self._reset_unpacker()  # prevent from corrupting next data
            return

    def get_by_name(self, name):
        """Returns message class with given name

        MessageFactory.get_by_name(name): return class

        name - name of message

        Returns namedtuple class.
        """
        return self._message_names[name]

    def get_by_type(self, type_id):
        """Returns message class with given type_id

        MessageFactory.get_by_type(name): return class

        type_id - type identifier of message

        Returns namedtuple class.
        """
        return self._message_types[type_id]

    def get_params(self, message):
        """Return tuple containing type_id, and sending keyword args

        MessageFactory.get_params(message): return (int, dict)

        message - message class created by register
        """
        return self._message_params[message]

    def get_hash(self):
        """Calculate and return hash.

        Hash depends on registered messages and used serializing library.
        """
        if self._frozen:
            if self._hash is None:
                ids = self._message_types.keys()
                ids.sort()
                l = list()
                l.append(serialization._selected_adapter.__name__)
                for i in ids:
                    p = self._message_types[i]
                    l.append((i, p.__name__, p._fields))
                # should be the same on 32 & 64 platforms
                self._hash = hash(tuple(l)) & 0xffffffff
            return self._hash
        else:
            _logger.warning('Attempt to get hash of not frozen MessageFactory')


message_factory = MessageFactory()
update_remoteobject = message_factory.register('update_remoteobject', (
    'type_id',
    'obj_id',
    'variables'
), channel=1, flags=0)
chat_msg = message_factory.register('chat_msg', (
    'player',
    'msg'
))
