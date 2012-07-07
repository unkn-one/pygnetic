:mod:`pygame_network` Package
=============================

.. toctree::
   :maxdepth: 1
   
   connection
   event
   packet
   syncobject


Functions
---------

.. function:: register(name, field_names[, flags])
   
   Register new packet type and return class by calling 
   :meth:`packet.PacketManager.register` 
   
   :param name: name of packet class
   :param field_names: list of names of packet fields
   :param flags: 
      enet flags used when sending packet
      (default :const:`enet.PACKET_FLAG_RELIABLE`)
   :rtype: (named tuple) packet
   
   
.. class:: Client([connections_limit, channel_limit, in_bandwidth, out_bandwidth])

   Class representing network client

   Example::
   
      client = pygame_network.Client()
      connection = client.connect("localhost", 10000)
      while True:
         client.step()


.. class:: Server([address, port, connections_limit, channel_limit, in_bandwidth, out_bandwidth])

   Class representing network client

   Example::
   
      server = pygame_network.Server(port=10000)
      while True:
         client.step()


.. class:: Receiver()