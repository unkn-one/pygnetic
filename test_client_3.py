import random
import logging
import pygame
from pygame.locals import *
import pygame_network
from pygame_network.event import *

logging.basicConfig(level=logging.DEBUG)


def packet_status(screen, position, packets):
    i = 0
    keys = packets.keys()
    keys.sort()
    screen.fill(0x000000, (position[0], position[1], 350, 15))
    for k in keys:
        msg1, msg2 = packets[k]
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
    echo = pygame_network.packet.PacketManager.register('echo', ('msg',))
    client = pygame_network.client.Client()
    connection = None

    # Variables
    run = True
    limit = True
    packets = {}

    while run:
        events = pygame.event.get()
        for e in events:
            if e.type == KEYDOWN:
                if e.key == K_SPACE:
                    if connection is not None:
                        if connection.state == pygame_network.connection.STATE_CONNECTED:
                            connection.disconnect_later()
                            connection_status(screen, (140, 38), False)
                    else:
                        connection = client.connect("localhost", 54301)
                        connection_status(screen, (140, 38), False)
                if e.key == K_l:
                    limit = not limit
            if e.type == NETWORK and e.connection == connection:
                if e.net_type == NET_CONNECTED:
                    connection_status(screen, (140, 38), True)
                elif e.net_type == NET_DISCONNECTED:
                    connection_status(screen, (140, 38), None)
                    connection = None
                    packets = {}
                    packet_status(screen, (110, 62), packets)
                elif e.net_type == NET_RECEIVED:
                    if e.p_type == echo:
                        msg = e.packet.msg
                        packets[e.p_id][1] = msg
                        packet_status(screen, (110, 62), packets)
            if e.type == QUIT or e.type == KEYDOWN and e.key == K_ESCAPE:
                run = False
        if len(packets) < 10 and connection is not None and connection.state == pygame_network.connection.STATE_CONNECTED:
            msg = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz', 10))
            p_id = connection.net_echo(msg)
            packets[p_id] = [msg, None]
            packet_status(screen, (110, 62), packets)
        client.step()
        pygame.display.flip()
        if limit:
            clock.tick(4)


if __name__ == '__main__':
    main()
