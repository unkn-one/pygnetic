from weakref import proxy
import pygame
from pygame.event import Event
from pygame.locals import USEREVENT

NETWORK = USEREVENT + 1
NET_CONNECTED = 0
NET_DISCONNECTED = 1
NET_RECEIVED = 2
NET_RESPONSE = 3


def _connected_event(connection):
    pygame.event.post(Event(NETWORK, {
        'net_type': NET_CONNECTED,
        'connection': proxy(connection)
    }))


def _disconnected_event(connection):
    pygame.event.post(Event(NETWORK, {
        'net_type': NET_DISCONNECTED,
        'connection': proxy(connection)
    }))


def _received_event(connection, channel, packet, packet_id):
    pygame.event.post(Event(NETWORK, {
        'net_type': NET_RECEIVED,
        'connection': proxy(connection),
        'channel': channel,
        'packet': packet,
        'p_id': packet_id,
        'p_type': packet.__class__
    }))


def _response_event(connection, channel, packet, packet_id):
    pygame.event.post(Event(NETWORK, {
        'net_type': NET_RESPONSE,
        'connection': proxy(connection),
        'channel': channel,
        'packet': packet,
        'p_id': packet_id,
        'p_type': packet.__class__
    }))
