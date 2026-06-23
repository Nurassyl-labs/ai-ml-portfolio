from __future__ import annotations

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, JSONResponse
from PIL import Image
from pathlib import Path
import io
import os
import json
import base64
import numpy as np
import requests

from .image_ops import stylize
from .sam_service import SAMService
from .mask_refine import RefineParams, refine_mask, decontaminate_rgb

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------- Configure SAM here ----------
# Default checkpoint path:
# backend/checkpoints/sam_vit_b_01ec64.pth
_BACKEND_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_SAM_CHECKPOINT = _BACKEND_ROOT / "checkpoints" / "sam_vit_b_01ec64.pth"

SAM_CHECKPOINT = Path(os.environ.get("SAM_CHECKPOINT", str(_DEFAULT_SAM_CHECKPOINT)))
SAM_MODEL_TYPE = os.environ.get("SAM_MODEL_TYPE", "vit_b")

sam_service: SAMService | None = None


def _parse_refine(refine_json: str | None) -> RefineParams:
    if not refine_json:
        return RefineParams()
    try:
        d = json.loads(refine_json)
        if not isinstance(d, dict):
            return RefineParams()
        return RefineParams(
            expand=int(d.get("expand", 0) or 0),
            smooth=int(d.get("smooth", 0) or 0),
            feather=int(d.get("feather", 0) or 0),
            fill_holes=bool(d.get("fill_holes", True)),
            remove_islands_min_area=int(d.get("remove_islands_min_area", 0) or 0),
            decontam=bool(d.get("decontam", False)),
            decontam_threshold=int(d.get("decontam_threshold", 220) or 220),
            decontam_radius=int(d.get("decontam_radius", 3) or 3),
        )
    except Exception:
        return RefineParams()


def _cutout_with_refine(pil: Image.Image, mask_u8: np.ndarray, p: RefineParams) -> Image.Image:
    alpha = refine_mask(mask_u8, p)
    rgba = np.array(pil.convert("RGBA"), dtype=np.uint8)
    rgb = rgba[..., :3]
    if p.decontam:
        rgb = decontaminate_rgb(
            rgb, alpha, threshold=p.decontam_threshold, radius=p.decontam_radius
        )
    out = np.dstack([rgb, alpha.astype(np.uint8)]).astype(np.uint8)
    # Clear RGB for fully transparent pixels
    transparent = out[..., 3] == 0
    out[transparent, 0] = 0
    out[transparent, 1] = 0
    out[transparent, 2] = 0
    return Image.fromarray(out, mode="RGBA")


def _encode_png_b64(pil: Image.Image) -> str:
    buf = io.BytesIO()
    pil.save(buf, format="PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def _data_url_from_bytes(content: bytes, mime: str) -> str:
    b64 = base64.b64encode(content).decode("ascii")
    return f"data:{mime};base64,{b64}"


def _decode_openrouter_image_data_url(data_url: str) -> tuple[bytes, str]:
    # data:image/png;base64,....
    if not data_url.startswith("data:") or ";base64," not in data_url:
        raise ValueError("OpenRouter returned an unexpected image URL format.")
    meta, b64 = data_url.split(",", 1)
    mime = meta.split(";", 1)[0].replace("data:", "").strip() or "image/png"
    return base64.b64decode(b64), mime


@app.on_event("startup")
def _startup():
    """
    Safe startup: do not crash if SAM checkpoint is missing or invalid.
    """
    global sam_service
    try:
        if SAM_CHECKPOINT.exists():
            sam_service = SAMService(checkpoint_path=str(SAM_CHECKPOINT), model_type=SAM_MODEL_TYPE)
            print("[SAM] loaded")
        else:
            sam_service = None
            print(f"[SAM] checkpoint not found: {SAM_CHECKPOINT} (magic disabled)")
    except Exception as e:
        sam_service = None
        print(f"[SAM] failed to load: {e} (magic disabled)")


@app.get("/health")
def health():
    return {"ok": True, "sam_loaded": sam_service is not None}


@app.post("/api/stylize")
async def stylize_api(
    image: UploadFile = File(...),
    params: str = Form(...),
):
    """
    Apply simple stylization to an element image.
    Expects:
      - image: PNG/JPG
      - params: JSON string {preset, sat, bri}
    Returns: PNG
    """
    p = json.loads(params)
    raw = await image.read()
    img = Image.open(io.BytesIO(raw)).convert("RGBA")

    out = stylize(
        img=img,
        preset=str(p.get("preset", "none")),
        sat=float(p.get("sat", 1.0)),
        bri=float(p.get("bri", 1.0)),
    )

    buf = io.BytesIO()
    out.save(buf, format="PNG", optimize=True)
    return Response(buf.getvalue(), media_type="image/png")


@app.post("/api/magic_select")
async def magic_select_api(
    image: UploadFile = File(...),
    click_x: int = Form(...),
    click_y: int = Form(...),
    refine: str | None = Form(None),
):
    """
    Magic select by a single foreground click.
    Returns RGBA cutout PNG.
    """
    if sam_service is None:
        return JSONResponse(status_code=503, content={"error": "SAM is not loaded."})

    raw = await image.read()
    pil = Image.open(io.BytesIO(raw)).convert("RGBA")

    mask = sam_service.predict_mask_from_point(
        pil, (int(click_x), int(click_y)), point_label=1, multimask=True
    )
    p = _parse_refine(refine)
    cutout = _cutout_with_refine(pil, mask, p)

    buf = io.BytesIO()
    cutout.save(buf, format="PNG", optimize=True)
    return Response(buf.getvalue(), media_type="image/png")


@app.post("/api/magic_select_candidates")
async def magic_select_candidates_api(
    image: UploadFile = File(...),
    click_x: int = Form(...),
    click_y: int = Form(...),
    refine: str | None = Form(None),
):
    """
    Magic select (SAM click) with multi-mask candidates.
    Returns JSON: {candidates:[{score,png_b64},...]} where png is an RGBA cutout.
    """
    if sam_service is None:
        return JSONResponse(status_code=503, content={"error": "SAM is not loaded."})

    raw = await image.read()
    pil = Image.open(io.BytesIO(raw)).convert("RGBA")
    p = _parse_refine(refine)

    masks, scores = sam_service.predict_masks_from_point(
        pil, (int(click_x), int(click_y)), point_label=1, multimask=True
    )

    # Sort by score desc, keep top 3
    idxs = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:3]
    candidates = []
    for i in idxs:
        cutout = _cutout_with_refine(pil, masks[i], p)
        candidates.append({"score": float(scores[i]), "png_b64": _encode_png_b64(cutout)})
    return {"candidates": candidates}


@app.post("/api/magic_brush")
async def magic_brush_api(
    image: UploadFile = File(...),
    points: str = Form(...),
    refine: str | None = Form(None),
):
    """
    Magic brush: multi-point SAM prompt.
    points JSON:
      {"pos":[[x,y],[x,y],...], "neg":[[x,y],...]}
    Returns RGBA cutout PNG.
    """
    if sam_service is None:
        return JSONResponse(status_code=503, content={"error": "SAM is not loaded."})

    raw = await image.read()
    pil = Image.open(io.BytesIO(raw)).convert("RGBA")

    data = json.loads(points)
    pos = data.get("pos", [])
    neg = data.get("neg", [])

    if not pos or len(pos) < 2:
        return JSONResponse(
            status_code=422, content={"error": "Need at least 2 positive brush points."}
        )

    pts: list[tuple[int, int]] = []
    labels: list[int] = []

    for x, y in pos:
        pts.append((int(x), int(y)))
        labels.append(1)

    for x, y in neg:
        pts.append((int(x), int(y)))
        labels.append(0)

    mask = sam_service.predict_mask_from_points(pil, pts, labels, multimask=True)
    p = _parse_refine(refine)
    cutout = _cutout_with_refine(pil, mask, p)

    buf = io.BytesIO()
    cutout.save(buf, format="PNG", optimize=True)
    return Response(buf.getvalue(), media_type="image/png")


@app.post("/api/magic_brush_candidates")
async def magic_brush_candidates_api(
    image: UploadFile = File(...),
    points: str = Form(...),
    refine: str | None = Form(None),
):
    """
    Magic brush (multi-point SAM prompt) with multi-mask candidates.
    Returns JSON: {candidates:[{score,png_b64},...]} where png is an RGBA cutout.
    """
    if sam_service is None:
        return JSONResponse(status_code=503, content={"error": "SAM is not loaded."})

    raw = await image.read()
    pil = Image.open(io.BytesIO(raw)).convert("RGBA")
    p = _parse_refine(refine)

    data = json.loads(points)
    pos = data.get("pos", [])
    neg = data.get("neg", [])

    if not pos or len(pos) < 2:
        return JSONResponse(
            status_code=422, content={"error": "Need at least 2 positive brush points."}
        )

    pts: list[tuple[int, int]] = []
    labels: list[int] = []

    for x, y in pos:
        pts.append((int(x), int(y)))
        labels.append(1)

    for x, y in neg:
        pts.append((int(x), int(y)))
        labels.append(0)

    masks, scores = sam_service.predict_masks_from_points(pil, pts, labels, multimask=True)

    idxs = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:3]
    candidates = []
    for i in idxs:
        cutout = _cutout_with_refine(pil, masks[i], p)
        candidates.append({"score": float(scores[i]), "png_b64": _encode_png_b64(cutout)})
    return {"candidates": candidates}


@app.post("/api/ai_refine_final")
async def ai_refine_final_api(
    image: UploadFile = File(...),
    user_text: str = Form(""),
):
    """
    Refine the final exported composition using OpenRouter image-capable chat models.
    Accepts a PNG/JPG input and returns an edited image (usually PNG).
    """
    print(image)

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        return JSONResponse(
            status_code=500,
            content={"error": "OPENROUTER_API_KEY is not set on the backend."},
        )

    model = os.environ.get("OPENROUTER_MODEL", "google/gemini-3-pro-image-preview")
    referer = os.environ.get("OPENROUTER_HTTP_REFERER")
    title = os.environ.get("OPENROUTER_X_TITLE")

    raw = await image.read()
    mime = image.content_type or "image/png"
    if mime not in ("image/png", "image/jpeg", "image/jpg", "image/webp"):
        # Still allow, but many models expect png/jpg; fall back to png mime for data url.
        mime = "image/png"

    prompt = (
        "Edit the provided image."
        # "You are a professional sticker/layout editor. "
        # "Edit the provided image according to the request, but keep the main subjects and composition consistent "
        # "unless explicitly asked. Produce a clean, high-quality result suitable for stickers. "
        # "If adding text, make it cute and well placed, and ensure it is readable."
    )
    extra = (user_text or "").strip()
    if extra:
        prompt = prompt + "\n\nUser request: " + extra
    else:
        prompt = (
            prompt
            + "\n\nUser request: Make it a bit cuter and more polished, but do not change layout."
        )

    payload = {
        "model": model,
        "modalities": ["image", "text"],
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": _data_url_from_bytes(raw, mime)}},
                ],
            }
        ],
    }

    print(payload)

    headers: dict[str, str] = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    if referer:
        headers["HTTP-Referer"] = referer
    if title:
        headers["X-Title"] = title

    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=120,
        )
    except Exception as e:
        return JSONResponse(status_code=502, content={"error": f"OpenRouter request failed: {e}"})

    if not r.ok:
        return JSONResponse(
            status_code=502,
            content={"error": "OpenRouter error", "status": r.status_code, "detail": r.text},
        )

    out = r.json()
    try:
        img0 = out["choices"][0]["message"]["images"][0]
        url_obj = img0.get("image_url") or img0.get("imageUrl")
        data_url = url_obj["url"]
        img_bytes, out_mime = _decode_openrouter_image_data_url(data_url)
    except Exception as e:
        return JSONResponse(
            status_code=502, content={"error": f"Failed to parse OpenRouter response: {e}"}
        )

    return Response(img_bytes, media_type=out_mime)
