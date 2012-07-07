import logging
import pygame_network
from pygame_network.server import Server
from pygame_network.connection import Receiver


class EchoReceiver(pygame_network.connection.Receiver):
    def net_echo(self, channel, packet_id, packet):
        msg = packet.msg.upper()
        self.connection.net_echo(msg)
        print 'packet #%d @ch%d: %s' % (packet_id, channel, packet)


def main():
    logging.basicConfig(level=logging.DEBUG)

    pygame_network.packet.PacketManager.register('echo', ('msg',))
    print 'starting server'
    server = Server("localhost", 54301)
    server.receiver_cls = EchoReceiver
    print 'server started'
    run = True
    while run:
        server.step(1000)


if __name__ == '__main__':
    main()
