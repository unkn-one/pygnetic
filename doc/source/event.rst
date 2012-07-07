:mod:`event` Module
===================

.. module:: event
   :synopsis: Module defining Pygame events.


Connected event
   | ``event.type`` = :const:`NETWORK`
   | ``event.net_type`` = :const:`NET_CONNECTED`
   | ``event.connection`` -- :func:`proxy <weakref.proxy>` to connection

Disconnected event
   | ``event.type`` = :const:`NETWORK`
   | ``event.net_type`` = :const:`NET_DISCONNECTED`
   | ``event.connection`` -- :func:`proxy <weakref.proxy>` to connection

Received event
   | ``event.type`` = :const:`NETWORK`
   | ``event.net_type`` = :const:`NET_RECEIVED`
   | ``event.connection`` -- :func:`proxy <weakref.proxy>` to connection
   | ``event.channel`` -- channel of connection
   | ``event.packet`` -- received packet
   | ``event.p_id`` -- packet identifier
   | ``event.p_type`` -- packet type

Response event
   | ``event.type`` = :const:`NETWORK`
   | ``event.net_type`` = :const:`NET_RESPONSE`
   | ``event.connection`` -- :func:`proxy <weakref.proxy>` to connection
   | ``event.channel`` -- channel of connection
   | ``event.packet`` -- received packet
   | ``event.p_id`` -- packet identifier
   | ``event.p_type`` -- packet type

Example::

   for e in pygame.event.get():
       if e.type == NETWORK:
           if e.net_type == NET_CONNECTED:
               print 'connected'
           elif e.net_type == NET_DISCONNECTED:
               print 'disconnected'
           elif e.net_type == NET_RECEIVED:
               if e.p_type == packet.chat_msg:
                   print '%s: %s' % (e.packet.player, e.packet.msg)
               else:
                   print 'received:', e.packet
           elif e.net_type == NET_RESPONSE:
               print 'response @%d: %s' % (e.p_id, e.packet)