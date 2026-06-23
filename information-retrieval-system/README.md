# RAG Course‑Material Retrieval System

*A Retrieval‑Augmented Generation (RAG) web app that semantically searches course documents using sentence embeddings + FAISS, then generates a grounded answer.*

![Python](https://img.shields.io/badge/Python-Flask-blue)
![FAISS](https://img.shields.io/badge/FAISS-vector%20search-orange)
![SentenceTransformers](https://img.shields.io/badge/Embeddings-MiniLM-green)
![Frontend](https://img.shields.io/badge/Frontend-Vanilla%20JS-yellow)

## Overview

This is a small but complete **RAG pipeline** with a web UI:

1. **Index** — course documents (TXT/PDF) are split into overlapping chunks and embedded with a multilingual SentenceTransformer (`paraphrase-multilingual-MiniLM-L12-v2`, 384‑dim).
2. **Retrieve** — chunks are stored in a **FAISS** index; a user query is embedded and matched by semantic similarity (Top‑K).
3. **Generate** — retrieved chunks become context for an answer. If an LLM API key is configured (DeepSeek / OpenAI / Gemini) it synthesizes the answer; otherwise a clean **template‑based fallback** formats the retrieved evidence — so the app works fully offline.

The UI visualizes the whole pipeline: retrieved sources, chunk previews, document upload, and an adjustable Top‑K.

## Tech Stack

- **Backend:** Flask + Flask‑CORS, SentenceTransformers, FAISS (`IndexFlatL2`), PyMuPDF (optional PDF parsing).
- **Frontend:** vanilla HTML / CSS / JavaScript — single‑page chat interface, no framework.
- **LLM (optional):** DeepSeek / OpenAI / Google Gemini via `.env`.

## Project Structure

```
backend/
  app.py            # Flask app: chunking, embedding, FAISS index, retrieval, answer generation
  requirements.txt  # Python dependencies
  .env.example      # Optional LLM API keys (DEEPSEEK / OPENAI / GEMINI)
  data/             # Indexed course documents
front/
  index.html        # Layout: doc sidebar, chat area, pipeline + retrieved-chunks panel
  app.js            # Upload, query, render, pipeline animation
  style.css         # Styling
```

**Key API endpoints:** `GET /api/status`, `GET /api/documents`, `GET /api/chunks`, `POST /api/upload`, `POST /api/query`.

## How to Run

```bash
cd backend
pip install -r requirements.txt
python app.py          # serves at http://127.0.0.1:5001
```

Open `http://127.0.0.1:5001` in a browser (the Flask app serves the frontend). To enable LLM‑generated answers, copy `.env.example` to `.env` and add an API key — otherwise the offline fallback is used.

## Notes

- Chunking: 350‑character chunks with 50‑character overlap.
- Ships with a few sample course documents so it runs out of the box.
- Built as coursework for an *Information Storage & Retrieval* course.
