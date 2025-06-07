# 🕹️ StockfishGPT (Legacy – Streamlit Version)

**Status:** 📦 Archived  
**Project Type:** Experimental Prototype  
**Frontend:** Streamlit  
**Backend:** Python + Stockfish + OpenAI GPT

---

## 🔍 Overview

**StockfishGPT** was an early experimental interface combining the **Stockfish chess engine** with **OpenAI's GPT** to create a hybrid chess analysis assistant. The app allowed users to:

- Input chess moves or FEN strings
- Receive tactical analysis from Stockfish
- Generate natural language insights with GPT
- Experiment with blended AI + chess logic in real-time

This version used **Streamlit** as the UI layer and was hosted locally or via temporary online deployments.

---

## 📁 Project Structure

- `streamlit_app.py` – Main UI logic
- `stockfish/` – Contains the Stockfish engine binary
- `.streamlit/secrets.toml` – Handled OpenAI API key (now scrubbed from history)
- `README.md`, `.gitignore`, and other configs

---

## 🔐 Important Notes

- **All API keys and secrets** have been removed from commit history.
- `.gitignore` now protects all sensitive files (`.env`, `.streamlit/secrets.toml`, etc.).
- This repo **no longer contains any private or active keys**.

---

## 🚧 Why Archived?

This Streamlit-based prototype was part of our **Attempt 1** development cycle. We've since:

- ✅ Cleaned up commit history
- ✅ Synced and secured GitHub
- ✅ Moved on to a more robust, standalone implementation (Attempt 2)

This repo is being **archived** for reference and historical tracking only.

---

## 📦 What's Next?

We're now building a more stable and feature-rich version of StockfishGPT using a new architecture (Attempt 2), possibly on platforms like **Replit** or with a custom frontend.

Stay tuned for updates in our new repo!

---



