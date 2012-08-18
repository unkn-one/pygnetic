import logging
import socket
import select
import SocketServer
from collections import OrderedDict
from itertools import islice
from .. import __init__ as net
from .. import message

_logger = logging.getLogger(__name__)

message_factory = message.MessageFactory()
# server messages
register = message_factory.register('register', (
    'name', 'host', 'port'
))
get_servers = message_factory.register('get_servers', (
    'current', 'list_step'
))
servers_list = message_factory.register('servers_list', (
    'servers'
))
ping = message_factory.register('ping', (
    'sid'
))
error = message_factory.register('error', (
    'type'
))
ack = message_factory.register('ack', (
    'value'
))


class Errors(object):
    TIMEOUT = 1


class ServerHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data, socket = self.request
        message = message_factory.unpack(data)
        if message is None:
            return
        ret_value = getattr(self, 'net_' + message.__class__.__name__)(message)
        ack_data = message_factory.pack(ack(ret_value))
        socket.sendto(ack_data, self.client_address)

    def unknown_msg(self, message):
        _logger.warning('Received unknown message: %s', message.__calss__.__name__)

    def net_register(self, message):
        sid = self.server.id_cnt = self.server.id_cnt + 1
        self.server.servers[sid] = [message, 0]
        return sid

    def net_get_servers(self, message):
        s = message.current * message.list_step
        e = s + message.list_step
        servers = self.server.servers
        return {k: servers[k][0] for k in islice(servers.iterkeys(), s, e)}


class DiscoveryServer(SocketServer.UDPServer):
    allow_reuse_address = True
    max_packet_size = 8192

    def __init__(self, host, port):
        super(DiscoveryServer, self).__init__((host, port), ServerHandler)
        self.servers = OrderedDict()
        self.id_cnt = 0


class DiscoveryClient(object):
    max_packet_size = 8192

    def __init__(self, host, port, s_adapter=net.serialization.selected_adapter):
        self.address = host, port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.response = None
        self.sid = 0

    def _send_msg(self, message):
        data = message_factory.pack(message)
        self.socket.sendto(data, self.address)

    def update(self, timeout=0):
        r = select.select([self.socket], [], [], timeout / 1000.0)[0]
        if len(r) > 0:
            data, address = self.socket.recvfrom(self.max_packet_size)
            if address == self.address:
                self.response = message_factory.unpack(data)

    def close(self):
        self.socket.close()

    def register(self, name, host, port):
        self._send_msg(register(name, host, port))

    def ping(self):
        if self.sid == 0:
            return False
        self._make_connection()
        self.connection.net_ping(self.sid)
        return True
