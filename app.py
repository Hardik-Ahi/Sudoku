import time

import streamlit as st

from sudoku.generator import CLUES, generate
from sudoku.validator import conflicts, is_complete

st.set_page_config(page_title="Sudoku", page_icon="🔢", layout="wide")


def new_game(difficulty):
    puzzle, solution = generate(difficulty)
    st.session_state.update(
        puzzle=puzzle,
        solution=solution,
        board=list(puzzle),
        selected=None,
        message="",
        start=time.time(),
        difficulty=difficulty,
        solved_shown=False,
    )


if "board" not in st.session_state:
    new_game("Medium")

S = st.session_state
puzzle, solution, board = S.puzzle, S.solution, S.board
bad = conflicts(board)
won = is_complete(board)


def select(i):
    S.selected = i
    S.message = ""


def enter(v):
    i = S.selected
    if i is None:
        st.toast("Select a cell first.", icon="⚠️")
    elif puzzle[i]:
        st.toast("That cell is a given.", icon="⚠️")
    else:
        board[i] = v


def reset():
    S.board = list(S.puzzle)
    S.selected = None
    S.message = ""
    S.solved_shown = False


def check():
    wrong = [i for i in range(81) if board[i] and board[i] != solution[i]]
    if wrong:
        S.message = f"❌ {len(wrong)} cell(s) don't match the solution."
        S.selected = wrong[0]
    else:
        S.message = "✅ So far so good!"


def hint():
    empties = [i for i in range(81) if board[i] != solution[i]]
    if not empties:
        return
    i = S.selected if S.selected in empties and not puzzle[S.selected] else empties[0]
    board[i] = solution[i]
    S.selected = i
    S.message = "💡 Hint revealed."


def show_solution():
    S.board = list(solution)
    S.solved_shown = True


# --- styling ---------------------------------------------------------------
css = """
.st-key-grid, .st-key-pad{max-width:640px;margin:0 auto;}
.st-key-grid [data-testid="stHorizontalBlock"]{flex-wrap:nowrap !important;gap:3px !important;}
.st-key-grid [data-testid="stColumn"]{min-width:0 !important;}
.st-key-grid button{width:100%;min-height:3.4rem;aspect-ratio:1/1;padding:0;border-radius:4px;
  border:1.5px solid #4b5563;background:#FFFFFF;color:#1D4ED8;}
.st-key-grid button p{font-size:1.9rem;line-height:1;color:inherit;}
.st-key-pad [data-testid="stHorizontalBlock"]{flex-wrap:nowrap !important;gap:4px !important;}
.st-key-pad [data-testid="stColumn"]{min-width:0 !important;}
.st-key-pad button{min-height:3rem;}
.st-key-pad button p{font-size:1.5rem;}
"""


def tile(i, bg, fg, weight):
    return (
        f".st-key-c{i} button{{background:{bg} !important;color:{fg} !important;"
        f"font-weight:{weight} !important;}}\n"
        f".st-key-c{i} button p{{color:{fg} !important;font-weight:{weight} !important;}}\n"
    )


for i in range(81):
    r, c = divmod(i, 9)
    if i in bad:
        css += tile(i, "#B00020", "#FFFFFF", 800)
    elif S.selected == i:
        css += tile(i, "#FFD54A", "#000000", 800)
    elif puzzle[i]:
        css += tile(i, "#DCE6F5", "#0A1F44", 800)
    else:
        css += tile(i, "#FFFFFF", "#1D4ED8", 700)
    if S.selected == i:
        css += f".st-key-c{i} button{{border:3px solid #000000 !important;}}\n"
    margins = ""
    if c in (2, 5):
        margins += "margin-right:8px;"
    if r in (2, 5):
        margins += "margin-bottom:8px;"
    if margins:
        css += f".st-key-c{i} button{{{margins}}}\n"
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# --- sidebar ---------------------------------------------------------------
with st.sidebar:
    st.header("New game")
    diff = st.selectbox(
        "Difficulty", list(CLUES), index=list(CLUES).index(S.difficulty)
    )
    if st.button("New Game", use_container_width=True, type="primary"):
        new_game(diff)
        st.rerun()
    st.divider()
    st.button("Check", on_click=check, use_container_width=True)
    st.button("Hint", on_click=hint, use_container_width=True)
    st.button("Reset", on_click=reset, use_container_width=True)
    st.button("Show solution", on_click=show_solution, use_container_width=True)

# --- main ------------------------------------------------------------------
st.title("🔢 Sudoku")
st.caption(f"Difficulty: {S.difficulty} · Clues: {sum(1 for v in puzzle if v)}")

if won and not S.solved_shown:
    st.balloons()
    st.success(f"🎉 Solved in {int(time.time() - S.start) // 60} min "
               f"{int(time.time() - S.start) % 60} s!")
elif S.message:
    st.info(S.message)

with st.container(key="grid"):
    for r in range(9):
        cols = st.columns(9)
        for c in range(9):
            i = r * 9 + c
            with cols[c]:
                st.button(
                    str(board[i]) if board[i] else " ",
                    key=f"c{i}",
                    on_click=select,
                    args=(i,),
                    type="primary" if S.selected == i else "secondary",
                )

with st.container(key="pad"):
    cols = st.columns(10)
    for v in range(1, 10):
        cols[v - 1].button(str(v), key=f"p{v}", on_click=enter, args=(v,),
                           use_container_width=True)
    cols[9].button("⌫", key="p0", on_click=enter, args=(0,),
                   use_container_width=True)
