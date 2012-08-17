# -*- coding: utf-8 -*-
"""Network adapters."""

from .. import _utils

_selected_adapter = None


def select_adapter(names):
    global _selected_adapter
    _selected_adapter = _utils.select_adapter(__name__, names)


class Client(object):
    "Class creating its instance based on selected :term:`network adapter`."

    def __new__(cls, *args, **kwargs):
        "Create instance of Client class depending on selected network adapter"
        b = cls.__bases__
        if Client in b:  # creation by inheritance
            i = b.index(Client) + 1
            cls.__bases__ = b[:i] + (_selected_adapter.Client,) + b[i:]
            return super(cls, cls).__new__(cls, *args, **kwargs)
        else:  # direct object creation
            # can't assign to __bases__ - bugs.python.org/issue672115
            return _selected_adapter.Client(*args, **kwargs)


class Server(object):
    "Class creating its instance based on selected :term:`network adapter`."

    def __new__(cls, *args, **kwargs):
        "Create instance of Server class depending on selected network adapter"
        b = cls.__bases__
        if Server in b:  # creation by inheritance
            i = b.index(Server) + 1
            cls.__bases__ = b[:i] + (_selected_adapter.Server,) + b[i:]
            return super(Server, cls).__new__(cls, *args, **kwargs)
        else:  # direct object creation
            # can't assign to __bases__ - bugs.python.org/issue672115
            return _selected_adapter.Server(*args, **kwargs)
