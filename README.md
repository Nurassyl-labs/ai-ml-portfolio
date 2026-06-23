<h1 align="center">🧠 Nurassyl — AI / ML Project Portfolio</h1>

<p align="center">
  <em>A collection of hands-on projects in deep learning, computer vision, NLP, data science and web development — each one built from scratch, documented, and runnable.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white">
  <img src="https://img.shields.io/badge/PyTorch-deep%20learning-red?logo=pytorch&logoColor=white">
  <img src="https://img.shields.io/badge/OpenCV-computer%20vision-green?logo=opencv&logoColor=white">
  <img src="https://img.shields.io/badge/JavaScript-web-yellow?logo=javascript&logoColor=black">
  <img src="https://img.shields.io/badge/projects-9-blueviolet">
</p>

---

## ⭐ Featured: Autonomous Warehouse Drone — 3D Simulator & AI Inventory Vision

A from-scratch 3D warehouse, rendered headlessly with OpenCV, where a virtual drone flies the aisles and a neural network reads back its **pose** and **how many boxes are in stock**.

<p align="center">
  <a href="https://github.com/Nurassyl-labs/warehouse-drone-simulation">
    <img src="warehouse-drone-simulation/docs/demo.gif" width="80%" alt="Live autonomous warehouse drone scanning dashboard">
  </a>
</p>

<p align="center"><b>→ <a href="https://github.com/Nurassyl-labs/warehouse-drone-simulation">Dedicated repo</a></b></p>

---

## 📂 All Projects

> ⭐ = has its own **dedicated repository** (the strongest projects, broken out for easy starring & reuse). The rest live here in the portfolio.

### 🤖 Deep Learning & Computer Vision

| Project | What it does | Stack |
|---|---|---|
| 🚁 **[Warehouse Drone Simulation](https://github.com/Nurassyl-labs/warehouse-drone-simulation)** ⭐ | 3D warehouse simulator + CNN pose regression & inventory counting | PyTorch · OpenCV · FastAPI |
| 🔬 **[Vision Transformer from Scratch](https://github.com/Nurassyl-labs/vision-transformer-from-scratch)** ⭐ | A clean ViT implementation (patch embed, MHSA, encoder) trained on CIFAR-10 | PyTorch |
| ✂️ **[Interactive Image Segmenter (Meta SAM)](sam-interactive-image-editor/)** | Click-to-segment image editor on top of Segment Anything | FastAPI · SAM · Canvas |

### 📈 NLP, Retrieval & Applied ML

| Project | What it does | Stack |
|---|---|---|
| 📊 **[Stock Movement Prediction with News Sentiment](https://github.com/Nurassyl-labs/stock-sentiment-prediction)** ⭐ | Fuses price, FinBERT sentiment & GloVe embeddings with a stacking ensemble | scikit-learn · PyTorch · Transformers |
| 🔎 **[RAG Course-Material Retrieval](information-retrieval-system/)** | Semantic search over documents (FAISS + embeddings) with grounded answers | Flask · FAISS · SentenceTransformers |

### 📊 Data Science

| Project | What it does | Stack |
|---|---|---|
| 📉 **[Quantitative Analysis — CFPS 2022](quantitative-analysis-cfps/)** | Econometric study of internet use vs life satisfaction (OLS + moderation) | statsmodels · pandas |

### 🌐 Web & Design

| Project | What it does | Stack |
|---|---|---|
| 📚 **[Campus Bookstore — Information Architecture](bookstore-information-architecture/)** | Full IA design + working full-stack prototype (marketplace, forum, book-drifting) | Node/Express · SQLite · Tailwind |
| 🦖 **[Dino Runner Game](dino-game-js/)** | Chrome dinosaur game cloned from scratch — game loop & collisions | Vanilla JS · Canvas |

### 🧮 Fundamentals

| Project | What it does | Stack |
|---|---|---|
| 🧩 **[Data Structures & Algorithms](data-structures-algorithms/)** | ~44 Python solutions: sorting, recursion, stacks, complexity analysis | Python |

---

## 🛠️ Tech Stack Across Projects

**Languages:** Python · JavaScript · HTML/CSS · SQL
**ML / DL:** PyTorch · scikit-learn · Hugging Face Transformers · FAISS
**CV:** OpenCV · Segment Anything (SAM) · ArUco
**Backend:** FastAPI · Flask · Node/Express
**Data:** pandas · NumPy · statsmodels · Matplotlib

## 📁 Repository Layout

Each folder is a **self-contained project** with its own `README.md`, source code and (where useful) result images. Large datasets, model checkpoints and third-party assets are intentionally excluded — every project documents how to regenerate them.

## 📬 Contact

Feel free to open an issue or reach out if anything here is useful to you.

<p align="center"><sub>Built with curiosity. ⭐ Star a project if you find it interesting!</sub></p>
