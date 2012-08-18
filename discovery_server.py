import logging
import pygnetic
from pygnetic.discovery import DiscoveryServer

_logger = logging.getLogger(__name__)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Server discovery service.')
    parser.add_argument('-i', '--host', type=str, default='',
                        help='Server host IP')
    parser.add_argument('-p', '--port', type=int, default=5000,
                        help='Server port')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Enable debugging')
    args = parser.parse_args()
    if args.debug:
        pygnetic.init(logging_lvl=logging.DEBUG)
    else:
        pygnetic.init()
    _logger.info('Server started (Use Control-C to exit)')
    try:
        DiscoveryServer(args.host, args.port).serve_forever()
    except KeyboardInterrupt:
        pass
    _logger.info('Exiting')
