from termcolor import cprint
from enum import Enum
from copy import deepcopy


class SolutionStatus(Enum):
    SUCCESSFUL = 0
    ERROR = 1
    STUCKED = 2


class SudokuSolver:
    def __init__(self):
        self.n = 3
        s = Sudoku(n=self.n, v=True)
        self.correct = s.load_from_file('sudoku.txt')

        self.available_states = [s]

    def solve(self):
        if self.correct:
            while len(self.available_states) > 0:
                s = self.available_states.pop()
                status = s.solve()
                if status == SolutionStatus.SUCCESSFUL:
                    s.discard_new_cell_values()
                    s.print()
                    return
                elif status == SolutionStatus.ERROR:
                    continue
                elif status == SolutionStatus.STUCKED:
                    minimum_options = s.n2
                    i_opt, j_opt = 0, 0
                    # TODO simplify in Pythonic manner
                    for i in range(s.n2):
                        for j in range(s.n2):
                            n = len(s.state[i][j][1])
                            if 0 < n < minimum_options:
                                minimum_options = n
                                i_opt, j_opt = i, j

                    for v in s.state[i_opt][j_opt][1]:
                        s_new = deepcopy(s)
                        s_new.set_cell_value(i_opt, j_opt, v)
                        self.available_states.append(s_new)

        else:
            print('Incorrect original state of the sudoku!')


class Sudoku:
    def __init__(self, n, v):
        if type(n) != int or not 2 <= n <= 5:
            raise Exception('Sudoku rank must be an integer between 2 and 5')

        self.n = n
        self.n2 = n ** 2
        self.digits = set(range(1, self.n2 + 1))

        self.v = v

        # third parameter - is guessed number new
        self.state = [[[None, self.digits.copy(), False] for _1 in range(self.n2)] for _2 in range(self.n2)]
        self.unknown_cnt = self.n2 ** 2

    @staticmethod
    def print_cell(cell):
        if cell[0] is None:
            cprint(' ', 'grey', f'on_white', end='')
        elif cell[2]:
            cprint(cell[0], 'grey', f'on_yellow', end='')
        else:
            cprint(cell[0], 'grey', f'on_green', end='')

    def print(self):
        for i in range(self.n2):
            if i % self.n == 0:
                print((' ' + '-' * self.n) * self.n)

            for j in range(self.n2):
                if j % self.n == 0:
                    print('|', end='')
                self.print_cell(self.state[i][j])
            print('|')

        print((' ' + '-' * self.n) * self.n)
        print()

        self.discard_new_cell_values()

    def load_from_file(self, filename):
        with open(filename, encoding='utf-8') as file:
            i = 0
            for line in file:
                if '-' in line or len(line.strip()) == 0:
                    continue

                vals = line.split()
                j = 0
                for v in vals:
                    if v == '|':
                        continue
                    elif v.isdigit():
                        if not self.set_cell_value(i, j, int(v)):
                            return False
                    elif v != '?':
                        raise Exception('Unknown symbol! Only digits for known numbers, ? for unknown '
                                        'and | as separators are allowed!')

                    j += 1

                i += 1

        return True

    def set_cell_value(self, i, j, v):
        if self.state[i][j][0] == v:
            return
        elif self.state[i][j][0] is not None or v not in self.state[i][j][1]:
            return False

        self.state[i][j][0] = v
        self.state[i][j][1] = set()
        self.state[i][j][2] = True
        self.unknown_cnt -= 1

        for k in range(self.n2):
            self.state[i][k][1].discard(v)
            self.state[k][j][1].discard(v)

        i0 = i - (i % self.n)
        j0 = j - (j % self.n)
        for di in range(self.n):
            for dj in range(self.n):
                self.state[i0 + di][j0 + dj][1].discard(v)

        return True

    def actualize_over_set(self, lst):
        unsolved = self.digits.copy()
        stats = [[0, None] for _ in range(self.n2 + 1)]

        for i, j in lst:
            w = self.state[i][j][0]
            if w is not None:
                if w not in unsolved:
                    return False
                unsolved.remove(w)
            else:
                for v in self.state[i][j][1]:
                    stats[v][0] += 1
                    stats[v][1] = [i, j]

        for v, s in enumerate(stats):
            if s[0] == 1:
                i, j = s[1]
                self.set_cell_value(i, j, v)

        return True

    def actualize_state(self):
        for i in range(self.n2):
            for j in range(self.n2):
                if len(self.state[i][j][1]) == 1:
                    if not self.set_cell_value(i, j, next(iter(self.state[i][j][1]))):
                        return False
                if self.state[i][j][0] is None and len(self.state[i][j][1]) == 0:
                    return False

        for i in range(self.n2):
            if not self.actualize_over_set([[i, j] for j in range(self.n2)]) or \
               not self.actualize_over_set([[j, i] for j in range(self.n2)]):
                return False

        for i0 in range(0, self.n2, self.n):
            for j0 in range(0, self.n2, self.n):
                lst = []
                for di in range(self.n):
                    for dj in range(self.n):
                       lst.append([i0 + di, j0 + dj])
                if not self.actualize_over_set(lst):
                    return False

        return True

    def discard_new_cell_values(self):
        for i in range(self.n2):
            for j in range(self.n2):
                self.state[i][j][2] = False

    def solve(self):
        unknown_cnt = self.unknown_cnt
        while unknown_cnt > 0:
            if not self.actualize_state():
                return SolutionStatus.ERROR

            if self.v:
                self.print()

            if unknown_cnt == self.unknown_cnt:
                return SolutionStatus.STUCKED

            unknown_cnt = self.unknown_cnt

        return SolutionStatus.SUCCESSFUL
