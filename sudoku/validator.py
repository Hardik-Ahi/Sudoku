"""Conflict detection and completion checks."""


def _groups():
    for r in range(9):
        yield [r * 9 + c for c in range(9)]
    for c in range(9):
        yield [r * 9 + c for r in range(9)]
    for br in range(3):
        for bc in range(3):
            yield [(br * 3 + r) * 9 + bc * 3 + c for r in range(3) for c in range(3)]


def conflicts(board):
    """Set of cell indices whose value duplicates another in row/col/box."""
    bad = set()
    for g in _groups():
        seen = {}
        for i in g:
            if board[i]:
                seen.setdefault(board[i], []).append(i)
        for idxs in seen.values():
            if len(idxs) > 1:
                bad.update(idxs)
    return bad


def is_complete(board):
    return all(board) and not conflicts(board)
