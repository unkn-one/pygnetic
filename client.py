from packets import *

class Host(object):
    """class allowing to send messages and packets

    peer - connection to send packet over
    channel - channel of connection

    examples:
        host = Host()
        # chat_msg packet is defined in packets module
        host.net_chat_msg('Tom', 'Test message')
        # alternative
        host.send(packets.chat_msg('Tom', 'Test message'))
    """
    peer = None
    channel = None

    def __getattr__(self, name):
        parts = name.split('_', 1)
        if len(parts) == 2 and parts[0] == 'net' and len(parts[1]) > 0:
            return lambda *args, **kwargs: self.send(parts[1], *args, **kwargs)
        else:
            raise AttributeError("'%s' object has no attribute '%s'" % (type(self).__name__, name))

    def send(self, packet, *args, **kwargs):
        """send packet

        Host.send(packet, *args, **kwargs): return int

        packet - object of class created by register or name of packet

        When packet is name, args and kwargs are used to initialize packet object.
        Returns packet id which can be used to retrieve response from Pygame event queue.
        """
        return PacketManager.send(self.peer, self.channel, packet, *args, **kwargs)