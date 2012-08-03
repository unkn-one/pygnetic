import logging
from importlib import import_module
import message
import syncobject
from handler import Handler
from network.base_adapter import State

_logger = logging.getLogger(__name__)
_network_module = None
_serialization_module = None
register = message.MessageFactory.register


class Client(object):
    def __new__(cls, *args, **kwargs):
        "Create instance of Client class depending on selected network adapter"
        return _network_module.Client(*args, **kwargs)


class Server(object):
    def __new__(cls, *args, **kwargs):
        "Create instance of Server class depending on selected network adapter"
        return _network_module.Server(*args, **kwargs)


def _find_adapter(a_type, names):
    """Find and return first found adapter

    a_type - adapter type
    names - string or list of strings with names of libraries
    """
    if isinstance(names, basestring):
        names = (names,)
    for name in names:
        a_name = name + '_adapter'
        try:
            _logger.debug("Trying to import %s.%s", a_type, a_name)
            return import_module('.'.join((__name__, a_type, a_name)))
        except ImportError as e:
            _logger.debug("%s: %s", e.__class__.__name__, e.message)
        finally:
            _logger.info("Using %s %s module", name, a_type)
    else:
        _logger.critical("Can't find any %s module", a_type)


def init(events=False, event_val=1, logging_lvl=logging.INFO,
         network=('enet',), serialization=('msgpack', 'json')):
    """Initialize network library.

    events - allow sending Pygame events (default False)
    event_val - set event ID as event_val + pygame.USEREVENT (default 1)
    logging_lvl - level of logging messages (default logging.INFO, None to skip
                  initializing logging module
    network - string or list of strings with names of network library adapters,
              first available will be used
    serialization - string or list of strings with names of serialization
                    library adapters, first available will be used

    Note: Because of the dynamic loading of network library adapter, Client,
        Server and State classes will only be available after initialization.
    """
    global _network_module, _serialization_module
    if logging_lvl is not None:
        logging.basicConfig(level=logging_lvl,
                            format='%(asctime)-8s %(levelname)-8s %(message)s',
                            datefmt='%H:%M:%S')
    _network_module = _find_adapter('network', network)
    _serialization_module = _find_adapter('serialization', serialization)
    message.s_lib = _serialization_module
    if events:
        _logger.info("Enabling pygame events")
        import event
        event.init(event_val)
