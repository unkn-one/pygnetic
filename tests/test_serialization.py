if __name__ == '__main__':
    import sys
    import os
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir, pkg_name = os.path.split(pkg_dir)
    sys.path.insert(0, parent_dir)
import unittest
import pygnetic


class CommonTests(object):
    def test_select_adapter(self):
        pygnetic.serialization.select_adapter(self.adapter_lib_name)
        self.assertEqual(pygnetic.serialization.selected_adapter,
                         self.adapter,
                         'incorrect selected adapter')
        self.assertEqual(pygnetic.serialization.pack,
                         self.adapter.pack,
                         'incorrect selected adapter pack function')
        self.assertEqual(pygnetic.serialization.unpack,
                         self.adapter.unpack,
                         'incorrect selected adapter unpack function')
        self.assertEqual(pygnetic.serialization.unpacker,
                         self.adapter.unpacker,
                         'incorrect selected adapter unpacker class')

    def test_get_adapter(self):
        adapter = pygnetic.serialization.get_adapter(self.adapter_lib_name)
        self.assertEqual(adapter, self.adapter,
                         'incorrect selected adapter')


class MsgpackAdapterTests(unittest.TestCase, CommonTests):
    def setUp(self):
        import pygnetic.serialization.msgpack_adapter as adapter
        self.adapter = adapter
        self.adapter_lib_name = 'msgpack'


class JsonAdapterTests(unittest.TestCase, CommonTests):
    def setUp(self):
        import pygnetic.serialization.json_adapter as adapter
        self.adapter = adapter
        self.adapter_lib_name = 'json'


if __name__ == '__main__':
    unittest.main(verbosity=2)
