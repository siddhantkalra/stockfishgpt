
import streamlit as st
import chess.pgn
import openai
import tempfile
from stockfish import Stockfish

# Set page config
st.set_page_config(page_title="StockfishGPT", layout="wide")
st.title("♟️ StockfishGPT")
st.markdown("Upload a PGN file and get natural language commentary from GPT based on Stockfish analysis.")

# OpenAI client setup
client = openai.OpenAI()

# Setup Stockfish
stockfish = Stockfish(path="./stockfish/stockfish", depth=15)

# Upload file
uploaded_file = st.file_uploader("Upload a PGN file", type="pgn")

def analyze_game(pgn_text):
    game = chess.pgn.read_game(pgn_text)
    board = game.board()
    comments = []

    for i, move in enumerate(game.mainline_moves(), start=1):
        board.push(move)
        fen = board.fen()
        stockfish.set_fen_position(fen)
        eval_info = stockfish.get_evaluation()

        if eval_info["type"] == "cp" and abs(eval_info["value"]) > 80:
            comment_prompt = f"This is move {i}. The move just played was {board.peek()}. " \
                             f"Stockfish evaluation is {eval_info}. Please explain this move for a 1400-rated player."
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": comment_prompt}],
                temperature=0.7,
                max_tokens=200
            )
            comment_text = response.choices[0].message.content
            comments.append((i, board.peek().uci(), comment_text))

    return comments

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name

    with open(tmp_file_path, encoding='utf-8') as pgn_file:
        comments = analyze_game(pgn_file)

    for move_num, move, comment in comments:
        st.markdown(f"### Move {move_num}: {move}")
        st.markdown(comment)
