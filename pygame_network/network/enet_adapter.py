import logging
import enet
from .. import connection, server, client

_logger = logging.getLogger(__name__)


class Connection(connection.Connection):
    def __init__(self, parent, peer, message_factory, *args, **kwargs):
        super(Connection, self).__init__(parent, message_factory, *args, **kwargs)
        self.peer = peer

    def __del__(self):
        self.peer.disconnect_now()

    def _send_data(self, data, channel=0, flags=enet.PACKET_FLAG_RELIABLE, **kwargs):
        self.peer.send(channel, enet.Packet(data, flags))

    def disconnect(self, when=0):
        """Request a disconnection.

        when - type of disconnection
               0  - disconnect with acknowledge
               1  - disconnect after sending all messages
               -1 - disconnect without acknowledge
        """
        if when == 0:
            self.peer.disconnect()
        elif when == 1:
            self.peer.disconnect_later()
        else:
            self.peer.disconnect_now()

    @property
    def connected(self):
        """Connection state."""
        return self.peer.state == enet.PEER_STATE_CONNECTED

    @property
    def address(self):
        """Connection address."""
        address = self.peer.address
        return address.host, address.port


class Server(server.Server):
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


class Client(client.Client):
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
