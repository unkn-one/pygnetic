"""Echo server"""

import logging
import pygnetic as net


class EchoHandler(net.Handler):
    def net_echo(self, message, **kwargs):
        logging.info('Received message: %s', message)
        msg = message.msg.upper()
        logging.info('Sending: %s', msg)
        self.connection.net_echo(msg, message.msg_id)


def main():
    net.init(logging_lvl=logging.DEBUG, n_adapter='enet')
    net.register('echo', ('msg', 'msg_id'))
    #server = net.Server(port=1337, handler=EchoHandler)
    server = net.Server(port=1337, n_adapter='socket')
    server.handler = EchoHandler
    logging.info('Listening')
    try:
        while True:
            server.update(1000)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
