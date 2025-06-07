# 📜 StockfishGPT – CHANGELOG

All major changes, additions, and enhancements to the StockfishGPT codebase are tracked here.

---

## v1.0 – Initial Build (June 6, 2025)
- ✅ PGN parser using `python-chess`
- ✅ Integrated Stockfish engine (local binary)
- ✅ Evaluated each move with centipawn deltas
- ✅ Flagged mistakes/blunders (ΔCP > 100)
- ✅ GPT-generated commentary per flagged move
- ✅ Streamlit Cloud deployment (v1.0 MVP)

---

## v1.8 – Stability Update (June 7, 2025)
- ✅ Migrated to OpenAI SDK `v1.x` (`client.chat.completions.create`)
- ✅ Secrets moved to `.streamlit/secrets.toml`
- ✅ GPT rate-limit retry logic
- ✅ FEN-based prompts for accuracy
- ✅ Lichess board embed added (basic HTML)
- ✅ GPT-generated strategic game summary

---

## v1.9 – Commentary Fixes
- ✅ Piece map added for GPT
- ✅ Clear prompt structure enforced
- ✅ hallucination rate reduced
- ✅ Refactored prompt to reference FEN + move + player

---

## v1.10 – Board Fix + Commentary Overhaul (June 8, 2025)
- ✅ HTML board now renders using `chessboard.js`
- ✅ PGN safely passed using `json.dumps()` to escape JS properly
- ✅ Improved GPT prompt accuracy with board state + player turn
- ✅ Full-game GPT summary added
- ✅ Codespaces sync + GitHub push-to-deploy activated

---

## 📌 Upcoming v2.0 – Phase 2
- 🔄 Chess.com + Lichess account integration
- 🔄 Batch analysis across 1000s of games
- 🔄 Trend summary: openings, weaknesses, score charts
- 🔄 PDF / PGN export
- 🔄 Per-move “Explain This” button
