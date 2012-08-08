import logging
import enet
from ... import message
from .. import base_adapter
from connection import Connection

_logger = logging.getLogger(__name__)


class Server(base_adapter.Server):
    connection = Connection

    def __init__(self, address='', port=0, con_limit=4, *args, **kwargs):
        super(Server, self).__init__(address, port, con_limit, *args, **kwargs)
        address = enet.Address(address, port)
        self.host = enet.Host(address, con_limit, *args, **kwargs)
        self._peer_cnt = 0

    def update(self, timeout=0):
        host = self.host
        event = host.service(timeout)
        while event is not None:
            if event.type == enet.EVENT_TYPE_CONNECT:
                peer_id = str(self._peer_cnt + 1)
                if self._accept(event.data, event.peer, peer_id, event.peer.address):
                    event.peer.data = peer_id
                    self._peer_cnt += 1
                else:
                    event.peer.disconnect_now()
            elif event.type == enet.EVENT_TYPE_DISCONNECT:
                self._disconnect(event.peer.data)
            elif event.type == enet.EVENT_TYPE_RECEIVE:
                self._receive(event.peer.data, event.packet.data, channel=event.channelID)
            event = host.check_events()
