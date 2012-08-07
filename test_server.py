import logging
import pygame_network as net


class EchoHandler(net.Handler):
    def net_echo(self, message, channel):
        logging.info('Received message @ch%d: %s', channel, message)
        msg = message.msg.upper()
        self.connection.net_echo(msg, message.msg_id)


class Server(net.Server):
    handler = EchoHandler


def main():
    net.init(logging_lvl=logging.DEBUG)
    net.register('echo', ('msg', 'msg_id'))
    server = Server(port=54301)
    logging.info('Listening')
    run = True
    while run:
        server.step(1000)


if __name__ == '__main__':
    main()
