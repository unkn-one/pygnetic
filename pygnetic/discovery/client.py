from weakref import proxy
from .. import __init__ as net
import messages


class Handler(net.Handler):
    def net_register_ack(self, message, **kwargs):
        self.parent.sid = message.sid

    def net_servers_list(self, message, **kwargs):
        pass

    def net_error(self, message, **kwargs):
        if message.type == messages.Errors.TIMEOUT:
            self._make_connection()
            self.parent.net_register(self.parent.info)

    def net_ping(self, message, **kwargs):
        self._make_connection()
        self.parent.net_ping(message.sid)


class Client(object):
    def __init__(self, host, port=5000, n_adapter=net.network.selected_adapter,
                 s_adapter=net.serialization.selected_adapter):
        messages.message_factory.s_adapter = s_adapter
        self.client = n_adapter.Client()
        self.connection = None
        self.handler = Handler()
        self.handler.parent = proxy(self)
        self.address = host, port
        self.info = ('', '', 0)
        self.sid = 0

    def _make_connection(self):
        if self.connection is None or not self.connection.connected:
            self.connection = self.client.connect(*self.address)
            self.connection.add_handler(self.handler)

    def register(self, name, host, port):
        self.info = name, host, port
        self._make_connection()
        self.connection.net_register(name, host, port)

    def ping(self):
        if self.sid == 0:
            return False
        self._make_connection()
        self.connection.net_ping(self.sid)
        return True
