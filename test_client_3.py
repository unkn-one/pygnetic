import random
import logging
import pygame
from pygame.locals import KEYDOWN, QUIT, K_ESCAPE, K_SPACE, K_l
import pygnetic as net


def message_status(screen, position, messages):
    i = 0
    keys = messages.keys()
    keys.sort()
    screen.fill(0x000000, (position[0], position[1], 350, 15))
    for k in keys:
        msg1, msg2 = messages[k]
        if msg2 is None:
            color = 0xffff00
        elif msg2 == msg1.upper():
            color = 0x00ff00
        else:
            color = 0xff0000
        screen.fill(color, (position[0] + i * 20, position[1], 15, 15))
        i += 1


def connection_status(screen, position, status=None):
    if status is None:
            color = 0xff0000
    elif status:
        color = 0x00ff00
    else:
        color = 0xffff00
    screen.fill(color, (5 + position[0], position[1], 15, 15))


def main():
    # Pygame init
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Client test")
    font = pygame.font.Font(pygame.font.get_default_font(), 20)
    clock = pygame.time.Clock()
    screen.blit(font.render('Client test', True, (255, 255, 255)), (10, 10))
    screen.blit(font.render('Connection:', True, (255, 255, 255)), (10, 35))
    screen.blit(font.render('Packets:', True, (255, 255, 255)), (10, 60))
    screen.blit(font.render('SPACE - connect/disconnect  L - fps limiter on / off', True, (255, 255, 255)), (10, 570))
    connection_status(screen, (140, 38))
    pygame.display.flip()

    # Network init
    net.init(events=True, logging_lvl=logging.DEBUG)  # enable Pygame events
    echo = net.register('echo', ('msg', 'msg_id'))
    client = net.Client()
    connection = None

    # Variables
    run = True
    limit = True
    messages = {}
    m_id = 0

    while run:
        events = pygame.event.get()
        for e in events:
            if e.type == KEYDOWN:
                if e.key == K_SPACE:
                    if connection is not None:
                        if connection.connected:
                            connection.disconnect()
                            connection_status(screen, (140, 38), False)
                    else:
                        connection = client.connect("localhost", 1337)
                        connection_status(screen, (140, 38), False)
                if e.key == K_l:
                    limit = not limit

            # Handling network messages
            if e.type == net.event.NETWORK and e.connection == connection:
                if e.net_type == net.event.NET_CONNECTED:
                    connection_status(screen, (140, 38), True)
                elif e.net_type == net.event.NET_DISCONNECTED:
                    connection_status(screen, (140, 38), None)
                    connection = None
                    messages = {}
                    message_status(screen, (110, 62), messages)
                elif e.net_type == net.event.NET_RECEIVED:
                    if e.msg_type == echo:
                        msg = e.message.msg
                        messages[e.message.msg_id][1] = msg
                        message_status(screen, (110, 62), messages)
            if e.type == QUIT or e.type == KEYDOWN and e.key == K_ESCAPE:
                run = False
        if len(messages) < 10 and connection is not None and connection.connected:
            msg = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz', 10))

            # Sending messages
            m_id += 1
            connection.net_echo(msg, m_id)

            messages[m_id] = [msg, None]
            message_status(screen, (110, 62), messages)
        client.update()
        pygame.display.flip()
        if limit:
            clock.tick(4)


if __name__ == '__main__':
    main()
