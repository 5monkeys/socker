import unittest

from socker.router import Tree


class TestTree(unittest.TestCase):
    def test_subscribe(self):
        t = Tree()
        channel = 'foo.bar.baz'
        other_channel = 'foo.bar.zab'
        node = 'joar'

        t.subscribe(channel, node)
        t.subscribe(other_channel, node)

        self.assertEqual(t['foo']['bar']['baz'].subscribers, {node})
        self.assertEqual(t['foo']['bar']['zab'].subscribers, {node})

    def test_get_subscribers(self):
        t = Tree()
        wildcard_channel = 'foo.bar.baz.*'
        channel = 'foo.bar.baz.zab'
        node = 'joar'

        t.subscribe(wildcard_channel, node)

        subscribers = t.get_subscribers(channel)

        self.assertEqual(set(subscribers), {node})

        subscribers = t.get_subscribers(channel + '.bah')

        self.assertEqual(set(subscribers), {node})


    def test_unsubscribe(self):
        t = Tree()
        wc_channel = 'foo.bar.*'
        channel = 'foo.bar.baz'
        node = 'joar'

        t.subscribe(wc_channel, node)
        t.subscribe(channel, node)

        t.unsubscribe(wc_channel, node)

        self.assertEqual(set(t.get_subscribers(wc_channel)), set())

if __name__ == '__main__':
    unittest.main()