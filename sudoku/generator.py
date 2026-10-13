"""Puzzle generation: random full grid, then dig holes keeping uniqueness."""
import random

from .solver import count_solutions, solve

CLUES = {"Easy": 40, "Medium": 32, "Hard": 27, "Expert": 23}


def full_grid(rng=random):
    board = [0] * 81
    for box in range(3):  # diagonal boxes are independent
        digits = list(range(1, 10))
        rng.shuffle(digits)
        base = box * 30  # first cell of boxes 0, 4, 8
        for k, d in enumerate(digits):
            board[base + (k // 3) * 9 + k % 3] = d
    return solve(board, randomize=True, rng=rng)


def generate(difficulty="Medium", rng=random):
    """Return (puzzle, solution) with a unique solution."""
    target = CLUES[difficulty]
    solution = full_grid(rng)
    puzzle = list(solution)
    cells = list(range(81))
    rng.shuffle(cells)
    clues = 81
    for i in cells:
        if clues <= target:
            break
        saved = puzzle[i]
        puzzle[i] = 0
        if count_solutions(puzzle, 2) != 1:
            puzzle[i] = saved
        else:
            clues -= 1
    return puzzle, solution
