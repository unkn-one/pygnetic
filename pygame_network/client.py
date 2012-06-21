from weakref import WeakKeyDictionary
from functools import partial
from inspect import getmembers
from packet import PacketManager


class Host(object):
    """Class allowing to send messages and packets

    peer - connection to send packet over
    channel - channel of connection

    example:
        host = Host()
        # chat_msg packet is defined in packets module
        host.net_chat_msg('Tom', 'Test message')
        # alternative
        host.send(packets.chat_msg('Tom', 'Test message'))
    """
    peer = None  # connection to send packet over
    channel = None  # channel of connection

    def __getattr__(self, name):
        parts = name.split('_', 1)
        if len(parts) == 2 and parts[0] == 'net' and\
                parts[1] in PacketManager._packets:
            p = partial(self.send, parts[1])
            p.__doc__ = "Send %s packet to remote host\n\nHost.net_%s: return"\
            " int" % (parts[1], PacketManager._packets[parts[1]].__doc__)
            # add new method so __getattr__ is no longer needed
            setattr(self, name, p)
            return p
        else:
            raise AttributeError("'%s' object has no attribute '%s'" %
                                 (type(self).__name__, name))

    def send(self, packet, *args, **kwargs):
        """Send packet to remote host

        Host.send(packet, *args, **kwargs): return int

        packet - object of class created by register or name of packet

        When packet is name, args and kwargs are used to
        initialize packet object. Returns packet id which can be used to
        retrieve response from Pygame event queue.
        """
        return PacketManager.send(self.peer, self.channel,
                                  packet, *args, **kwargs)


class Receiver(object):
    def __init__(self, *args, **kwargs):
        super(Receiver, self).__init__(*args, **kwargs)
        ReceiverManager.register(self)


class ReceiverManager(object):
    _rcvr_objs = WeakKeyDictionary()

    @classmethod
    def register(cls, obj):
        # get names of supported packets by available methods
        cls._rcvr_objs[obj] = tuple(
            name[4:]
            for name, _ in getmembers(obj, callable)
            if name.startswith('net_')
        )

    @classmethod
    def notify_all(cls, packet):
        name = packet.__name__
        for obj, packets in cls._rcvr_objs.iteritems():
            if name in packets:
                getattr(obj, 'net_' + name)(packet)
