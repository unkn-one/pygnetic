import logging
import socket
import select
import threading
import SocketServer
from collections import OrderedDict
from itertools import islice
import message

_logger = logging.getLogger(__name__)

message_factory = message.MessageFactory()

register = message_factory.register('register', (
    'oid', 'name', 'host', 'port'
))
get_servers = message_factory.register('get_servers', (
    'oid', 'current', 'part_size'
))
ping = message_factory.register('ping', (
    'oid', 'sid'
))
response = message_factory.register('response', (
    'oid', 'value', 'error'
))


class Errors(object):
    NO_ERROR = 0
    TIMEOUT = 1


class ServerHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        data, socket = self.request
        _logger.debug('Received data: %r', data)
        message = message_factory.unpack(data)
        if message is None:
            return
        name = message.__class__.__name__
        _logger.info('Received %s message from %s', name, self.client_address)
        ret_val, err = getattr(self, 'net_' + name)(message)
        ack_data = message_factory.pack(response(message.oid, ret_val, err))
        cnt = socket.sendto(ack_data, self.client_address)
        _logger.info('Sent response to %s', self.client_address)
        _logger.debug('Sent %d bytes: %r', cnt, ack_data)

    def unknown_msg(self, message):
        name = message.__class__.__name__
        _logger.warning('Received unknown %s message from %s',
                        name, self.client_address)

    def net_register(self, message):
        sid = self.server.id_cnt = self.server.id_cnt + 1
        self.server.servers[sid] = [message[1:], 0]
        return sid, Errors.NO_ERROR

    def net_get_servers(self, message):
        s = message.current * message.part_size
        e = s + message.part_size
        servers = self.server.servers
        d = {k: servers[k][0] for k in islice(servers.iterkeys(), s, e)}
        return d, Errors.NO_ERROR

    def net_ping(self, message):
        s = self.server.servers.get(message.sid)
        if s is not None:
            s[1] = 0
            return None, Errors.NO_ERROR
        else:
            return None, Errors.TIMEOUT


class DiscoveryServer(SocketServer.UDPServer, object):
    allow_reuse_address = True
    max_packet_size = 8192
    cleaner_period = 10
    ping_timeout = 6

    def __init__(self, host='', port=5000):
        super(DiscoveryServer, self).__init__((host, port), ServerHandler)
        self.servers = OrderedDict()
        self.id_cnt = 0
        self.c_stop = threading.Event()
        self.c_thread = threading.Thread(target=self.cleaner)
        self.c_thread.daemon = True
        self.c_thread.start()

    def __del__(self):
        self.c_stop.set()

    def cleaner(self):
        while not self.c_stop.is_set():
            keys = []
            for k, v in self.servers.iteritems():
                v[1] += 1
                if v[1] > self.ping_timeout:
                    keys.append(k)
            for k in keys:
                del self.servers[k]
            self.c_stop.wait(self.cleaner_period)


class DiscoveryClient(object):
    max_packet_size = 8192

    def __init__(self, host, port=5000):
        self.address = socket.gethostbyname(host), port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.response = None
        self.callback = None
        self.oid = 0

    def _send_msg(self, message, *args):
        oid = self.oid = self.oid + 1
        data = message_factory.pack(message(oid, *args))
        cnt = self.socket.sendto(data, self.address)
        self.response = None
        name = message.__class__.__name__
        _logger.info('Sent %s message to %s', name, self.address)
        _logger.debug('Sent %d bytes: %r', cnt, data)
        return oid

    def update(self, timeout=0):
        r = select.select([self.socket], [], [], timeout / 1000.0)[0]
        if len(r) > 0:
            data, address = self.socket.recvfrom(self.max_packet_size)
            if address == self.address:
                _logger.debug('Received data: %r', data)
                r = self.response = message_factory.unpack(data)
                _logger.info('Received response from %s', address)
                if callable(self.callback):
                    self.callback(r)
            else:
                _logger.info('Unexpected data from %s', address)

    def close(self):
        self.socket.close()

    def register(self, name, host, port):
        return self._send_msg(register, name, host, port)

    def ping(self, sid):
        return self._send_msg(ping, sid)

    def get_servers(self, current=0, part_size=10):
        return self._send_msg(get_servers, current, part_size)
