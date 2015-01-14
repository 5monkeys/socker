import unittest

from socker.tree import Tree


class TestTree(unittest.TestCase):

    def test_add(self):
        tree = Tree()

        member = 'joar'
        path1 = 'foo.bar.baz'
        path2 = 'foo.bar.zab'

        tree.add(member, path1, path2)

        self.assertEqual(tree['foo']['bar']['baz'].members, {member})
        self.assertEqual(tree['foo']['bar']['zab'].members, {member})

    def test_get(self):
        tree = Tree()

        member = 'joar'
        path = 'foo.bar.baz.zab'
        wildcard_path = 'foo.bar.baz.*'

        tree.add(member, wildcard_path)
        members = tree.get_members(path)
        self.assertEqual(members, {member})

        members = tree.get_members(path + '.bah')
        self.assertEqual(members, {member})

    def test_remove(self):
        tree = Tree()

        member = 'joar'
        path = 'foo.bar.baz'
        wildcard_path = 'foo.bar.*'

        tree.add(member, path, wildcard_path)

        tree.remove(member, wildcard_path)
        members = tree.get_members(wildcard_path)
        self.assertEqual(members, set())                   # * member removed
        self.assertNotIn('*', tree.get('foo').get('bar'))  # * node cleaned up

        self.assertIn('baz', tree.get('foo').get('bar'))   # still got baz node
        members = tree.get_members(path)
        self.assertEqual(members, {member})  # still got baz members

        tree.remove(member, path)
        members = tree.get_members(path)
        self.assertEqual(members, set())     # baz member removed
        self.assertNotIn('foo', tree)        # foo (bar, baz) node cleaned up
        self.assertFalse(tree)


if __name__ == '__main__':
    unittest.main()
