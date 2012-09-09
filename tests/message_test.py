if __name__ == '__main__':
    import sys
    import os
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir, pkg_name = os.path.split(pkg_dir)
    sys.path.insert(0, parent_dir)
import unittest
import pygnetic


class MessageTests(unittest.TestCase):

    def setUp(self):
        pygnetic.serialization.select_adapter('msgpack')
        self.message_factory = pygnetic.message.MessageFactory()

    def test_register(self):
        message_factory = pygnetic.message.MessageFactory()
        name = 'test_01'
        fields = ('name_01', 'name_02', 'name_03')
        parameters = {'arg_1': 1, 'arg_2': 2, 'arg_3': 3}
        test_01 = message_factory.register(name, fields, **parameters)
        self.assertIsNotNone(test_01)
        self.assertEqual(test_01.__name__, name)
        self.assertTupleEqual(test_01._fields, fields)
        self.assertDictEqual(message_factory.get_params(test_01), parameters)

if __name__ == '__main__':
    unittest.main(verbosity=2)
