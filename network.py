from threading import Thread, Event
from collections import namedtuple
import msgpack

Message = namedtuple('Message', ['action', 'id', 'args', 'kwargs'])

class Host(object):
    packer = msgpack.Packer()
    msg_id = 0
    def __getattr__(self, name):
        parts = name.split('_')
        if len(parts) == 2 and parts[0] == 'net' and len(parts[1]) > 0:
            return lambda *args, **kwargs: self.send(parts[1], *args, **kwargs)
        else:
            raise AttributeError("'%s' object has no attribute '%s'" % (type(self).__name__, name))

    def send(self, action, *args, **kwargs):
        msg_id = self.msg_id
        msg = Message(action, msg_id, args, kwargs)
        print 'msg:', msg, 'len:', len(self.packer.pack(msg))
        self.msg_id = msg_id + 1
        return msg_id

class RemoteObject(object):
    synch = ()

    def __init__(self, *args, **kwargs):
        super(RemoteObject, self).__init__(*args, **kwargs)
        self._changed = False

    def _synch_var(self):
        return ((k,v) for k,v in self.__dict__.iteritems() if k in self.synch)

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        object.__setattr__(self, '_changed', self._changed or name in self.synch)

class Player(RemoteObject):
    synch = ('x', 'y')
    def __init__(self):
        super(Player, self).__init__()
        self.name = 'test'
        self.x = self.y = 0