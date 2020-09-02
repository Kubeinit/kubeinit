"""test_package unit test."""

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import unittest

from ansible_collections.kubeinit.kubeinit.plugins.module_utils \
    import const


class TestStringMethods(unittest.TestCase):
    """Run the TestStringMethods method.

    This method check if test_isupper pass
    """

    def test_upper(self):
        """Run the test_upper method."""
        self.assertEqual(const.KUBEINIT_VERSION.upper(), const.KUBEINIT_VERSION)

    def test_isupper(self):
        """Run the test_isupper method."""
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        """Run the test_split method."""
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)


if __name__ == '__main__':
    unittest.main()
