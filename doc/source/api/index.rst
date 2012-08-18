:mod:`pygnetic` Package
=======================

.. automodule:: pygnetic

   .. autofunction:: init([events[, event_val[, logging_lvl[, n_module[, s_module]]]]])
   
   .. autofunction:: register(name[, field_names[, **kwargs]])
   
      .. note:: It uses :data:`.message.message_factory`
      
   .. autoclass:: Client
   
   .. autoclass:: Server
   
   .. class :: Handler
   
      :class:`handler.Handler` binding.
   
   
:mod:`client` Module
--------------------

.. automodule:: pygnetic.client
    
   .. autoclass:: Client([conn_limit, [*args, **kwargs]])
    
      Example::
      
         client = pygnetic.client.Client()
         connection = client.connect("localhost", 10000)
         while True:
            client.update()
            
      .. data:: message_factory
         
         Default :class:`~.message.MessageFactory` object used for new
         connections. (default: :data:`.message.message_factory`)
      
      .. automethod:: connect(host, port[, message_factory[, **kwargs]])
      
      .. automethod:: update(self[, timeout])


:mod:`connection` Module
------------------------

.. automodule:: pygnetic.connection
    
   .. autoclass:: Connection(parent, conn_obj, message_factory)
      
      Example::
      
         # assuming chat_msg message is already defined
         connection.net_chat_msg('Tom', 'Test message')
         # alternative
         connection.send(chat_msg, 'Tom', 'Test message')
         # or
         connection.send('chat_msg', 'Tom', 'Test message')
      
      .. attribute:: parent
      
         :func:`Proxy <weakref.proxy>` to Client / Server instance
         
      .. attribute:: address
      
         Connection address
         
      .. attribute:: connected
      
         True if connected
         
      .. attribute:: data_sent
      
         Amount of data sent
         
      .. attribute:: data_received
      
         Amount of data received
         
      .. attribute:: messages_sent
      
         Amount of messages sent
         
      .. attribute:: messages_received
      
         Amount of messages received
         
      .. automethod:: add_handler(handler)
      
      .. automethod:: disconnect([*args])
      
      .. method:: net_message_name([\*args, \*\*kwargs])

         Send ``message_name`` messagge to remote host.
         
         :param args: parameters used to initialize message object
         :param kwargs: keyword parameters used to initialize message object
         
         It uses :meth:`__getattr__ <object.__getattr__>` mechanism to add
         :meth:`net_message_name` :func:`partial <functools.partial>` method
         to class and call it. Any subsequent call is realized by new method.
      
      .. automethod:: send(message[, *args, **kwargs])
         


:mod:`event` Module
-------------------

.. automodule:: pygnetic.event
   
   .. data:: NETWORK

   .. data:: NET_DISCONNECTED
   
   .. data:: NET_CONNECTED
   
   .. data:: NET_ACCEPTED
   
   .. data:: NET_RECEIVED
   
   Event attributes:
   
      Connected event
         | ``type`` = :const:`NETWORK`
         | ``net_type`` = :const:`NET_CONNECTED`
         | ``connection`` -- connection
      
      Disconnected event
         | ``type`` = :const:`NETWORK`
         | ``net_type`` = :const:`NET_DISCONNECTED`
         | ``connection`` -- connection
      
      Accepted event
         | ``type`` = :const:`NETWORK`
         | ``net_type`` = :const:`NET_ACCEPTED`
         | ``connection`` -- connection
      
      Received event
         | ``type`` = :const:`NETWORK`
         | ``net_type`` = :const:`NET_RECEIVED`
         | ``connection`` -- connection
         | ``message`` -- received message
         | ``msg_type`` -- message type
   
   Example::

      for e in pygame.event.get():
          if e.type == event.NETWORK:
              if e.net_type == event.NET_CONNECTED:
                  print 'connected'
              elif e.net_type == event.NET_DISCONNECTED:
                  print 'disconnected'
              elif e.net_type == event.NET_RECEIVED:
                  # assuming chat_msg message is already defined
                  if e.msg_type == chat_msg:
                      print '%s: %s' % (e.message.player, e.message.msg)
                  else:
                      print 'received:', e.message
   
   .. note::
      
      To use events you need to enable them with :func:`.init`
   
   .. warning::
   
      If you plan to change value of :const:`NETWORK` with
      :func:`.init`, then use:: 
         
         import pygnetic.event as event
         # rather than
         # from pygnetic.event import NETWORK


:mod:`handler` Module
---------------------

.. automodule:: pygnetic.handler

   .. autoclass:: Handler
   
      .. attribute:: connection
      
         :func:`Proxy <weakref.proxy>` to :class:`~.connection.Connection`
         derived class instance
         
      .. attribute:: server
      
         :func:`Proxy <weakref.proxy>` to :class:`~.server.Server`
         derived class instance   
      
      .. method:: net_message_name(message[, **kwargs])
      
         Called when ``message_name`` message is received
         
         :param kwargs:
            additional keyword arguments from :term:`network adapter`
      
      .. automethod:: on_connect
      
      .. automethod:: on_disconnect
      
      .. automethod:: on_recive(message[, **kwargs])


:mod:`message` Module
---------------------

.. automodule:: pygnetic.message

   .. data:: message_factory
      
      Default instance of :class:`MessageFactory` used by other modules.
   
   .. autoclass:: MessageFactory([s_adapter])
   
      Example::
      
         chat_msg = MessageFactory.register('chat_msg', ('player', 'msg'))
         data = MessageFactory.pack(chat_msg('Tom', 'Test message'))
         message = MessageFactory.unpack(data)
         player = message.player
         msg = message.msg
         
      .. note::
      
         You can create more instances of :class:`MessageFactory` when you want
         to separate messages for different connections in
         :class:`~.client.Client`.
      
      .. automethod:: get_by_name
      
      .. automethod:: get_by_type
      
      .. automethod:: get_hash
      
      .. automethod:: get_params
      
      .. automethod:: pack
      
      .. automethod:: register(name[, field_names[, **kwargs]])
      
      .. automethod:: reset_context
      
      .. automethod:: set_frozen
      
      .. automethod:: unpack
      
      .. automethod:: unpack_all


:mod:`server` Module
--------------------

.. automodule:: pygnetic.server
    
   .. autoclass:: Server([host[, port[, conn_limit[, *args, **kwargs]]]])
      
      .. attribute:: address
         
         Server address.
         
      .. automethod:: connections([exclude])
      
      .. automethod:: handlers([exclude])
      
      .. automethod:: update([timeout])


Small FAQ
=========

**Why I have to register message? Can't I just use dictionary to send it?**
   :meth:`~.message.MessageFactory.register` creates a compact
   data structure - :func:`namedtuple <collections.namedtuple>`, which contains
   only essential data, reducing overall amount of data to send. Take a look at
   example below and compare sizes of packed dictionary and structure created
   by :class:`~.message.MessageFactory`.

      >>> import msgpack
      >>> m1 = msgpack.packb({'action':'chat_msg', 'player':'Tom', 'msg':'Test message'})
      >>> m1, len(m1)
      ('\x83\xa6action\xa8chat_msg\xa6player\xa3Tom\xa3msg\xacTest message', 45)
      >>> import pygnetic as net
      >>> net.init()
      17:11:40 INFO     Using enet_adapter
      17:11:40 INFO     Using msgpack_adapter
      True
      >>> chat_msg = net.register('chat_msg', ('player', 'msg'))
      >>> m2 = net.message.message_factory.pack(chat_msg('Tom', 'Test message'))
      >>> m2, len(m2)
      ('\x93\x02\xa3Tom\xacTest message', 19)

   The only drawback of this method is the need to register the same messages
   in the same order in client and server.

**Why order of creating messages is important?**
   As You may noticed in previous example, there is no string with type of
   message in packed data. That's because type is encoded as integer,
   depending on order of creation.


Glossary
========

.. glossary::
   :sorted:

   network adapter
      class providing unified interface for different network libraries
      
   serialization adapter
      class providing unified interface for different serialization libraries