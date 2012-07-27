import msgpack
_packer = msgpack.Packer()
_unpacker = msgpack.Unpacker()
pack = _packer.pack
unpack = lambda data: _unpacker.feed(data) or _unpacker.unpack()
