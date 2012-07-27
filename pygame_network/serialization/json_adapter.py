import json
_packer = json.JSONEncoder()
_unpacker = json.JSONDecoder()
pack = _packer.encode
unpack = _unpacker.decode
