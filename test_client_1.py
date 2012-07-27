import random
import logging
import pygame_network as net


def main():
    net.init(logging_lvl=logging.DEBUG)
    net.register('echo', ('msg',))
    client = net.Client()
    connection = client.connect("localhost", 54301)
    counter = 0
    while connection.state != net.State.DISCONNECTED:
        client.step()
        if counter < 10 and connection.state == net.State.CONNECTED:
            msg = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz', 10))
            logging.info('Sending: %s', msg)
            connection.net_echo(msg)
            counter += 1


if __name__ == '__main__':
    main()
