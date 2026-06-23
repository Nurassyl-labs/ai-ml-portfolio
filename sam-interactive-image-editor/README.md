# Interactive Image Segmenter (Meta SAM)

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-backend-009688?logo=fastapi&logoColor=white)
![Model](https://img.shields.io/badge/Meta-Segment%20Anything-0866FF)
![Frontend](https://img.shields.io/badge/Frontend-HTML5%20Canvas-orange)
![License](https://img.shields.io/badge/license-MIT-yellow)

An interactive image segmentation editor powered by Meta's Segment Anything Model (SAM). The project consists of a FastAPI backend wrapping the SAM ViT-B predictor and an intuitive HTML5 Canvas frontend allowing users to upload images, place point prompts, and edit segmentations in real time.

---

## 🚀 Key Features

* **Interactive Point Prompts**: Add foreground (positive) and background (negative) points to guide SAM's mask generation.
* **FastAPI Backend Service**: Interfacing with PyTorch weights using `sam_service.py` to run predictions in milliseconds.
* **Canvas Mask Refinement**: Perform postprocessing refinements (like dilation and erosion ops via `mask_refine.py`) to fine-tune object borders.
* **Vanilla Web UI**: Lightweight HTML5, CSS, and JavaScript implementation, making it easy to run and modify without heavy dependencies.

---

## 🛠️ Tech Stack
* **Backend**: FastAPI, PyTorch, Segment Anything Model (SAM), OpenCV, NumPy, `uv`
* **Frontend**: HTML5 Canvas, Vanilla CSS, Vanilla JavaScript

---

## 📁 Repository Structure
```text
├── src/
│   └── image_process_backend/
│       ├── server.py       # FastAPI application
│       ├── sam_service.py  # Segment Anything model loading and prediction
│       ├── mask_refine.py  # Dilation/erosion postprocessing routines
│       ├── image_ops.py    # Utility image format converters (Base64/OpenCV)
│       └── cli.py          # Command line operations
├── frontend/
│   ├── index.html          # Canvas drawing app layout
│   ├── styles.css          # Clean dark-themed CSS styling
│   └── main.js             # Event listeners for drawing & API requests
├── pyproject.toml          # uv backend dependencies manifest
├── uv.lock                 # Resolved dependencies lockfile
└── README.md
```

---

## ⚙️ Installation & Usage

### 1. Backend Setup (using `uv`)
Ensure you have `uv` installed (fast Python package installer):
```bash
# Install dependencies
uv sync
```

Download Meta's SAM ViT-B checkpoint (approx. 375 MB) and place it under `checkpoints/`:
```bash
mkdir -p checkpoints
wget -O checkpoints/sam_vit_b_01ec64.pth https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth
```

Start the FastAPI backend:
```bash
uv run image-process-backend --reload --port 8001
```

### 2. Frontend Running
To avoid CORS issues, serve the `frontend` directory using any local web server. For instance:
```bash
cd frontend
python -m http.server 8000
```
Open `http://localhost:8000` in your web browser.

---

## 🎨 How to Use
1. **Upload an Image**: Drag-and-drop or select an image to load it onto the canvas.
2. **Left-Click to Add Foreground**: Click on the object you want to segment (adds a blue point).
3. **Right-Click to Add Background**: Click outside the object to exclude sections (adds a red point).
4. **Export Masks**: Download the segmented mask or transparency PNG directly.
