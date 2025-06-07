import streamlit as st
import chess.pgn
import chess.engine
from io import StringIO
import openai
import os
import tempfile
from stockfish import Stockfish

# === LOAD API KEY FROM STREAMLIT SECRETS ===
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# === PATH TO STOCKFISH ===
STOCKFISH_PATH = "./stockfish/stockfish"

# === CONFIG ===
EVAL_THRESHOLD_CP = 100  # Centipawn loss threshold to flag mistakes
STOCKFISH_DEPTH = 15

# === SET PAGE ===
st.set_page_config(page_title="StockfishGPT", layout="wide")
st.title("♟️ StockfishGPT — Chess Game Analyzer with GPT Commentary")

# === FILE UPLOAD ===
uploaded_file = st.file_uploader("Upload your PGN file", type=["pgn"])

def run_stockfish_on_position(fen):
    stockfish = Stockfish(STOCKFISH_PATH, depth=STOCKFISH_DEPTH)
    stockfish.set_fen_position(fen)
    evaluation = stockfish.get_evaluation()
    best_move = stockfish.get_best_move()
    return evaluation, best_move

def format_move_info(move_num, move, evaluation, best_move):
    eval_value = evaluation.get("value", "N/A")
    eval_type = evaluation.get("type", "cp")
    eval_str = f"{eval_value} ({eval_type})"
    return {
        "move_number": move_num,
        "move": move.uci(),
        "evaluation": eval_str,
        "best_move": best_move
    }

def analyze_game(pgn_text):
    game = chess.pgn.read_game(StringIO(pgn_text))
    board = game.board()

    analysis = []
    previous_eval = None
    move_number = 1

    for move in game.mainline_moves():
        board.push(move)
        fen = board.fen()
        evaluation, best_move = run_stockfish_on_position(fen)

        current_cp = evaluation.get("value")
        current_type = evaluation.get("type")

        if current_type == "mate":
            move_number += 1
            continue

        if previous_eval is not None:
            cp_loss = previous_eval - current_cp
            if cp_loss >= EVAL_THRESHOLD_CP:
                move_info = format_move_info(move_number, move, evaluation, best_move)
                analysis.append(move_info)

        previous_eval = current_cp
        move_number += 1

    return analysis

def generate_commentary(move_info, pgn_text):
    move_num = move_info["move_number"]
    played = move_info["move"]
    best = move_info["best_move"]
    eval_info = move_info["evaluation"]

    prompt = f"""
You are a chess coach.

A player played the move {played} on move {move_num}, but Stockfish suggests {best} would have been better.

The evaluation for the move was: {eval_info}.

The PGN of the full game is:

{pgn_text}

Explain to a 1400-rated player why this move was inaccurate, and what the better move would have done. Be clear, concise, and instructional.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=300,
    )

    return response.choices[0].message.content.strip()

# === MAIN APP LOGIC ===
if uploaded_file:
    pgn_text = uploaded_file.read().decode("utf-8")

    with st.spinner("Analyzing game with Stockfish..."):
        mistakes = analyze_game(pgn_text)

    st.subheader("🔍 Mistakes / Inaccuracies Found")
    if not mistakes:
        st.success("No major inaccuracies detected based on current threshold.")
    else:
        for move_info in mistakes:
            with st.expander(f"Move {move_info['move_number']}: {move_info['move']} → Suggested: {move_info['best_move']}"):
                st.write(f"**Evaluation:** {move_info['evaluation']}")
                with st.spinner("Generating commentary..."):
                    comment = generate_commentary(move_info, pgn_text)
                    st.markdown(comment)
