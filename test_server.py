import enet
import pygame_network

PM = pygame_network.packet.PacketManager
PM.register('echo', ('msg',))
PM._frozen = True

host = enet.Host(enet.Address(b"localhost", 54301), 10, 0, 0, 0)

connect_count = 0
run = True
shutdown_recv = False
while run:
    # Wait 1 second for an event
    event = host.service(1000)
    if event.type == enet.EVENT_TYPE_CONNECT:
        correct = event.data == PM.get_hash()
        print("%s: CONNECT, PacketManager hash %scorrect" % (
            event.peer.address, '' if correct else 'in'))
        if not correct:
            event.peer.disconnect()
    elif event.type == enet.EVENT_TYPE_DISCONNECT:
        print("%s: DISCONNECT" % event.peer.address)
    elif event.type == enet.EVENT_TYPE_RECEIVE:
        pid, packet = PM.unpack(event.packet.data)
        msg = packet.msg.upper()
        print("%s: IN:  %r" % (event.peer.address, packet.msg))
        if event.peer.send(0, enet.Packet(PM.pack(pid, packet.__class__(msg)))) < 0:
            print("%s: Error sending echo packet!" % event.peer.address)
        else:
            print("%s: OUT: %r" % (event.peer.address, msg))
