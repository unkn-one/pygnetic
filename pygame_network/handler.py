class Handler(object):
    """Base class for objects handling packets through
    net_packet_name(channel, message_id, message) functions
    """
    def on_connect(self):
        pass

    def on_disconnect(self):
        pass

    def on_recive(self, channel, message_id, message):
        pass
