__all__ = ('NETWORK',
           'NET_CONNECTED',
           'NET_DISCONNECTED',
           'NET_RECEIVED')

NETWORK = 30
NET_CONNECTED = 0
NET_DISCONNECTED = 1
NET_RECEIVED = 2


def connected(connection):
    pass


def disconnected(connection):
    pass


def received(connection, message, channel):
    pass


def init(event_val=1):
    global NETWORK, connected, disconnected, received
    import pygame
    from pygame.event import Event
    from pygame.locals import USEREVENT
    NETWORK = USEREVENT + event_val

    def _connected(connection):
        pygame.event.post(Event(NETWORK, {
            'net_type': NET_CONNECTED,
            #'connection': proxy(connection)
            'connection': connection
        }))
    connected = _connected

    def _disconnected(connection):
        pygame.event.post(Event(NETWORK, {
            'net_type': NET_DISCONNECTED,
            #'connection': proxy(connection)
            'connection': connection
        }))
    disconnected = _disconnected

    def _received(connection, message, channel=0):
        pygame.event.post(Event(NETWORK, {
            'net_type': NET_RECEIVED,
            #'connection': proxy(connection),
            'connection': connection,
            'channel': channel,
            'message': message,
            'msg_type': message.__class__
        }))
    received = _received
