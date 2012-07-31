:mod:`pygame_network` Package
=============================

.. toctree::
   :maxdepth: 1
   
   connection
   event
   message
   syncobject


Functions
---------

.. function:: init([events, event_val, logging_lvl, network, serialization])

   Initialize network library.
   
   :param events: allow sending Pygame events (default False)
   :param event_val:
      set :const:`event.NETWORK` as :const:`pygame.USEREVENT` + :attr:`event_val` (default 1)
   :param logging_lvl:
      level of logging messages (default :const:`logging.INFO`
      (see: :ref:`logging-basic-tutorial`), None to skip initializing
      logging module)
   :param network:
      name(s) of network library adapters, first available will be used
      (default ['enet'])
   :type network: string or list of strings
   :param serialization:
      name(s) of serialization library adapters, first available will be used
      (default ['msgpack', 'json'])
   :type serialization: string or list of strings
   
   .. note::
   
      Because of the dynamic loading of network library adapter, 
      :class:`Client`, :class:`Server` and :class:`State` classes will only be
      available after initialization.


.. function:: register(name, field_names[, flags])
   
   Register new packet type and return class by calling 
   :meth:`message.MessageFactory.register`
   
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