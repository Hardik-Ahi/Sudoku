# Sudoku

Streamlit Sudoku with unique-solution puzzles in four difficulties.

## Run
```
pip install -r requirements.txt
streamlit run app.py
```

## Test
```
python -m pytest
```

## How it works
- **Solver** (`sudoku/solver.py`): backtracking with bitmask candidates and the minimum-remaining-values heuristic; also counts solutions (capped) to check uniqueness.
- **Generator** (`sudoku/generator.py`): random full grid (diagonal boxes filled, rest by randomized backtracking), then removes cells in random order while the puzzle keeps exactly one solution, down to a clue target per difficulty.
- **Validator** (`sudoku/validator.py`): duplicate detection in rows/columns/boxes (shown in red) and completion check.
