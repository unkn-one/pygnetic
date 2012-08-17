#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
from .. import __init__ as net
import messages

_logger = logging.getLogger(__name__)


class Handler(net.Handler):
    def net_register(self, message, channel):
        self.server.append()

    def net_get_servers(self, message, channel):
        pass


class Server(net.Server):
    handler = Handler
    message_factory = messages.message_factory
    servers = list()


def run(address, port):
    server = Server(address, port)
    _logger.info('Listening')
    try:
        while True:
            server.step(1000)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Server discovery service.')
    parser.add_argument('-a', '--address', type=str, default='')
    parser.add_argument('-p', '--port', type=int, default=8000)
    args = parser.parse_args()
    print 'Server started (Use Control-C to exit)'
    run(args.address, args.port)
    print 'Exiting'
