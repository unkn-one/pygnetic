#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from SimpleXMLRPCServer import SimpleXMLRPCServer

_logger = logging.getLogger(__name__)


class DiscoveryService(object):
    def __init__(self):
        self.servers = []

    def register(self, name, address, port):
        """register(name, address, port) => string

        Register new server
        """
        try:
            self.servers.append((str(name), str(address), int(port)))
        except Exception as e:
            return '%s: %s' % (e.__class__.__name__, e.message)

    def list(self):
        """list() => [<name, address, port>]

        List all available servers
        """
        return self.servers


def main(address, port):
    server = SimpleXMLRPCServer((address, port), allow_none=True)
    server.register_introspection_functions()
    server.register_instance(DiscoveryService())
    server.serve_forever()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Server discovery service.')
    parser.add_argument('-a', '--address', type=str, default='')
    parser.add_argument('-p', '--port', type=int, default=8000)
    args = parser.parse_args()
    print 'Server started (Use Control-C to exit)'
    main(args.address, args.port)
    print 'Exiting'
