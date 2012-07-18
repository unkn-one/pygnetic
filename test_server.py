import logging
import pygame_network
from pygame_network import Handler, Server


class EchoHandler(Handler):
    def net_echo(self, channel, message_id, message):
        msg = message.msg.upper()
        self.connection.net_echo(msg)
        print 'message #%d @ch%d: %s' % (message_id, channel, message)


def main():
    logging.basicConfig(level=logging.DEBUG)

    pygame_network.register('echo', ('msg',))
    print 'starting server'
    server = Server(port=54301)
    server.handler_cls = EchoHandler
    print 'server started'
    run = True
    while run:
        server.step(1000)


if __name__ == '__main__':
    main()
