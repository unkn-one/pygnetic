import random
import logging
import enet
import pygame_network

logging.basicConfig(level=logging.DEBUG)

MSG_NUMBER = 10
SHUTDOWN_MSG = b"SHUTDOWN"

pygame_network.packet.PacketManager.register('echo', ('msg',))

print 'connecting'
client = pygame_network.client.Client()
connection = client.connect("localhost", 54301)

counter = 0
print 'client started'
while connection.state != enet.PEER_STATE_DISCONNECTED:
    client.step()
    if counter < MSG_NUMBER and connection.state == enet.PEER_STATE_CONNECTED:
        msg = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz', 10))
        print("%s: out: %r" % (connection.peer.address, msg))
        connection.net_echo(msg)
        counter += 1
