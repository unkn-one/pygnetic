#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from .. import __init__ as net
import messages

_logger = logging.getLogger(__name__)


class Handler(net.Handler):
    def __init__(self):
        self.curr = 0
        self.list_step = 10
        self.servers = None

    def net_register(self, message, **kwargs):
        sid = self.server.id_cnt = self.server.id_cnt + 1
        self.server.servers[sid] = [message, 0]
        self.connection.net_register_ack(sid)
        self.connection.disconnect()

    def net_get_servers(self, message, **kwargs):
        self.list_step = int(message.list_step)
        self.servers = tuple(m for m, _ in self.server.servers.itervalues())
        self.connection.net_servers_list(self.servers[:self.list_step])
        self.curr = 1

    def net_next_servers(self, message, **kwargs):
        if self.servers is not None:
            s = self.curr * self.list_step
            e = s + self.list_step
            self.curr += 1
            t = self.servers[s:e]
            self.connection.net_servers_list(t)
            if len(t) < self.list_step:
                self.connection.disconnect()

    def net_ping(self, message, **kwargs):
        s = self.server.servers.get(message.sid)
        if s is not None:
            s[1] = 0
        else:
            self.connection.net_error(messages.Errors.TIMEOUT)
        self.connection.disconnect()


class DiscoveryServer(net.Server):
    handler = Handler
    message_factory = messages.message_factory
    servers = {}
    id_cnt = 0
    ping_timeout = 30

    def update(self, *args):
        super(DiscoveryServer, self).update(*args)
        self.servers = {k: [v[0], v[1] + 1]
                        for k, v in self.servers.iteritems()
                        if v[1] + 1 < self.ping_timeout}


def run(host, port):
    server = DiscoveryServer(host, port)
    _logger.info('Listening')
    try:
        while True:
            server.update(1000)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Server discovery service.')
    parser.add_argument('-a', '--address', type=str, default='')
    parser.add_argument('-p', '--port', type=int, default=5000)
    args = parser.parse_args()
    print 'Server started (Use Control-C to exit)'
    run(args.address, args.port)
    print 'Exiting'
