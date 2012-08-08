import logging
import message
import syncobject
import network
import serialization
from handler import Handler
from network import Server, Client

_logger = logging.getLogger(__name__)
_network_module = None
_serialization_module = None
register = message.message_factory.register


def init(events=False, event_val=1, logging_lvl=logging.INFO,
         network_m=('enet',), serialization_m=('msgpack', 'json')):
    """Initialize network library.

    events - allow sending Pygame events (default False)
    event_val - set event ID as event_val + pygame.USEREVENT (default 1)
    logging_lvl - level of logging messages (default logging.INFO, None to skip
                  initializing logging module
    network_m - string or list of strings with names of network
              library adapters, first available will be used
    serialization_m - string or list of strings with names of serialization
                    library adapters, first available will be used

    Note: Because of the dynamic loading of network library adapter, Client,
        Server and State classes will only be available after initialization.
    """
    global _network_module, _serialization_module
    if logging_lvl is not None:
        logging.basicConfig(level=logging_lvl,
                            format='%(asctime)-8s %(levelname)-8s %(message)s',
                            datefmt='%H:%M:%S')
    network.select_adapter(network_m)
    if network._selected_adapter is not None:
        _logger.info("Using %s",
            network._selected_adapter.__name__.split('.')[-1])
    else:
        _logger.critical("Can't find any network module")
    serialization.select_adapter(serialization_m)
    if serialization._selected_adapter is not None:
        _logger.info("Using %s",
            serialization._selected_adapter.__name__.split('.')[-1])
    else:
        _logger.critical("Can't find any serialization module")
    if events:
        _logger.info("Enabling pygame events")
        import event
        event.init(event_val)
