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

    def test_matches_alone(self):
        tree = Tree()

        member = 'joar'

        match_paths = [
            'foo.bar.baz',
            'foo.bar.baz.frog',
        ]

        wildcard_path = 'foo.bar.*'

        # Add both wildcard and path to tree.
        tree.add(member, wildcard_path)

        for path in match_paths:
            # Convert tuple generator to dict
            matches = dict(tree.get_matches(path))

            self.assertEqual({wildcard_path: member}, matches)

    def test_matches_direct(self):
        """
        Test that literal 'foo.bar.*' matches 'foo.bar.*' wildcard.
        :return:
        """
        tree = Tree()

        member = 'joar'
        wildcard_path = 'foo.bar.*'

        # Add both wildcard and path to tree.
        tree.add(member, wildcard_path)

        matches = dict(tree.get_matches(wildcard_path))

        self.assertEqual({wildcard_path: member}, matches)

    def test_not_matches(self):
        tree = Tree()

        member = 'joar'
        path = 'foo.not-bar.baz'
        wildcard_path = 'foo.bar.*'

        # Add member to paths 'foo.not-bar.baz' and 'foo.bar.*'
        tree.add(member, wildcard_path)

        # Get matches for 'foo.not-bar.baz' and convert tuple generator to dict
        matches = dict(tree.get_matches(path))

        # Assert 'foo.bar.*' did not match
        self.assertNotIn(wildcard_path, matches)


if __name__ == '__main__':
    unittest.main()
