import logging
from collections import deque
from asyncore import dispatcher
from .. import base_adapter
from ...message import MessageFactory

_logger = logging.getLogger(__name__)


class Connection(base_adapter.Connection, dispatcher):
    __send = dispatcher.send
    rcvr_buffer_size = 2048

    def __init__(self, parent, socket, message_factory=MessageFactory):
        super(Connection, self).__init__(parent, message_factory)
        self._queue = deque()
        self.state = base_adapter.State.DISCONNECTED

    def _send_data(self, data, **kwargs):
        self._message_queue.append(data)

    def disconnect(self, *args):
        """Request a disconnection."""
        pass

    @property
    def address(self):
        """Connection address."""
        return None, None

    def handle_read(self):
        self._receive(self.recv(self.rcvr_buffer_size))

    def handle_write(self):
        #queue, self._queue = self._queue, deque()
        for data in self._queue:
            self.__send(data)
        self._queue = deque()

    def handle_connect(self):
        self.state = base_adapter.State.CONNECTED
        self._connect()

    def handle_close(self):
        self.log_info('unhandled close event', 'warning')
        self.close()

    def log_info(self, message, type='info'):
        return getattr(_logger, type)(message)
