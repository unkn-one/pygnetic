import random
import logging
import pygame
from pygame.locals import *
import pygame_network
from pygame_network.event import *

logging.basicConfig(level=logging.DEBUG)


def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Alchemy Madness")
    echo = pygame_network.packet.PacketManager.register('echo', ('msg',))
    print 'connecting'
    client = pygame_network.client.Client()
    connection = client.connect("localhost", 54301)
    print 'client started'
    connected = None
    counter = 10
    while True:
        events = pygame.event.get()
        for e in events:
            if e.type == NETWORK and e.connection == connection:
                if e.net_type == NET_CONNECTED:
                    connected = True
                    print 'connected'
                elif e.net_type == NET_DISCONNECTED:
                    print 'disconnected'
                    break
                elif e.net_type == NET_RECEIVED:
                    if e.p_type == echo:
                        msg = e.packet.msg
                        print 'packet #%d @ch%d: %s' % (e.p_id, e.channel, e.packet)
            if e.type == QUIT or e.type == KEYDOWN and e.key == K_ESCAPE:
                break
        if counter > 0 and connected == True:
            msg = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz', 10))
            print("%s: out: %r" % (connection.peer.address, msg))
            connection.net_echo(msg)
            counter -= 1
        client.step()


if __name__ == '__main__':
    main()
