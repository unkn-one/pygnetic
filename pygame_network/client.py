import logging
import message

_logger = logging.getLogger(__name__)


class Client(object):
    """Class representing network client

    Example:
        client = pygame_network.client.Client()
        connection = client.connect("localhost", 10000)
        while True:
            client.update()
    """
    message_factory = message.message_factory

    def __init__(self, conn_limit=1, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)
        self.conn_map = {}
        _logger.info('Client created, connections limit: %d', conn_limit)

    def connect(self, address, port, message_factory=None, **kwargs):
        if message_factory is None:
            message_factory = self.message_factory
        _logger.info('Connecting to %s:%d', address, port)
        message_factory.set_frozen()
        socket, c_id = self._create_connection(address, port,
            message_factory.get_hash(), **kwargs)
        conn = self.connection(self, socket, message_factory)
        self.conn_map[c_id] = conn
        return conn

    def update(self, timeout=0):
        pass

    def _connect(self, c_id):
        self.conn_map[c_id]._connect()

    def _disconnect(self, c_id):
        self.conn_map[c_id]._disconnect()
        del self.conn_map[c_id]

    def _receive(self, c_id, data, **kwargs):
        self.conn_map[c_id]._receive(data, **kwargs)
