:mod:`syncobject` Module
========================

.. module:: syncobject
   :synopsis: Classes used by automatic objects synchronization.


.. class:: RemoteObject

   Class representing remote :class:`SyncObject` locally


.. class:: SyncObject(*args, **kwargs)

   Base class for synchronized objects
   
   The base class for local objects to be automatically synchronized with 
   remote host. Derived class should replace :attr:`sync_var`
   to specify a tuple of variable names for synchronization.
   Each assignment to a variable defined in :attr:`sync_var` will notify
   :class:`SyncObjectManager` which, depending on :attr:`sync_mode`, will 
   either prepare update packet (:const:`SYNCOBJECT_MODE_AUTO`) or wait with 
   preparation for :meth:`send_changes` call (:const:`SYNCOBJECT_MODE_MANUAL`).
   :attr:`sync_flags` overrides default enet sending flags.


   .. attribute:: SyncObject.sync_flags
   
      Overrides default enet sending flags.


   .. attribute:: SyncObject.sync_mode

      Synchronization mode flags:
      
      * update packet preparation mode
         * :const:`SYNCOBJECT_MODE_AUTO` - prepare update packet after every 
           variable assignment *(default)*
         * :const:`SYNCOBJECT_MODE_MANUAL` - wait with update packet 
           preparation for :meth:`send_changes` call
      * access mode
         * :const:`SYNCOBJECT_MODE_READWRITE` - allow changes from 
           :class:`RemoteObject` to impact :class:`SyncObject` *(default)*
         * :const:`SYNCOBJECT_MODE_READONLY` - prevent changes from 
           :class:`RemoteObject` to impact :class:`SyncObject`
   
   .. attribute:: SyncObject.sync_var
   
      Tuple of variable names for synchronization.
      
      *Allowed types:* all basic types and derivatives.


   .. method:: SyncObject.notify_change(var_name)
   
      Notify :class:`SyncObjectManager` that variable was changed
      
      .. note::
         Should be used whenever variable is modified without being assigned.
      
   
   .. method:: SyncObject.send_changes()
   
      Prepare update packet to send
      
      When :attr:`sync_mode` is :const:`SYNCOBJECT_MODE_MANUAL`,
      notify :class:`SyncObjectManager` to prepare update packet

   **Callbacks:**

   .. method:: SyncObject.on_change()

      Callback when variable(s) was changed by remote host


   .. method:: SyncObject.on_reply(packet_id)

      Callback when there was reply to change from remote host



.. class:: SyncObjectManager

   Manager of :class:`SyncObject` instances, shouldn't be used by user
   
   .. note::
   
       Class used by :class:`SyncObject` automatically, no need to use it.
   
   
   .. classmethod:: SyncObjectManager.changed(obj, var_name)
   
      Prepares update packet
      
   
   .. classmethod:: SyncObjectManager.register(obj)
   
      Registers new object deriving from :class:`SyncObject`

