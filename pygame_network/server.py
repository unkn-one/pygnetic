import logging
import enet
from packet import PacketManager
from connection import Connection

_logger = logging.getLogger(__name__)


class Server(object):
    packet_manager = PacketManager
    receiver = None

    def __init__(self, address, port, connections_limit=4, channel_limit=0, in_bandwidth=0, out_bandwidth=0):
        address = enet.Address(address, port)
        self.host = enet.Host(address, connections_limit, channel_limit, in_bandwidth, out_bandwidth)
        self._peers = {}
        self._peer_cnt = 0
        self.packet_manager._frozen = True

    def step(self, timeout=0):
        if len(self._peers) == 0:
            return
        host = self.host
        event = host.service(timeout)
        while event is not None:
            if event.type == enet.EVENT_TYPE_CONNECT:
                if event.data == self.packet_manager.get_hash():
                    peer_id = self._peer_cnt = self._peer_cnt + 1
                    peer_id = str(peer_id)
                    event.peer.data = peer_id
                    connection = Connection(self, event.peer, self.packet_manager)
                    self._peers[peer_id] = connection
                    # TODO: add receiver
                    connection._connect()
                    _logger.info('Connection with %s accepted', event.peer.address)
                else:
                    event.peer.data = 'N'
                    event.peer.disconnect()
                    _logger.warning('Connection with %s refused, incompatible packets set', event.peer.address)
            elif event.type == enet.EVENT_TYPE_DISCONNECT:
                if event.peer.data != 'N':
                    self._peers[event.peer.data]._disconnect()
                    del self._peers[event.peer.data]
                _logger.info('Disconnected from %s', event.peer.address)
            elif event.type == enet.EVENT_TYPE_RECEIVE:
                self._peers[event.peer.data]._receive(event.packet.data, event.channelID)
                _logger.info('Received data from %s', event.peer.address)
            event = host.check_events()
