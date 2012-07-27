import random
import logging
import pygame_network as net


class EchoHandler(net.Handler):
    def __init__(self):
        self.connected = None
        self.counter = 10

    def net_echo(self, channel, message_id, message):
        logging.info('Received message #%d @ch%d: %s', message_id, channel, message)

    def on_connect(self):
        self.connected = True

    def on_disconnect(self):
        self.connected = False

    def step(self):
        if self.counter > 0 and self.connected == True:
            msg = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz', 10))
            logging.info('Sending: %s', msg)
            self.connection.net_echo(msg)
            self.counter -= 1


def main():
    net.init(logging_lvl=logging.DEBUG)
    net.register('echo', ('msg',))
    client = net.Client()
    connection = client.connect("localhost", 54301)
    handler = EchoHandler()
    connection.add_handler(handler)
    while handler.connected != False:
        client.step()
        handler.step()


if __name__ == '__main__':
    main()
