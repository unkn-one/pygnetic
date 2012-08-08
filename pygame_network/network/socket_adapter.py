import logging
import socket
import asyncore
from collections import deque
from .. import connection, server, client

_logger = logging.getLogger(__name__)


class Connection(connection.Connection, asyncore.dispatcher):
    __send = asyncore.dispatcher.send
    # maximum amount of data received / sent at once
    recv_buffer_size = 4096

    def __init__(self, parent, socket, message_factory, *args, **kwargs):
        super(Connection, self).__init__(
            parent, message_factory, # params for base_adapter.Connection
            socket, parent.conn_map, # params for asyncore.dispatcher
            * args, **kwargs)
        #self.send_queue = deque()
        self.send_buffer = bytearray()
        self.recv_buffer = bytearray(b'\0' * self.recv_buffer_size)

    def _send_data(self, data, **kwargs):
        self.send_buffer.extend(data)
        self._send_part()

#    def _send_data2(self, data, **kwargs):
#        if len(self.send_buffer) == 0:
#            self.send_buffer = data
#        else:
#            self.send_queue.append(data)
#        self._send_part()

    def handle_write(self):
        self._send_part()

    def _send_part(self):
        try:
            num_sent = self.__send(self.send_buffer)
        except socket.error:
            self.handle_error()
            return
        self.send_buffer = self.send_buffer[num_sent:]

    def writable(self):
        return (not self.connected) or len(self.send_buffer)

    def handle_read(self):
        # tinkering with dispatcher internal variables,
        # because it doesn't support socket.recv_into
        try:
            data = self.socket.recv_into(self.recv_buffer)
            if not data:
                self.handle_close()
            else:
                self._receive(data)
        except socket.error, why:
            if why.args[0] in asyncore._DISCONNECTED:
                self.handle_close()
            else:
                self.handle_error()
            return
        self._receive(self.recv(self.recv_buffer_size))

    def handle_connect(self):
        self._connect()

    def handle_close(self):
        self._disconnect()
        self.close()

    def log_info(self, message, type='info'):
        return getattr(_logger, type)(message)

    def disconnect(self, *args):
        pass

    @property
    def address(self):
        return self.addr
