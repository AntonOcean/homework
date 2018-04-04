from unittest import TestCase

from minigolf import HitsMatch, HolesMatch, Player


class BadMatchTestCase(TestCase):
    def test_scenario(self):
        with self.assertRaises(AssertionError):
            m = HitsMatch(0, [Player('A'), Player('B')])
        with self.assertRaises(AssertionError):
            m = HitsMatch(7, (Player('A'), Player('B')))
        with self.assertRaises(AssertionError):
            m = HitsMatch(2, [Player('A'), ])
        with self.assertRaises(AssertionError):
            m = HolesMatch(0, [Player('A'), Player('B')])
        with self.assertRaises(AssertionError):
            m = HolesMatch(-7, [Player('A'), Player('B')])
        with self.assertRaises(AssertionError):
            m = HolesMatch(2, [Player('A'), ])