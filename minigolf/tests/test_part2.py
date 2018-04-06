from unittest import TestCase

from minigolf import HitsMatch, HolesMatch, Player


class HitsMatchTestCase(TestCase):
    def setUp(self):
        self._players = [Player('A'), Player('B'), Player('C')]
        self._match = HitsMatch(3, self._players)

    def test__init__(self):
        match = self._match
        with self.assertRaises(AssertionError):
            HitsMatch(0, [Player('A'), Player('B')])
        with self.assertRaises(AssertionError):
            HitsMatch(7, (Player('A'), Player('B')))
        with self.assertRaises(AssertionError):
            HitsMatch(2, [Player('A'), ])
        self.assertListEqual(list(match._players), [Player('A'), Player('B'), Player('C')])
        self.assertFalse(match.finished)
        self.assertEqual(match._current_hole, 0)

    def test_create_hole(self):
        match = self._match
        match._create_hole()
        self.assertListEqual(list(match._players), [Player('B'), Player('C'), Player('A')])
        self.assertEqual(match._current_hole, 1)
        self.assertFalse(match._pass_list)
        match._create_hole()
        self.assertListEqual(list(match._players), [Player('C'), Player('A'), Player('B')])
        self.assertEqual(match._current_hole, 2)
        self.assertFalse(match._pass_list)
        self.assertFalse(match.finished)
        match._create_hole()
        self.assertTrue(match.finished)

    def test_get_top_score(self):
        match = self._match
        self.assertEqual(match._get_top_score({'A': 1, 'B': 10, 'C': 0}), 0)
        self.assertEqual(match._get_top_score({'A': 100, 'B': 50, 'C': 210}), 50)

    def test_hit(self):
        match = self._match
        players = self._players
        match.hit()
        self.assertEqual(match._hole_result[players[0]], 1)
        match.hit()
        match.hit(True)
        self.assertEqual(match._hole_result[players[2]], 1)
        self.assertEqual(match._result[players[2]][match._current_hole], 1)
        self.assertListEqual(match._pass_list, [players[2]])
        self.assertEqual(match._current_hole, 0)
        match.hit(True)
        for _ in range(8):
            match.hit()
        self.assertEqual(match._current_hole, 1)
        for i in range(54):
            match.hit()
        with self.assertRaises(RuntimeError):
            match.hit()

    def test_get_table(self):
        match = self._match
        match.hit()
        match.hit()
        match.hit(True)
        match.hit(True)
        self.assertEqual(match.get_table(), [
            ('A', 'B', 'C'),
            (2, None, 1),
            (None, None, None),
            (None, None, None),
        ])
        for _ in range(8):
            match.hit()
        self.assertFalse(match.finished)
        self.assertEqual(match.get_table(), [
            ('A', 'B', 'C'),
            (2, 10, 1),
            (None, None, None),
            (None, None, None),
        ])

    def test_get_winners(self):
        match = self._match
        players = self._players
        match.hit()
        with self.assertRaises(RuntimeError):
            match.get_winners()
        match.hit()
        match.hit(True)
        match.hit(True)
        for _ in range(8):
            match.hit()
        match.hit()
        for _ in range(3):
            match.hit(True)
        match.hit()
        match.hit(True)
        match.hit()
        match.hit(True)
        match.hit()
        match.hit(True)
        self.assertEqual(match.get_winners(), [
            players[0], players[2]
        ])


class HolesMatchTestCase(TestCase):
    def setUp(self):
        self._players = [Player('A'), Player('B'), Player('C')]
        self._match = HolesMatch(3, self._players)

    def test__init__(self):
        match = self._match
        with self.assertRaises(AssertionError):
            HolesMatch(0, [Player('A'), Player('B')])
        with self.assertRaises(AssertionError):
            HolesMatch(-7, [Player('A'), Player('B')])
        with self.assertRaises(AssertionError):
            HolesMatch(2, [Player('A'), ])
        self.assertListEqual(list(match._players), [Player('A'), Player('B'), Player('C')]) ########
        self.assertFalse(match.finished)
        self.assertEqual(match._current_hole, 0)

    def test_create_hole(self):
        match = self._match
        match._create_hole()
        self.assertListEqual(list(match._players), [Player('B'), Player('C'), Player('A')])
        self.assertEqual(match._current_hole, 1)
        self.assertFalse(match._pass_list)
        match._create_hole()
        self.assertListEqual(list(match._players), [Player('C'), Player('A'), Player('B')])
        self.assertEqual(match._current_hole, 2)
        self.assertFalse(match._pass_list)
        self.assertFalse(match.finished)
        match._create_hole()
        self.assertTrue(match.finished)

    def test_get_top_score(self):
        match = self._match
        self.assertEqual(match._get_top_score({'A': 1, 'B': 10, 'C': 0}), 10)
        self.assertEqual(match._get_top_score({'A': 100, 'B': 50, 'C': 210}), 210)

    def test_hit(self):
        match = self._match
        players = self._players
        match.hit(True)
        self.assertListEqual(match._pass_list, [players[0]])
        self.assertEqual(match._result[players[0]][match._current_hole], 1)
        self.assertEqual(match._hole_hits, 1)
        self.assertEqual(match._count_circle_hole(), 1)
        match.hit()
        match.hit()
        self.assertEqual(match._current_hole, 1)
        for i in range(60):
            match.hit()
        with self.assertRaises(RuntimeError):
            match.hit()

    def test_get_table(self):
        match = self._match
        match.hit(True)
        match.hit()
        match.hit()
        self.assertFalse(match.finished)
        self.assertEqual(match.get_table(), [
            ('A', 'B', 'C'),
            (1, 0, 0),
            (None, None, None),
            (None, None, None),
        ])

    def test_get_winners(self):
        match = self._match
        players = self._players
        match.hit(True)
        match.hit()
        with self.assertRaises(RuntimeError):
            match.get_winners()
        match.hit()
        for _ in range(10):
            for _ in range(3):
                match.hit()
        for _ in range(9):
            for _ in range(3):
                match.hit()
        match.hit(True)
        match.hit(True)
        match.hit()
        self.assertEqual(match.get_winners(), [players[0]])

    def test_count_circle_hole(self):
        match = self._match
        match.hit()
        self.assertEqual(match._count_circle_hole(), 1)
        for _ in range(10):
            match.hit()
        self.assertEqual(match._count_circle_hole(), 4)
