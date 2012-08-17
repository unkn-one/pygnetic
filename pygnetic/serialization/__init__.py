# -*- coding: utf-8 -*-
"""Serialization adapters."""

from .. import _utils

_selected_adapter = None
pack = unpack = unpacker = None


def select_adapter(names):
    global _selected_adapter, pack, unpack, unpacker
    _selected_adapter = _utils.select_adapter(__name__, names)
    if _selected_adapter is not None:
        pack = _selected_adapter.pack
        unpack = _selected_adapter.unpack
        unpacker = _selected_adapter.unpacker
