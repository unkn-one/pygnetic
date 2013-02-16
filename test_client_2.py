"""Echo client"""

import random
import logging
import pygnetic as net


class EchoHandler(net.Handler):
    def __init__(self):
        self.out_counter = 0
        self.in_counter = 0

    def net_echo(self, message, **kwargs):
        logging.info('Received message: %s', message)
        self.in_counter += 1

    def update(self):
        if self.out_counter < 10 and self.connection.connected:
            msg = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz', 10))
            logging.info('Sending: %s', msg)
            self.connection.net_echo(msg, self.out_counter)
            self.out_counter += 1


def main():
    net.init(logging_lvl=logging.DEBUG, n_adapter='enet')
    net.register('echo', ('msg', 'msg_id'))
    client = net.Client(n_adapter='socket')
    connection = client.connect("localhost", 1337)
    handler = EchoHandler()
    connection.add_handler(handler)
    try:
        while handler.in_counter < 10:
            client.update()
            handler.update()
    except KeyboardInterrupt:
        pass
    finally:
        connection.disconnect()
        client.update()

if __name__ == '__main__':
    main()
