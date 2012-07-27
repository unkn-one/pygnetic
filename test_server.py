import logging
import pygame_network as net


class EchoHandler(net.Handler):
    def net_echo(self, channel, message_id, message):
        msg = message.msg.upper()
        self.connection.net_echo(msg)
        logging.info('message #%d @ch%d: %s', message_id, channel, message)


def main():
    net.init(logging_lvl=logging.DEBUG)
    net.register('echo', ('msg',))
    server = net.Server(port=54301)
    server.handler_cls = EchoHandler
    logging.info('Listening')
    run = True
    while run:
        server.step(1000)


if __name__ == '__main__':
    main()
