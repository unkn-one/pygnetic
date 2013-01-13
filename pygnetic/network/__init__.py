# -*- coding: utf-8 -*-
"""Network adapters."""

import types
from .. import _utils
from .. import client
from .. import server

selected_adapter = None


def select_adapter(names):
    """Select first found adapter

    :param names: - string or list of strings with names of libraries
    :return: adapter module
    """
    global selected_adapter
    selected_adapter = _utils.find_adapter(__name__, names)
    return selected_adapter

def get_adapter(names):
    """Return adapter

    :param names: - string or list of strings with names of libraries
    :return: adapter module
    """
    return _utils.find_adapter(__name__, names)


class Client(object):
    """Proxy class for selected :term:`network adapter`."""
    _adapter = None

    def __init__(self, *args, **kwargs):
        adapter = kwargs.pop('adapter', self._adapter)
        if adapter is not None:
            if not isinstance(adapter, client.Client):
                adapter = get_adapter(adapter).Client(*args, **kwargs)
        elif selected_adapter is not None:
            adapter = selected_adapter.Client(*args, **kwargs)
        else:
            raise AttributeError("Client adapter is not selected")
        self._adapter = adapter

    def __getattr__(self, name):
        return getattr(self._adapter, name)


class Server(object):
    """Proxy class for selected :term:`network adapter`."""
    _adapter = None

    def __init__(self, *args, **kwargs):
        adapter = kwargs.pop('adapter', self._adapter)
        if adapter is not None:
            if not isinstance(adapter, server.Server):
                adapter = get_adapter(adapter).Server(*args, **kwargs)
        elif selected_adapter is not None:
            adapter = selected_adapter.Server(*args, **kwargs)
        else:
            raise AttributeError("Server adapter is not selected")
        self._adapter = adapter

    def __getattr__(self, name):
        return getattr(self._adapter, name)
