import random

import pytest

from sudoku.generator import CLUES, generate
from sudoku.solver import count_solutions, solve
from sudoku.validator import conflicts, is_complete


@pytest.mark.parametrize("diff", list(CLUES))
def test_generate_unique_and_valid(diff):
    puzzle, solution = generate(diff, random.Random(1))
    assert is_complete(solution)
    assert count_solutions(puzzle, 2) == 1
    assert solve(puzzle) == solution
    assert all(p == 0 or p == s for p, s in zip(puzzle, solution))


def test_conflicts():
    b = [0] * 81
    b[0] = b[1] = 5
    assert conflicts(b) == {0, 1}
    b[1] = 0
    b[72] = 5  # same column
    assert conflicts(b) == {0, 72}


def test_unsolvable():
    b = [0] * 81
    b[0] = b[1] = 5
    assert solve(b) is None
    assert count_solutions(b) == 0


def test_empty_has_multiple():
    assert count_solutions([0] * 81, 2) == 2
