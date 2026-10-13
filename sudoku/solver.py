"""Backtracking Sudoku solver using bitmasks and the MRV heuristic.

A board is a list of 81 ints (0 = empty).
"""
import random

FULL = 0x1FF  # bits 0..8 represent digits 1..9


def _box(i):
    return (i // 27) * 3 + (i % 9) // 3


def _init_masks(board):
    rows, cols, boxes = [0] * 9, [0] * 9, [0] * 9
    for i, v in enumerate(board):
        if v:
            bit = 1 << (v - 1)
            r, c, b = i // 9, i % 9, _box(i)
            if (rows[r] | cols[c] | boxes[b]) & bit:
                return None  # initial conflict
            rows[r] |= bit
            cols[c] |= bit
            boxes[b] |= bit
    return rows, cols, boxes


def _pick(board, masks):
    rows, cols, boxes = masks
    best, best_cands, best_n = -1, 0, 10
    for i in range(81):
        if board[i] == 0:
            cands = FULL & ~(rows[i // 9] | cols[i % 9] | boxes[_box(i)])
            n = bin(cands).count("1")
            if n < best_n:
                best, best_cands, best_n = i, cands, n
                if n <= 1:
                    break
    return best, best_cands, best_n


def _search(board, masks, limit, count, rng, keep):
    """Backtrack; stops when `count` reaches `limit`.

    If keep is True the first solution is left in `board`.
    """
    rows, cols, boxes = masks
    best, cands, n = _pick(board, masks)
    if best == -1:
        count[0] += 1
        return
    digits = [d for d in range(1, 10) if cands >> (d - 1) & 1]
    if rng:
        rng.shuffle(digits)
    r, c, b = best // 9, best % 9, _box(best)
    for d in digits:
        bit = 1 << (d - 1)
        board[best] = d
        rows[r] |= bit
        cols[c] |= bit
        boxes[b] |= bit
        _search(board, masks, limit, count, rng, keep)
        if keep and count[0] >= limit:
            return
        board[best] = 0
        rows[r] &= ~bit
        cols[c] &= ~bit
        boxes[b] &= ~bit
        if count[0] >= limit:
            return


def solve(board, randomize=False, rng=None):
    """Return a solved copy of board, or None if unsolvable."""
    b = list(board)
    masks = _init_masks(b)
    if masks is None:
        return None
    count = [0]
    _search(b, masks, 1, count, (rng or random) if randomize else None, True)
    return b if count[0] else None


def count_solutions(board, limit=2):
    """Count solutions, stopping at `limit`."""
    b = list(board)
    masks = _init_masks(b)
    if masks is None:
        return 0
    count = [0]
    _search(b, masks, limit, count, None, False)
    return count[0]
