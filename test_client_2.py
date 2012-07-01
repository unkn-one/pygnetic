import random
import logging
import pygame_network

logging.basicConfig(level=logging.DEBUG)


class EchoReceiver(pygame_network.client.Receiver):
    def __init__(self, connection):
        super(EchoReceiver, self).__init__()
        self.connection = connection
        self.connected = None
        self.counter = 10

    def net_echo(self, channel, packet_id, packet):
        print 'packet #%d @ch%d: %s' % (packet_id, channel, packet)

    def on_connect(self):
        self.connected = True

    def on_disconnect(self):
        self.connected = False

    def step(self):
        if self.counter > 0 and self.connected == True:
            msg = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz', 10))
            print("%s: out: %r" % (self.connection.peer.address, msg))
            self.connection.net_echo(msg)
            self.counter -= 1


def main():
    pygame_network.packet.PacketManager.register('echo', ('msg',))
    print 'connecting'
    client = pygame_network.client.Client()
    connection = client.connect("localhost", 54301)
    receiver = EchoReceiver(connection)
    print 'client started'
    while receiver.connected != False:
        client.step()
        receiver.step()


if __name__ == '__main__':
    main()
