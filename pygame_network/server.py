import logging
from weakref import proxy
import message
import event
from handler import Handler

_logger = logging.getLogger(__name__)


class Server(object):
    message_factory = message.message_factory
    handler = None
    connection = None

    def __init__(self, host='', port=0, conn_limit=4, *args, **kwargs):
        super(Server, self).__init__(*args, **kwargs)
        _logger.info('Server created %s:%d, connections limit: %d',
                     host, port, conn_limit)
        self.message_factory.set_frozen()
        self.conn_map = {}
        self.conn_limit = conn_limit

    def update(self, timeout=0):
        pass

    def _accept(self, mf_hash, socket, c_id, address):
        if mf_hash == self.message_factory.get_hash():
            _logger.info('Connection with %s accepted', address)
            connection = self.connection(self, socket, self.message_factory)
            if self.handler is not None and issubclass(self.handler, Handler):
                handler = self.handler()
                handler.server = proxy(self)
                connection.add_handler(handler)
            self.conn_map[c_id] = connection
            event.accepted(self)
            connection._connect()
            return True
        else:
            _logger.info('Connection with %s refused, MessageFactory'\
                            ' hash incorrect', address)
            return False

    def _disconnect(self, c_id):
        self.conn_map[c_id]._disconnect()
        del self.conn_map[c_id]

    def _receive(self, c_id, data, **kwargs):
        self.conn_map[c_id]._receive(data, **kwargs)

    def connections(self, exclude=None):
        if exclude is None:
            return self.conn_map.itervalues()
        else:
            return (c for c in self.conn_map.itervalues() if c not in exclude)

    def handlers(self, exclude=None):
        if exclude is None:
            return (c.handlers[0] for c in self.conn_map.itervalues())
        else:
            return (c.handlers[0] for c in self.conn_map.itervalues()
                    if c not in exclude)

    @property
    def address(self):
        """Server address."""
        return None, None
