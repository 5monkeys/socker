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
        self.assertEqual(members, set())

        members = tree.get_members(path)
        self.assertEqual(members, {member})


if __name__ == '__main__':
    unittest.main()
