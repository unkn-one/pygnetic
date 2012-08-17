pygnetic --- Easy networking in Pygame
======================================

**pygnetic** is a library designed to help in the development of
network games and applications in `Pygame <http://www.pygame.org>`_.


Features
--------

* Two approaches to handle network events
   * generating events in pygame queue
   * using handler classes
* Efficient packaging of data through the message system
* Support for multiple network and serialization libraries


Contents
--------

.. toctree::
   :maxdepth: 2
   :glob:

   api/index
   examples
   license


Installation
------------

**pygnetic** can be installed with
`windows installer <http://pypi.python.org/pypi/pygnetic/#downloads>`_
or with `pip <http://www.pip-installer.org>`_::

   pip install pygnetic

Optional requirements
---------------------

* `Message Pack <http://msgpack.org/>`_ (recommended)
* `pyenet <http://code.google.com/p/pyenet/>`_


Resources
---------

* Package on PyPI -- http://pypi.python.org/pypi/pygnetic
* Repository on Bitbucket -- https://bitbucket.org/bluex/pygnetic
* Documentation -- http://pygnetic.readthedocs.org
* Development blog -- http://pygame-networking.blogspot.com


Credits
-------

pygnetic is under development by Szymon Wróblewski <bluex0@gmail.com>
as `GSoC 2012 <http://code.google.com/soc/>`_ project and mentored by
René Dudfield <renesd@gmail.com>.


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
