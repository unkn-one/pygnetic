import random
import logging
import pygame_network
from pygame_network.connection import STATE_CONNECTED, STATE_DISCONNECTED


def main():
    logging.basicConfig(level=logging.DEBUG)

    pygame_network.register('echo', ('msg',))
    print 'connecting'
    client = pygame_network.Client()
    connection = client.connect("localhost", 54301)
    counter = 0
    print 'client started'
    while connection.state != STATE_DISCONNECTED:
        client.step()
        if counter < 10 and connection.state == STATE_CONNECTED:
            msg = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz', 10))
            print("%s: out: %r" % (connection.address, msg))
            connection.net_echo(msg)
            counter += 1


if __name__ == '__main__':
    main()
