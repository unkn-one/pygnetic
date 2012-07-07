__all__ = ('NETWORK',
           'NET_CONNECTED',
           'NET_DISCONNECTED',
           'NET_RECEIVED',
           'NET_RESPONSE')

from weakref import proxy
import pygame
from pygame.event import Event
from pygame.locals import USEREVENT
import connection

NETWORK = USEREVENT + 1
NET_CONNECTED = 0
NET_DISCONNECTED = 1
NET_RECEIVED = 2
NET_RESPONSE = 3  # TODO: response !!


def init(event_val=1):
    global NETWORK
    NETWORK = USEREVENT + event_val
    connection._connected_event = _connected_event
    connection._disconnected_event = _disconnected_event
    connection._received_event = _received_event
    connection._response_event = _response_event


def _connected_event(connection):
    pygame.event.post(Event(NETWORK, {
        'net_type': NET_CONNECTED,
        #'connection': proxy(connection)
        'connection': connection
    }))


def _disconnected_event(connection):
    pygame.event.post(Event(NETWORK, {
        'net_type': NET_DISCONNECTED,
        #'connection': proxy(connection)
        'connection': connection
    }))


def _received_event(connection, channel, packet, packet_id):
    pygame.event.post(Event(NETWORK, {
        'net_type': NET_RECEIVED,
        #'connection': proxy(connection),
        'connection': connection,
        'channel': channel,
        'packet': packet,
        'p_id': packet_id,
        'p_type': packet.__class__
    }))


def _response_event(connection, channel, packet, packet_id):
    pygame.event.post(Event(NETWORK, {
        'net_type': NET_RESPONSE,
        #'connection': proxy(connection),
        'connection': connection,
        'channel': channel,
        'packet': packet,
        'p_id': packet_id,
        'p_type': packet.__class__
    }))
