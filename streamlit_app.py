# streamlit_app.py

import streamlit as st
import chess.pgn
import openai
import os
import time
import json
from io import StringIO
from stockfish import Stockfish
import streamlit.components.v1 as components
import chess

client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# === CONFIG ===
STOCKFISH_PATH = "./stockfish/stockfish"
STOCKFISH_DEPTH = 15
EVAL_THRESHOLD_CP = 100
GPT_MODEL = "gpt-4o"

st.set_page_config(page_title="♟️ StockfishGPT v1.10", layout="wide")
st.title("♟️ StockfishGPT — Chess Game Analyzer with GPT Commentary")
uploaded_file = st.file_uploader("📄 Upload a PGN File", type=["pgn"])

def render_chessboard_with_pgn(pgn_text):
    import json
    import streamlit.components.v1 as components

    with open("components/chessboard.html", "r") as file:
        html_template = file.read()

    safe_pgn = json.dumps(pgn_text.replace("\n", " "))
    html_filled = html_template.replace('"__PGN_PLACEHOLDER__"', safe_pgn)
    components.html(html_filled, height=550)

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

def build_piece_map(board):
    piece_map = board.piece_map()
    summary = {"White": {}, "Black": {}}
    for square, piece in piece_map.items():
        color = "White" if piece.color == chess.WHITE else "Black"
        piece_type = piece.symbol().upper() if piece.color == chess.WHITE else piece.symbol().lower()
        square_name = chess.square_name(square)
        summary[color].setdefault(piece_type, []).append(square_name)
    return summary

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
                move_info["piece_map"] = build_piece_map(board)
                move_info["turn"] = "White" if board.turn else "Black"
                move_info["last_move"] = move.uci()
                analysis.append(move_info)

        previous_cp = current_cp
        move_number += 1

    return analysis, game

def generate_commentary(move_info, retries=3):
    piece_map = move_info["piece_map"]
    piece_text = "\n".join(
        [f"{color} Pieces:\n" + "\n".join(
            [f"- {piece}: {', '.join(squares)}" for piece, squares in piece_map[color].items()]
        ) for color in piece_map]
    )

    prompt = f"""
You are a chess coach analyzing a single move in the middle of a game. Your goal is to clearly explain the position to a 1400-rated player. Only use information provided.

FEN before the move: {move_info['fen']}
Move played: {move_info['move']}  (by {move_info['turn']})
Best move suggested by Stockfish: {move_info['best_move']}
Stockfish evaluation after the played move: {move_info['evaluation']}
Last move played: {move_info['last_move']}

Full piece map:
{piece_text}

Instructions:
- Don't assume which side is winning.
- Only talk about what is visible from this board state.
- Do NOT invent ideas unless they are grounded in this FEN or move.
- Be extremely accurate when identifying which side played the move.

Structure your answer:
1. ✅ What move was played and by whom
2. ❌ Why it may be inaccurate
3. 💡 What Stockfish suggests instead and why it’s stronger
4. 🧠 Key learning tip based on this mistake
"""

    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=GPT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=400,
            )
            return response.choices[0].message.content.strip()
        except openai.RateLimitError:
            time.sleep(2 ** attempt)

    return "⚠️ GPT failed after retries."

def generate_game_summary(game):
    pgn_data = str(game)
    summary_prompt = f"""
You are a chess coach reviewing a student's full game.

PGN:
{pgn_data}

Summarize in 3–5 sentences:
- General plan
- When things turned
- Tips to improve

Avoid tactical lines. Be strategic and human-readable.
"""
    response = client.chat.completions.create(
        model=GPT_MODEL,
        messages=[{"role": "user", "content": summary_prompt}],
        temperature=0.7,
        max_tokens=300,
    )
    return response.choices[0].message.content.strip()

# === MAIN ===

st.subheader("♟️ Full Game Viewer")

if uploaded_file:
    pgn_text = uploaded_file.read().decode("utf-8")

    with st.spinner("🔍 Analyzing game..."):
        mistakes, game_obj = analyze_game(pgn_text)

    render_chessboard_with_pgn(pgn_text)

    st.subheader("⚠️ Mistakes & Inaccuracies")
    if not mistakes:
        st.success("✅ No major mistakes detected.")
    else:
        for move_info in mistakes:
            with st.expander(f"Move {move_info['move_number']}: {move_info['move']} → Best: {move_info['best_move']}"):
                st.markdown(f"**Eval:** {move_info['evaluation']}")
                with st.spinner("💬 GPT analyzing move..."):
                    comment = generate_commentary(move_info)
                    st.markdown(comment)

    st.subheader("📋 Game Summary")
    with st.spinner("🧠 Generating strategic summary..."):
        game_summary = generate_game_summary(game_obj)
        st.markdown(game_summary)

else:
    st.info("👈 Upload a PGN file to analyze a game.")
    render_chessboard_with_pgn("[Event \"Default Board\"]\n1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 *")
