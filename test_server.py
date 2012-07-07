import logging
import pygame_network
from pygame_network import Receiver, Server


class EchoReceiver(Receiver):
    def net_echo(self, channel, packet_id, packet):
        msg = packet.msg.upper()
        self.connection.net_echo(msg)
        print 'packet #%d @ch%d: %s' % (packet_id, channel, packet)


def main():
    logging.basicConfig(level=logging.DEBUG)

    pygame_network.register('echo', ('msg',))
    print 'starting server'
    server = Server(port=54301)
    server.receiver_cls = EchoReceiver
    print 'server started'
    run = True
    while run:
        server.step(1000)


if __name__ == '__main__':
    main()
