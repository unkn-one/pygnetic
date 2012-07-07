:mod:`connection` Module
========================

.. module:: connection
   :synopsis: Module containing class representing connections.


.. class:: Connection(parent, peer[, packet_manager])

   Class allowing to send packets

   .. note::
      It's created by :class:`~.client.Client` or :class:`~.server.Server`
      and shouldn't be created manually.

   Sending is possible in two ways:

   * using :meth:`net_packet_name` methods, where ``packet_name``
     is name of packet registered in :class:`~.packet.PacketManager`
   * using :meth:`send` method with packet as argument
   
   Example::
   
       # assuming chat_msg packet is already defined
       connection.net_chat_msg('Tom', 'Test message')
       # alternative
       connection.send(chat_msg, 'Tom', 'Test message')
       # or
       connection.send('chat_msg', 'Tom', 'Test message')


   .. attribute:: address

      Connection address


   .. attribute:: parent

      Proxy to Client / Server instance


   .. attribute:: peer

      Enet peer instance


   .. attribute:: state

      Connection state


   .. method:: add_receiver(receiver)

      Add :class:`Receiver` to handle packets.

      :param receiver:
         instance of :class:`Receiver` subclass


   .. method:: disconnect()

      Request a disconnection.


   .. method:: disconnect_later()

      Request a disconnection from a peer, but only after all queued
      outgoing packets are sent.


   .. method:: disconnect_now()

      Force an immediate disconnection.
      
   .. method:: net_packet_name(\*args, \*\*kwargs)

      Send ``packet_name`` packet to remote host.
      
      args and kwargs are used to initialize packet object
      
      :return:
         packet id which can be used to retrieve response from Pygame
         event queue (int)


   .. method:: send(packet[ , \*args, \*\*kwargs])

      Send packet to remote host.

      :param packet:
         object of class created by :meth:`~.packet.PacketManager.register` or
         name of packet (args and kwargs are used to initialize packet object)
      :return int:
         packet id which can be used to retrieve response from Pygame
         event queue
