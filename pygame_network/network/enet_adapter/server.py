import logging
from weakref import proxy
import enet
from ...handler import Handler
from ...message import MessageFactory
from connection import Connection

_logger = logging.getLogger(__name__)


class Server(object):
    message_factory = MessageFactory
    handler_cls = None

    def __init__(self, address='', port=0, connections_limit=4, *args, **kwargs):
        address = enet.Address(address, port)
        self.host = enet.Host(address, connections_limit, *args, **kwargs)
        self.peers = {}
        self._peer_cnt = 0
        _logger.debug('Server created %s, connections limit: %d', address, connections_limit)
        self.message_factory._frozen = True
        _logger.debug('MessageFactory frozen')


    def step(self, timeout=0):
        host = self.host
        event = host.service(timeout)
        while event is not None:
            if event.type == enet.EVENT_TYPE_CONNECT:
                if event.data == self.message_factory.get_hash():
                    _logger.info('Connection with %s accepted', event.peer.address)
                    peer_id = self._peer_cnt = self._peer_cnt + 1
                    peer_id = str(peer_id)
                    event.peer.data = peer_id
                    connection = Connection(self, event.peer, self.message_factory)
                    if issubclass(self.handler_cls, Handler):
                        handler = self.handler_cls()
                        handler.server = proxy(self)
                        connection.add_handler(handler)
                    self.peers[peer_id] = connection
                    connection._connect()
                else:
                    _logger.warning('Connection with %s refused, MessageFactory'\
                                    ' hash incorrect', event.peer.address)
                    event.peer.disconnect_now()
            elif event.type == enet.EVENT_TYPE_DISCONNECT:
                self.peers[event.peer.data]._disconnect()
                del self.peers[event.peer.data]
            elif event.type == enet.EVENT_TYPE_RECEIVE:
                self.peers[event.peer.data]._receive(event.packet.data, event.channelID)
            event = host.check_events()

    def connections(self, exclude=None):
        if exclude is None:
            return self.peers.itervalues()
        else:
            return (c for c in self.peers.itervalues() if c not in exclude)

    def handlers(self, exclude=[]):
        return (c._handlers[0] for c in self.peers.itervalues() if c not in exclude)
