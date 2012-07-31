:mod:`event` Module
===================

.. module:: event
   :synopsis: Module defining Pygame events.


.. data:: NETWORK

.. data:: NET_CONNECTED

.. data:: NET_DISCONNECTED

.. data:: NET_RECEIVED

.. note::
   
   If you plan to change value of :const:`NETWORK` with :func:`init`, then use:: 
      
      import pygame_network.event as event
      # rather than
      # from pygame_network.event import NETWORK # wrong
   
    

Event attributes
----------------

Connected event
   | ``type`` = :const:`event.NETWORK`
   | ``net_type`` = :const:`event.NET_CONNECTED`
   | ``connection`` -- connection

Disconnected event
   | ``type`` = :const:`event.NETWORK`
   | ``net_type`` = :const:`event.NET_DISCONNECTED`
   | ``connection`` -- connection

Received event
   | ``type`` = :const:`event.NETWORK`
   | ``net_type`` = :const:`event.NET_RECEIVED`
   | ``connection`` -- connection
   | ``channel`` -- channel of connection
   | ``message`` -- received message
   | ``msg_id`` -- message identifier
   | ``msg_type`` -- message type


Example
-------
::

   for e in pygame.event.get():
       if e.type == NETWORK:
           if e.net_type == NET_CONNECTED:
               print 'connected'
           elif e.net_type == NET_DISCONNECTED:
               print 'disconnected'
           elif e.net_type == NET_RECEIVED:
               if e.msg_type == message.chat_msg:
                   print '%s: %s' % (e.message.player, e.message.msg)
               else:
                   print 'received:', e.message
                   
   