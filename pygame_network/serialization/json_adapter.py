import json


class JSONDecoder(json.JSONDecoder):
    """JSONDecoder with streaming feature"""
    def __init__(self):
        super(JSONDecoder, self).__init__()
        self.buffer = bytearray()

    def feed(self, data):
        self.buffer.extend(data)

    def decode(self):
        try:
            obj, end = self.scan_once(self.buffer.decode(), 0)
            del self.buffer[:end]
            return obj
        except:
            raise StopIteration('No more data to decode.')

    next = decode


pack = json.dumps
unpack = json.loads
unpacker = JSONDecoder
