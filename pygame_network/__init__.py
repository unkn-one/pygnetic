import packet
import connection
import syncobject
from client import Client
from server import Server
from receiver import Receiver
try:
    import event
except ImportError:
    pass

register = packet.PacketManager.register
