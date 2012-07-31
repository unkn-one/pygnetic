:mod:`message` Module
=====================

.. module:: message
   :synopsis: Message factory and predefined messages.
   

.. class:: MessageFactory

   Class allowing to register new message types and pack/unpack them.
   
   Example::
   
      chat_msg = MessageFactory.register('chat_msg', ('player', 'msg'))
      data = MessageFactory.pack(chat_msg('Tom', 'Test message'))
      received_msg = MessageFactory.unpack(data)
      player = received_msg.player
      msg = received_msg.msg

   .. note::
      
      You can create instances of :class:`MessageFactory`, when you want to
      separate messages for different connections in Client.
      
   
   .. classmethod:: register(name, field_names[, kwargs])
   
      Register new message type
      
      :param name: name of message class
      :param field_names: list of names of message fields
      :param kwargs: keyword arguments for send method
      :return: packet (namedtuple)
      

Predefined messages
-------------------

.. class:: chat_msg(player, msg)

   :param player: player name
   :param msg: message


.. class:: update_remoteobject(type_id, obj_id, variables)

   Message used by :class:`syncobject.SyncObjectManager` to update state of
   :class:`syncobject.RemoteObject`.

   :param type_id: identifier of object type
   :param obj_id: identifier of object instance
   :param variables: list of changed object variables


Small FAQ
---------

Why I have to register message? Can't I just use dictionary to send it?
   :meth:`register` creates a compact data structure -
   :func:`namedtuple <collections.namedtuple>`, which contains only essential
   data, reducing overall amount of data to send. Take a look at example below
   and compare sizes of packed dictionary and structure created by
   :class:`MessageFactory`.

      >>> import msgpack
      >>> m1 = msgpack.packb({'action':'chat_msg', 'player':'Tom', 'msg':'Test message'})
      >>> m1, len(m1)
      ('\x83\xa6action\xa8chat_msg\xa6player\xa3Tom\xa3msg\xacTest message', 45)
      >>> import pygame_network as net
      >>> net.init()
      12:33:14:INFO:Using enet network module
      12:33:14:INFO:Using msgpack serialization module
      >>> chat_msg = net.register('chat_msg', ('player', 'msg'))
      >>> m2 = net.message.MessageFactory.pack(0, chat_msg('Tom', 'Test message'))
      >>> m2, len(m2)
      ('\x94\x03\x00\xa3Tom\xacTest message', 20)

   The only drawback of this method is the need to register the same messages
   in the same order in client and server.

Why order of creating messages is important?
   As You may noticed in previous example, there is no string with type of
   message in packed data. That's because type is encoded as integer,
   depending on order of creation.
