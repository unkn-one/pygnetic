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
        pygnetic.serialization.select_adapter('json')
        self.message_factory = pygnetic.message.MessageFactory()

    @classmethod
    def generate_msgs(cls, messages, fields, parameters):
        message_factory = pygnetic.message.MessageFactory()
        return message_factory, [
            message_factory.register(
                'test_%d' % (m + 1),
                ['name_%d' % (f + 1) for f in range(fields)],
                **{'arg_%d' % (a + 1) : (a + 1) for a in range(parameters)}
            ) for m in range(messages)
        ]

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

    def test_pack(self):
        mf, msgs = self.generate_msgs(3, 3, 3)
        data = list(range(1, 4))
        for i, msg in enumerate(msgs):
            self.assertEqual(
                '[%s]' % ', '.join(str(d) for d in [i + 1] + data),
                mf.pack(msg(*data))
            )
        with self.assertRaises(ValueError):
            mf.pack('')

    def test_unpack(self):
        mf, msgs = self.generate_msgs(3, 3, 3)
        data = list(range(1, 4))
        for i, msg in enumerate(msgs):
            self.assertTupleEqual(
                mf.unpack('[%s]' % ', '.join(str(d) for d in [i + 1] + data)),
                msg(*data)
            )

def suite():
    return unittest.TestLoader().loadTestsFromTestCase(MessageTests)

if __name__ == '__main__':
    unittest.main(verbosity=2)
