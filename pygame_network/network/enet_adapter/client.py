import logging
import enet
from .. import base_adapter
from connection import Connection

_logger = logging.getLogger(__name__)


class Client(base_adapter.Client):
    connection = Connection

    def __init__(self, conn_limit=1, *args, **kwargs):
        super(Client, self).__init__(*args, **kwargs)
        self.host = enet.Host(None, conn_limit)
        self._peer_cnt = 0

    def _create_connection(self, address, port, mf_hash, channels=1, **kwargs):
        address = enet.Address(address, port)
        peer_id = self._peer_cnt = self._peer_cnt + 1
        peer_id = str(peer_id)
        peer = self.host.connect(address, channels, mf_hash)
        peer.data = peer_id
        return peer, peer_id

    def update(self, timeout=0):
        if len(self.conn_map) == 0:
            return
        host = self.host
        event = host.service(timeout)
        while event is not None:
            if event.type == enet.EVENT_TYPE_CONNECT:
                self._connect(event.peer.data)
            elif event.type == enet.EVENT_TYPE_DISCONNECT:
                self._disconnect(event.peer.data)
            elif event.type == enet.EVENT_TYPE_RECEIVE:
                self._receive(event.peer.data, event.packet.data, channel=event.channelID)
            event = host.check_events()
