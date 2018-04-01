import itertools
from collections import deque, namedtuple
from abc import ABCMeta, abstractmethod

Player = namedtuple('Player', ['name'])
DEBUG = False


class Match(metaclass=ABCMeta):
    def __init__(self, holes, players):
        print(DEBUG*'Матч начался\n', end='')
        self._holes = iter(range(holes))
        self._players = deque([player for player in players])
        self._finish = False
        self._current_hole = next(self._holes)
        self._iter_players = itertools.cycle(self._players)
        self._pass_list = []
        self._result = {player: [None]*holes for player in players}

    def _create_hole(self):
        self._players.rotate(-1)
        try:
            self._current_hole = next(self._holes)
        except StopIteration:
            self._finish = True
            print(DEBUG*'Матч закончен\n', end='')
            return
        self._iter_players = itertools.cycle(self._players)
        self._pass_list = []
        print(DEBUG*'Подготовлена лунка №{}\n'.format(self._current_hole+1), end='')

    @abstractmethod
    def hit(self, success=False):
        pass

    @abstractmethod
    def _get_top_score(self, top):
        pass

    @property
    def finished(self):
        return self._finish

    def get_table(self):
        result = []
        for player, res in self._result.items():
            lst = [player.name, ]
            lst.extend(res)
            result.append(lst)
        print(*list(zip(*result))*DEBUG, sep='\n', end='')
        return list(zip(*result))

    def get_winners(self):
        if not self.finished:
            raise RuntimeError
        top = {player: sum(res) for player, res in self._result.items()}
        fin_result = self._get_top_score(top)
        result = [player for player, summ in top.items() if summ == fin_result]
        return result


class HitsMatch(Match):
    N = 10

    def __init__(self, holes, players):
        self._hole_result = {player: 0 for player in players}
        super(HitsMatch, self).__init__(holes, players)

    def _get_top_score(self, top):
        return min(top.values())

    def hit(self, success=False):
        if self.finished:
            raise RuntimeError
        player = next(self._iter_players)
        if player in self._pass_list:
            self.hit(success)
            return
        hole = self._current_hole
        print(DEBUG*'Игрок {} на лунке {}\n'.format(player.name, hole+1), end='')
        self._hole_result[player] += 1
        if success:
            self._pass_list.append(player)
            self._result[player][hole] = self._hole_result[player]
        elif self._hole_result[player] == self.N - 1:
            self._pass_list.append(player)
            self._result[player][hole] = self.N
        if len(self._pass_list) == len(self._players):
            self._hole_result = {player: 0 for player in self._players}
            self._create_hole()


class HolesMatch(Match):
    def __init__(self, holes, players):
        self._hole_hits = 0
        super(HolesMatch, self).__init__(holes, players)

    def _get_top_score(self, top):
        return max(top.values())

    def _count_circle_hole(self):
        return self._hole_hits // len(self._players) + 1

    def hit(self, success=False):
        if self.finished:
            raise RuntimeError
        player = next(self._iter_players)
        hole = self._current_hole
        print(DEBUG*'Игрок {} на лунке {}\n'.format(player.name, hole + 1), end='')
        if success:
            self._pass_list.append(player)
            self._result[player][hole] = 1
        elif self._pass_list or self._count_circle_hole() == 10:
            self._pass_list.append(player)
            self._result[player][hole] = 0
        self._hole_hits += 1
        if len(self._pass_list) == len(self._players):
            self._hole_hits = 0
            self._create_hole()
