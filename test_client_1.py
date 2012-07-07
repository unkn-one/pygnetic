import random
import logging
import pygame_network


def main():
    logging.basicConfig(level=logging.DEBUG)

    pygame_network.packet.PacketManager.register('echo', ('msg',))
    print 'connecting'
    client = pygame_network.client.Client()
    connection = client.connect("localhost", 54301)
    counter = 0
    print 'client started'
    while connection.state != pygame_network.connection.STATE_DISCONNECTED:
        client.step()
        if counter < 10 and connection.state == pygame_network.connection.STATE_CONNECTED:
            msg = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz', 10))
            print("%s: out: %r" % (connection.address, msg))
            connection.net_echo(msg)
            counter += 1


if __name__ == '__main__':
    main()
