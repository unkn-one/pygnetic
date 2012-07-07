class Receiver(object):
    """Base class for objects receiving packets through net_packet_name
    functions
    """
    def on_connect(self):
        pass

    def on_disconnect(self):
        pass

    def on_recive(self, channel, packet_id, packet):
        pass
