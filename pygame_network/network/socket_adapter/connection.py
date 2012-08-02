import logging
from collections import deque
from asyncore import dispatcher
from ...message import MessageFactory

_logger = logging.getLogger(__name__)


class Connection(dispatcher):
    __send = dispatcher.send

    def __init__(self, parent, socket, message_factory=MessageFactory):
        super(Connection, self).__init__(parent, message_factory)
        self._buffer = deque()

    def _send_data(self, data, **kwargs):
        pass

    def disconnect(self, *args):
        """Request a disconnection."""
        pass

    @property
    def state(self):
        """Connection state."""
        return None

    @property
    def address(self):
        """Connection address."""
        return None, None

    def handle_read(self):
        self.log_info('unhandled read event', 'warning')

    def handle_write(self):
        self.log_info('unhandled write event', 'warning')

    def handle_connect(self):
        self.log_info('unhandled connect event', 'warning')

    def handle_accept(self):
        self.log_info('unhandled accept event', 'warning')

    def handle_close(self):
        self.log_info('unhandled close event', 'warning')
        self.close()

    def log_info(self, message, type='info'):
        return getattr(_logger, type)(message)
