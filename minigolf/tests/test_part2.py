from unittest import TestCase

from minigolf import HitsMatch, HolesMatch, Player


class HitsMatchTestCase(TestCase):
    def setUp(self):
        self.players = [Player('A'), Player('B'), Player('C')]
        self.m = HitsMatch(3, self.players)

    def test__init__(self):
        with self.assertRaises(AssertionError):
            HitsMatch(0, [Player('A'), Player('B')])
        with self.assertRaises(AssertionError):
            HitsMatch(7, (Player('A'), Player('B')))
        with self.assertRaises(AssertionError):
            HitsMatch(2, [Player('A'), ])
        self.assertListEqual(list(self.m._players), [Player('A'), Player('B'), Player('C')])
        self.assertFalse(self.m.finished)
        self.assertEqual(self.m._current_hole, 0)

    def test_create_hole(self):
        self.m._create_hole()
        self.assertListEqual(list(self.m._players), [Player('B'), Player('C'), Player('A')])
        self.assertEqual(self.m._current_hole, 1)
        self.assertFalse(self.m._pass_list)
        self.m._create_hole()
        self.assertListEqual(list(self.m._players), [Player('C'), Player('A'), Player('B')])
        self.assertEqual(self.m._current_hole, 2)
        self.assertFalse(self.m._pass_list)
        self.assertFalse(self.m.finished)
        self.m._create_hole()
        self.assertTrue(self.m.finished)

    def test_get_top_score(self):
        self.assertEqual(self.m._get_top_score({'A': 1, 'B': 10, 'C': 0}), 0)
        self.assertEqual(self.m._get_top_score({'A': 100, 'B': 50, 'C': 210}), 50)

    def test_hit(self):
        self.m.hit()
        self.assertEqual(self.m._hole_result[self.players[0]], 1)
        self.m.hit()
        self.m.hit(True)
        self.assertEqual(self.m._hole_result[self.players[2]], 1)
        self.assertEqual(self.m._result[self.players[2]][self.m._current_hole], 1)
        self.assertListEqual(self.m._pass_list, [self.players[2]])
        self.assertEqual(self.m._current_hole, 0)
        self.m.hit(True)
        for _ in range(8):
            self.m.hit()
        self.assertEqual(self.m._current_hole, 1)
        for i in range(54):
            self.m.hit()
        with self.assertRaises(RuntimeError):
            self.m.hit()

    def test_get_table(self):
        self.m.hit()
        self.m.hit()
        self.m.hit(True)
        self.m.hit(True)
        self.assertEqual(self.m.get_table(), [
            ('A', 'B', 'C'),
            (2, None, 1),
            (None, None, None),
            (None, None, None),
        ])
        for _ in range(8):
            self.m.hit()
        self.assertFalse(self.m.finished)
        self.assertEqual(self.m.get_table(), [
            ('A', 'B', 'C'),
            (2, 10, 1),
            (None, None, None),
            (None, None, None),
        ])

    def test_get_winners(self):
        self.m.hit()
        with self.assertRaises(RuntimeError):
            self.m.get_winners()
        self.m.hit()
        self.m.hit(True)
        self.m.hit(True)
        for _ in range(8):
            self.m.hit()
        self.m.hit()
        for _ in range(3):
            self.m.hit(True)
        self.m.hit()
        self.m.hit(True)
        self.m.hit()
        self.m.hit(True)
        self.m.hit()
        self.m.hit(True)
        self.assertEqual(self.m.get_winners(), [
            self.players[0], self.players[2]
        ])


class HolesMatchTestCase(TestCase):
    def setUp(self):
        self.players = [Player('A'), Player('B'), Player('C')]
        self.m = HolesMatch(3, self.players)

    def test__init__(self):
        with self.assertRaises(AssertionError):
            HolesMatch(0, [Player('A'), Player('B')])
        with self.assertRaises(AssertionError):
            HolesMatch(-7, [Player('A'), Player('B')])
        with self.assertRaises(AssertionError):
            HolesMatch(2, [Player('A'), ])
        self.assertListEqual(list(self.m._players), [Player('A'), Player('B'), Player('C')])
        self.assertFalse(self.m.finished)
        self.assertEqual(self.m._current_hole, 0)

    def test_create_hole(self):
        self.m._create_hole()
        self.assertListEqual(list(self.m._players), [Player('B'), Player('C'), Player('A')])
        self.assertEqual(self.m._current_hole, 1)
        self.assertFalse(self.m._pass_list)
        self.m._create_hole()
        self.assertListEqual(list(self.m._players), [Player('C'), Player('A'), Player('B')])
        self.assertEqual(self.m._current_hole, 2)
        self.assertFalse(self.m._pass_list)
        self.assertFalse(self.m.finished)
        self.m._create_hole()
        self.assertTrue(self.m.finished)

    def test_get_top_score(self):
        self.assertEqual(self.m._get_top_score({'A': 1, 'B': 10, 'C': 0}), 10)
        self.assertEqual(self.m._get_top_score({'A': 100, 'B': 50, 'C': 210}), 210)

    def test_hit(self):
        self.m.hit(True)
        self.assertListEqual(self.m._pass_list, [self.players[0]])
        self.assertEqual(self.m._result[self.players[0]][self.m._current_hole], 1)
        self.assertEqual(self.m._hole_hits, 1)
        self.assertEqual(self.m._count_circle_hole(), 1)
        self.m.hit()
        self.m.hit()
        self.assertEqual(self.m._current_hole, 1)
        for i in range(60):
            self.m.hit()
        with self.assertRaises(RuntimeError):
            self.m.hit()

    def test_get_table(self):
        self.m.hit(True)
        self.m.hit()
        self.m.hit()
        self.assertFalse(self.m.finished)
        self.assertEqual(self.m.get_table(), [
            ('A', 'B', 'C'),
            (1, 0, 0),
            (None, None, None),
            (None, None, None),
        ])

    def test_get_winners(self):
        self.m.hit(True)
        self.m.hit()
        with self.assertRaises(RuntimeError):
            self.m.get_winners()
        self.m.hit()
        for _ in range(10):
            for _ in range(3):
                self.m.hit()
        for _ in range(9):
            for _ in range(3):
                self.m.hit()
        self.m.hit(True)
        self.m.hit(True)
        self.m.hit()
        self.assertEqual(self.m.get_winners(), [self.players[0]])

    def test_count_circle_hole(self):
        self.m.hit()
        self.assertEqual(self.m._count_circle_hole(), 1)
        for _ in range(10):
            self.m.hit()
        self.assertEqual(self.m._count_circle_hole(), 4)
