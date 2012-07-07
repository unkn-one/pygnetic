import logging
from weakref import proxy
import enet
from packet import PacketManager
from connection import Connection, Receiver

_logger = logging.getLogger(__name__)


class Server(object):
    packet_manager = PacketManager
    receiver_cls = None

    def __init__(self, address, port, connections_limit=4, channel_limit=0, in_bandwidth=0, out_bandwidth=0):
        address = enet.Address(address, port)
        self.host = enet.Host(address, connections_limit, channel_limit, in_bandwidth, out_bandwidth)
        self.peers = {}
        self._peer_cnt = 0
        self.packet_manager._frozen = True

    def step(self, timeout=0):
        host = self.host
        event = host.service(timeout)
        while event is not None:
            if event.type == enet.EVENT_TYPE_CONNECT:
                if event.data == self.packet_manager.get_hash():
                    _logger.info('Connection with %s accepted', event.peer.address)
                    peer_id = self._peer_cnt = self._peer_cnt + 1
                    peer_id = str(peer_id)
                    event.peer.data = peer_id
                    connection = Connection(self, event.peer, self.packet_manager)
                    if issubclass(self.receiver_cls, Receiver):
                        receiver = self.receiver_cls()
                        receiver.server = proxy(self)
                        connection.add_receiver(receiver)
                    self.peers[peer_id] = connection
                    connection._connect()
                else:
                    _logger.warning('Connection with %s refused, PacketManager'\
                                    ' hash incorrect', event.peer.address)
                    event.peer.disconnect_now()
            elif event.type == enet.EVENT_TYPE_DISCONNECT:
                _logger.info('Disconnected from %s', event.peer.address)
                self.peers[event.peer.data]._disconnect()
                del self.peers[event.peer.data]
            elif event.type == enet.EVENT_TYPE_RECEIVE:
                _logger.info('Received data from %s', event.peer.address)
                self.peers[event.peer.data]._receive(event.packet.data, event.channelID)
            event = host.check_events()
