import enet
from .. import base_adapter


class Connection(base_adapter.Connection):
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
