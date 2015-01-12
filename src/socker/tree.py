from collections import defaultdict


class Tree(defaultdict, dict):

    def __init__(self):
        defaultdict.__init__(self, self.__class__)
        self.members = set()

    def __repr__(self):
        repr_ = dict(self)
        repr_.update(self.__dict__)
        return repr(repr_)

    def walk(self, path):
        """
        Walk tree and yield nodes in path.

        :param path: dot separated tree path
        """
        parts = path.split('.')
        cursor = self

        for part in parts:
            yield cursor, False
            cursor = cursor[part]

        yield cursor, True

    def get_leaf(self, path):
        """
        Get last node of path in tree

        :param path: dot separated tree path
        :return: node
        """
        node, _ = list(self.walk(path))[-1]
        return node

    def add(self, member, *paths):
        """
        Add member to nodes at paths

        :param member: object to add in tree at paths
        :param paths: dot separated tree paths
        """
        for path in paths:
            self.get_leaf(path).members.add(member)

    def remove(self, member, *paths):
        """
        Remove member from nodes at paths

        :param member: object to add in tree at paths
        :param paths: dot separated tree paths
        """
        for path in paths:
            self.get_leaf(path).members.remove(member)

    def get_members(self, path):
        """
        Get unique members for path, including parent wildcards.

        :param path: dot separated tree path
        :return: set of members
        """
        members = set()

        for node, is_leaf in self.walk(path):
            if is_leaf:
                members.update(node.members)
            else:
                members.update(node['*'].members)

        return members
