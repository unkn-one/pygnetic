import random
import logging
import pygame_network as net


class EchoHandler(net.Handler):
    def __init__(self):
        self.out_counter = 0
        self.in_counter = 0

    def net_echo(self, message, channel):
        logging.info('Received message @ch%d: %s', channel, message)
        self.in_counter += 1

    def step(self):
        if self.out_counter < 10 and self.connection.connected:
            msg = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz', 10))
            logging.info('Sending: %s', msg)
            self.connection.net_echo(msg, self.out_counter)
            self.out_counter += 1
        if self.out_counter == 10 and self.in_counter == 10:
            self.connection.disconnect()


def main():
    net.init(logging_lvl=logging.DEBUG)
    net.register('echo', ('msg', 'msg_id'))
    client = net.Client()
    connection = client.connect("localhost", 54301)
    handler = EchoHandler()
    connection.add_handler(handler)
    while True:
        client.step()
        handler.step()


if __name__ == '__main__':
    main()
