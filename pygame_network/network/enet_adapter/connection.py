import enet
from .. import base_adapter

_state_mapping = {
    enet.PEER_STATE_ACKNOWLEDGING_CONNECT: base_adapter.State.CONNECTING,
    enet.PEER_STATE_ACKNOWLEDGING_DISCONNECT: base_adapter.State.DISCONNECTING,
    enet.PEER_STATE_CONNECTED: base_adapter.State.CONNECTED,
    enet.PEER_STATE_CONNECTING: base_adapter.State.CONNECTING,
    enet.PEER_STATE_CONNECTION_PENDING: base_adapter.State.CONNECTING,
    enet.PEER_STATE_CONNECTION_SUCCEEDED: base_adapter.State.CONNECTING,
    enet.PEER_STATE_DISCONNECTED: base_adapter.State.DISCONNECTED,
    enet.PEER_STATE_DISCONNECTING: base_adapter.State.DISCONNECTING,
    enet.PEER_STATE_DISCONNECT_LATER: base_adapter.State.DISCONNECTING,
    enet.PEER_STATE_ZOMBIE: base_adapter.State.DISCONNECTING
}


class Connection(base_adapter.Connection):
    """Class allowing to send messages

    It's created by by Client or Server, shouldn't be created manually.

    Sending is possible in two ways:
    * using net_<message_name> methods, where <message_name>
      is name of message registered in MessageFactory
    * using send method with message as argument

    Attributes:
        parent - proxy to Client / Server instance
        peer - Enet peer instance
    """

    def __init__(self, parent, peer, message_factory=None):
        super(Connection, self).__init__(parent, message_factory)
        self.peer = peer

    def __del__(self):
        self.peer.disconnect_now()

    def _send_data(self, data, channel=0, flags=enet.PACKET_FLAG_RELIABLE):
        self.peer.send(channel, enet.Packet(data, flags))

    def disconnect(self, when=0):
        """Request a disconnection.

        when - type of disconnection
               0  - disconnect with acknowledge
               -1 - disconnect after sending all messages
               1  - disconnect without acknowledge
        """
        if when == 0:
            self.peer.disconnect()
        elif when == -1:
            self.peer.disconnect_later()
        else:
            self.peer.disconnect_now()

    @property
    def state(self):
        """Connection state."""
        return _state_mapping[self.peer.state]

    @property
    def address(self):
        """Connection address."""
        address = self.peer.address
        return address.host, address.port
