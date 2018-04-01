import itertools
from collections import deque, namedtuple
from abc import ABCMeta, abstractmethod

Player = namedtuple('Player', ['name'])


class Match(metaclass=ABCMeta):
    def __init__(self, holes, players):
        #  print('Матч начался')
        self._holes = range(holes).__iter__()
        self._players = deque([player for player in players])
        self._finish = False
        self._current_hole = self._holes.__next__()
        self._iter_players = itertools.cycle(self._players)
        self._pass_list = []
        self._result = {player: [None for _ in range(holes)] for player in players}

    def _create_hole(self):
        self._players.rotate(-1)
        try:
            self._current_hole = self._holes.__next__()
        except StopIteration:
            self._finish = True
            #  print('Матч закончен')
            return
        self._iter_players = itertools.cycle(self._players)
        self._pass_list = []
        #  print('Подготовлена лунка №{}'.format(self.current_hole+1))

    @abstractmethod
    def hit(self, success=False):
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
        #  print(*list(zip(*result)), sep='\n')
        return list(zip(*result))

    def get_winners(self):
        if not self.finished:
            raise RuntimeError
        top = {player: sum(res) for player, res in self._result.items()}
        if self.__class__.__name__ == 'HolesMatch':
            fin_result = max(top.values())
        else:
            fin_result = min(top.values())
        result = [player for player, summ in top.items() if summ == fin_result]
        return result


class HitsMatch(Match):
    def __init__(self, holes, players):
        self._hole_result = {player: 0 for player in players}
        super(HitsMatch, self).__init__(holes, players)

    def hit(self, success=False):
        if self.finished:
            raise RuntimeError
        player = self._iter_players.__next__()
        if player in self._pass_list:
            self.hit(success)
            return
        hole = self._current_hole
        #  print('Игрок {} на лунке {}'.format(player.name, hole+1))
        self._hole_result[player] += 1
        if success:
            self._pass_list.append(player)
            self._result[player][hole] = self._hole_result[player]
        elif self._hole_result[player] == 9:
            self._pass_list.append(player)
            self._result[player][hole] = 10
        if len(self._pass_list) == len(self._players):
            self._hole_result = {player: 0 for player in self._players}
            self._create_hole()


class HolesMatch(Match):
    def __init__(self, holes, players):
        self._hole_hits = 0
        super(HolesMatch, self).__init__(holes, players)

    def _count_circle_hole(self):
        return self._hole_hits // len(self._players) + 1

    def hit(self, success=False):
        if self.finished:
            raise RuntimeError
        player = self._iter_players.__next__()
        hole = self._current_hole
        #  print('Игрок {} на лунке {}'.format(player.name, hole + 1))
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
