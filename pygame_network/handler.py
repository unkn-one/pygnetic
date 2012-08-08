class Handler(object):
    """Base class for objects handling packets through
    net_packet_name(message, **kwargs) methods
    """
    def on_connect(self):
        pass

    def on_disconnect(self):
        pass

    def on_recive(self, message, **kwargs):
        pass
