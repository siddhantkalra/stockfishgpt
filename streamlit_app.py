import streamlit as st
import chess.pgn
import openai
import os
import time
from io import StringIO
from stockfish import Stockfish

# === OPENAI INIT ===
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# === CONFIG ===
STOCKFISH_PATH = "./stockfish/stockfish"
STOCKFISH_DEPTH = 15
EVAL_THRESHOLD_CP = 100
GPT_MODEL = "gpt-4o"

# === STREAMLIT UI ===
st.set_page_config(page_title="♟️ StockfishGPT v1.8", layout="wide")
st.title("♟️ StockfishGPT — Chess Game Analyzer with GPT Commentary")

uploaded_file = st.file_uploader("📄 Upload a PGN File", type=["pgn"])

# === STOCKFISH EVAL ===
def run_stockfish_on_position(fen):
    stockfish = Stockfish(STOCKFISH_PATH, depth=STOCKFISH_DEPTH)
    stockfish.set_fen_position(fen)
    evaluation = stockfish.get_evaluation()
    best_move = stockfish.get_best_move()
    return evaluation, best_move

def format_move_info(move_num, move, evaluation, best_move, fen):
    eval_value = evaluation.get("value", "N/A")
    eval_type = evaluation.get("type", "cp")
    eval_str = f"{eval_value} ({eval_type})"
    return {
        "move_number": move_num,
        "move": move.uci(),
        "evaluation": eval_str,
        "best_move": best_move,
        "fen": fen
    }

def analyze_game(pgn_text):
    game = chess.pgn.read_game(StringIO(pgn_text))
    board = game.board()
    analysis = []
    previous_cp = None
    move_number = 1

    for move in game.mainline_moves():
        board.push(move)
        fen = board.fen()
        evaluation, best_move = run_stockfish_on_position(fen)

        if evaluation.get("type") == "mate":
            move_number += 1
            continue

        current_cp = evaluation.get("value")
        if previous_cp is not None:
            cp_loss = previous_cp - current_cp
            if cp_loss >= EVAL_THRESHOLD_CP:
                move_info = format_move_info(move_number, move, evaluation, best_move, fen)
                analysis.append(move_info)

        previous_cp = current_cp
        move_number += 1

    return analysis, game

# === GPT COMMENTARY (FEN-Based, Fine-Tuned) ===
def generate_commentary(move_info, retries=3):
    prompt = f"""
You are a chess coach helping a 1400-rated player improve their understanding of key mistakes.

Here is the position (FEN): {move_info['fen']}
Move played: {move_info['move']}
Stockfish recommends: {move_info['best_move']}
Evaluation after move: {move_info['evaluation']}

Structure your response with:

- What was played
- Why it’s inaccurate
- What the engine suggests instead
- Why the suggestion is stronger (in terms of control, tactics, or strategy)

Use clear chess language but do not overload the user.
"""

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=GPT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300,
            )
            return response.choices[0].message.content.strip()
        except openai.RateLimitError:
            time.sleep(2 ** attempt)

    return "⚠️ GPT failed after retries."

# === FULL-GAME STRATEGIC SUMMARY ===
def generate_game_summary(game):
    pgn_data = str(game)

    summary_prompt = f"""
You are a chess coach reviewing a student's full game.

Below is the PGN of the game:

{pgn_data}

Provide a concise 3–5 sentence summary focused on:
- Overall strategy (what the player was aiming for)
- Where they lost the advantage
- One or two general suggestions for improvement

Avoid tactical detail, keep it strategic and accessible.
"""

    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=[{"role": "user", "content": summary_prompt}],
        temperature=0.7,
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()

# === STREAMLIT MAIN ===
if uploaded_file:
    pgn_text = uploaded_file.read().decode("utf-8")

    with st.spinner("🔍 Running Stockfish..."):
        mistakes, game_obj = analyze_game(pgn_text)

    st.subheader("♟️ Mistakes & Inaccuracies")
    if not mistakes:
        st.success("✅ No major mistakes detected.")
    else:
        for move_info in mistakes:
            with st.expander(f"Move {move_info['move_number']}: {move_info['move']} → Best: {move_info['best_move']}"):
                st.write(f"**Eval:** {move_info['evaluation']}")

                # ✅ Lichess Board Diagram
                fen_core = move_info["fen"].split(" ")[0].replace("/", "-")
                lichess_url = f"https://lichess.org/analysis/standard/{fen_core}"
                st.markdown(f"[📷 View Board on Lichess]({lichess_url})")

                with st.spinner("💬 GPT generating commentary..."):
                    comment = generate_commentary(move_info)
                    st.markdown(comment)

    # ✅ FULL GAME STRATEGIC SUMMARY
    st.subheader("📋 Game Summary")
    with st.spinner("🧠 Summarizing full game strategy..."):
        game_summary = generate_game_summary(game_obj)
        st.markdown(game_summary)
