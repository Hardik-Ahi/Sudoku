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


def notify(msg, icon):
    S.setdefault("toasts", []).append((msg, icon))


def select(i):
    S.selected = i


def enter(v):
    i = S.selected
    if i is None:
        notify("Select a cell first.", "⚠️")
    elif puzzle[i]:
        notify("That cell is a given.", "⚠️")
    else:
        board[i] = v


def reset():
    S.board = list(S.puzzle)
    S.selected = None
    S.solved_shown = False


def check():
    wrong = [i for i in range(81) if board[i] and board[i] != solution[i]]
    if wrong:
        notify(f"{len(wrong)} cell(s) don't match the solution.", "❌")
        S.selected = wrong[0]
    else:
        notify("So far so good!", "✅")


def hint():
    empties = [i for i in range(81) if board[i] != solution[i]]
    if not empties:
        return
    i = S.selected if S.selected in empties and not puzzle[S.selected] else empties[0]
    board[i] = solution[i]
    S.selected = i
    notify("Hint revealed.", "💡")


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
.st-key-toasts{display:none;}
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
for r in (2, 5):
    css += f".st-key-row{r}{{margin-bottom:10px;}}\n"
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

# st.toast always lands at the same element path, and the frontend drops a toast
# whose path matches one still on screen. Writing through a container instead
# gives each toast its own path (cycling through 8 slots).
with st.container(key="toasts"):
    for msg, icon in S.pop("toasts", []):
        S.toast_n = S.get("toast_n", 0) + 1
        for _ in range(S.toast_n % 8):
            st.empty()
        st.container().toast(msg, icon=icon)

# --- main ------------------------------------------------------------------
st.title("🔢 Sudoku")
st.caption(f"Difficulty: {S.difficulty} · Clues: {sum(1 for v in puzzle if v)}")

if won and not S.solved_shown:
    st.balloons()
    st.success(f"🎉 Solved in {int(time.time() - S.start) // 60} min "
               f"{int(time.time() - S.start) % 60} s!")

with st.container(key="grid"):
    # Narrow empty spacer columns separate the 3x3 boxes; all 81 cell columns
    # share the same weight so every cell has the same size.
    weights = [1, 1, 1, 0.25, 1, 1, 1, 0.25, 1, 1, 1]
    for r in range(9):
        with st.container(key=f"row{r}"):
            cols = st.columns(weights)
            for c in range(9):
                i = r * 9 + c
                with cols[c + c // 3]:
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

# --- keyboard: digits, backspace/delete, arrows ----------------------------
KEY_JS = """
<script>
const p = window.parent;
if (!p.__sudokuKeys) {
  p.__sudokuKeys = true;
  const s = p.document.createElement('script');
  s.textContent = `
    document.addEventListener('keydown', (e) => {
      const t = e.target;
      if (t && (['INPUT','TEXTAREA','SELECT'].includes(t.tagName) || t.isContentEditable)) return;
      if (e.ctrlKey || e.metaKey || e.altKey) return;
      const click = (sel) => { const b = document.querySelector(sel); if (b) b.click(); };
      if (/^[1-9]$/.test(e.key)) { e.preventDefault(); click('.st-key-p' + e.key + ' button'); }
      else if (['Backspace','Delete','0'].includes(e.key)) { e.preventDefault(); click('.st-key-p0 button'); }
      else if (e.key.startsWith('Arrow')) {
        e.preventDefault();
        const cur = document.querySelector('.st-key-grid button[data-testid="stBaseButton-primary"]');
        const m = cur && cur.closest('[class*="st-key-c"]').className.match(/st-key-c(\\\\d+)/);
        let i = m ? parseInt(m[1], 10) : null;
        if (window.__selAt && Date.now() - window.__selAt < 1500) i = window.__selIdx;
        if (i === null) i = 0;
        else {
          let r = Math.floor(i / 9), c = i % 9;
          if (e.key === 'ArrowUp') r = Math.max(0, r - 1);
          if (e.key === 'ArrowDown') r = Math.min(8, r + 1);
          if (e.key === 'ArrowLeft') c = Math.max(0, c - 1);
          if (e.key === 'ArrowRight') c = Math.min(8, c + 1);
          i = r * 9 + c;
        }
        window.__selIdx = i; window.__selAt = Date.now();
        click('.st-key-c' + i + ' button');
      }
    });`;
  p.document.head.appendChild(s);
}
</script>
"""
st.iframe(KEY_JS, height=1)
