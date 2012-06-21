:mod:`client` Module
====================

.. module:: client
   :synopsis: Classes useful for network clients.


.. class:: Host([connection])

   Class allowing to send messages and packets.
   
   Sending is possible in two ways:
   
   * using :samp:`net_{packet_name}` methods, where :samp:`{packet_name}` 
     is name of packet registered in :class:`~.packet.PacketManager`  
   * using ``send`` method with packet as argument
   
   Example::
   
       host = Host()
       # chat_msg packet is defined in packet module
       host.net_chat_msg('Tom', 'Test message')
       # alternative
       host.send(packet.chat_msg('Tom', 'Test message'))
   
   
   .. attribute:: Host.channel
   
      Channel of enet connection
      
   
   .. attribute:: Host.peer
   
      Enet connection to send packet over
      
   
   .. method:: Host.send(packet[ , \*args, \*\*kwargs])
   
      Send packet to remote host
      
      :param packet: 
         object of class created by :meth:`packet.PacketManager.register` or 
         name of packet (args and kwargs are used to initialize packet object)
      :rtype: 
         (int) packet id which can be used to retrieve response from 
         Pygame event queue
      
