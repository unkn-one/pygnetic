import logging
from importlib import import_module
import message
import syncobject
from handler import Handler

register = message.MessageFactory.register


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
    global Client, Server, State
    _logger = logging.getLogger(__name__)
    if logging_lvl is not None:
        logging.basicConfig(level=logging_lvl,
                            format='%(asctime)s:%(levelname)s:%(message)s',
                            datefmt='%H:%M:%S')
    if isinstance(network, basestring):
        network = (network,)
    if isinstance(serialization, basestring):
        serialization = (serialization,)
    for name in network:
        try:
            _logger.debug("Trying to import network.%s_adapter", name)
            nmod = import_module('pygame_network.network.%s_adapter' % name)
            break
        except ImportError as e:
            _logger.debug("%s: %s", e.__class__.__name__, e.message)
    else:
        _logger.critical("Can't find any network module")
        return
    Client = nmod.Client
    Server = nmod.Server
    State = nmod.State
    _logger.info("Using %s network module", name)
    for name in serialization:
        try:
            _logger.debug("Trying to import serialization.%s_adapter", name)
            smod = import_module('pygame_network.serialization.%s_adapter' % name)
            break
        except ImportError:
            _logger.debug("%s: %s", e.__class__.__name__, e.message)
    else:
        _logger.critical("Can't find any serialization module")
        return
    message.s_lib = smod
    _logger.info("Using %s serialization module", name)
    if events:
        _logger.info("Enabling pygame events")
        import event
        event.init(event_val)
