from weakref import WeakKeyDictionary
from packets import *

REMOTEOBJECT_MODE_AUTO = 0
REMOTEOBJECT_MODE_MANUAL = 1

class Host(object):
    peer = None
    channel = None

    def __getattr__(self, name):
        parts = name.split('_', 1)
        if len(parts) == 2 and parts[0] == 'net' and len(parts[1]) > 0:
            return lambda *args, **kwargs: self.send(parts[1], *args, **kwargs)
        else:
            raise AttributeError("'%s' object has no attribute '%s'" % (type(self).__name__, name))

    def send(self, packet, *args, **kwargs):
        return PacketManager.send(self.peer, self.channel, packet, *args, **kwargs)

class RemoteObject(object):
    sync_var = ()
    sync_mode = REMOTEOBJECT_MODE_AUTO
    sync_flags = 0

    def __init__(self, *args, **kwargs):
        super(RemoteObject, self).__init__(*args, **kwargs)
        RemoteObjectManager.register(self)

    def __setattr__(self, name, value):
        object.__setattr__(self, name, value)
        if name in self.sync_var:
            RemoteObjectManager.changed(self, name)

    def on_change(self):
        """callback when variable(s) was changed by remote host, should be overridden
        """
        pass

    def send_changes(self):
        pass

class RemoteObjectManager(object):
    known_types = {}
    remote_objs = WeakKeyDictionary()
    type_id_cnt = 0
    obj_id_cnt = 0

    @classmethod
    def register(cls, obj):
        try:
            type_id = cls.known_types[obj.__class__]
        except KeyError:
            type_id = cls.type_id_cnt + 1
            cls.known_types[obj.__class__] = type_id
            cls.type_id_cnt = type_id
        obj_id = cls.obj_id_cnt + 1
        cls.remote_objs[obj] = (type_id, obj_id, [False]*len(obj.sync_var))
        cls.obj_id_cnt = obj_id

    def changed(cls, obj, var_name):
        cls.remote_objs[obj] # TODO: finish this

# TODO: pushing update packets from RemoteObject
# TODO: mapping obj type and variables to ints

class Player(RemoteObject):
    synch = ('x', 'y')
    def __init__(self):
        super(Player, self).__init__()
        self.name = 'test'
        self.x = self.y = 0