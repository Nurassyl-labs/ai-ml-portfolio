const editor = document.getElementById("editorCanvas");
const ctx = editor.getContext("2d");

const finalCanvas = document.getElementById("finalCanvas");
const fctx = finalCanvas.getContext("2d");

const fileInput = document.getElementById("fileInput");
const setBgBtn = document.getElementById("setBgBtn");
const clearCropBtn = document.getElementById("clearCropBtn");

const selectMode = document.getElementById("selectMode");
const addBtn = document.getElementById("addBtn");
const magicAddBtn = document.getElementById("magicAddBtn");

const activeSelect = document.getElementById("activeSelect");
const toFrontBtn = document.getElementById("toFrontBtn");
const toBackBtn = document.getElementById("toBackBtn");
const deleteBtn = document.getElementById("deleteBtn");

const scaleRange = document.getElementById("scaleRange");
const scaleVal = document.getElementById("scaleVal");
const rotRange = document.getElementById("rotRange");
const rotVal = document.getElementById("rotVal");

const preset = document.getElementById("preset");
const sat = document.getElementById("sat");
const bri = document.getElementById("bri");
const applyBtn = document.getElementById("applyBtn");

// Layout / layers
const lockEnable = document.getElementById("lockEnable");
const blendMode = document.getElementById("blendMode");
const opacity = document.getElementById("opacity");
const opacityVal = document.getElementById("opacityVal");

const groupBtn = document.getElementById("groupBtn");
const ungroupBtn = document.getElementById("ungroupBtn");
const selectAllBtn = document.getElementById("selectAllBtn");
const clearSelBtn = document.getElementById("clearSelBtn");

const alignLeftBtn = document.getElementById("alignLeftBtn");
const alignHCenterBtn = document.getElementById("alignHCenterBtn");
const alignRightBtn = document.getElementById("alignRightBtn");
const alignTopBtn = document.getElementById("alignTopBtn");
const alignVCenterBtn = document.getElementById("alignVCenterBtn");
const alignBottomBtn = document.getElementById("alignBottomBtn");
const distHBtn = document.getElementById("distHBtn");
const distVBtn = document.getElementById("distVBtn");

// Templates + snapping
const templatePreset = document.getElementById("templatePreset");
const applyTemplateBtn = document.getElementById("applyTemplateBtn");
const snapEnable = document.getElementById("snapEnable");
const guidesEnable = document.getElementById("guidesEnable");
const snapThresh = document.getElementById("snapThresh");
const snapThreshVal = document.getElementById("snapThreshVal");

// Sticker effects
const strokeEnable = document.getElementById("strokeEnable");
const strokeWidth = document.getElementById("strokeWidth");
const strokeWidthVal = document.getElementById("strokeWidthVal");
const strokeColor = document.getElementById("strokeColor");

const shadowEnable = document.getElementById("shadowEnable");
const shadowBlur = document.getElementById("shadowBlur");
const shadowBlurVal = document.getElementById("shadowBlurVal");
const shadowColor = document.getElementById("shadowColor");
const shadowX = document.getElementById("shadowX");
const shadowXVal = document.getElementById("shadowXVal");
const shadowY = document.getElementById("shadowY");
const shadowYVal = document.getElementById("shadowYVal");

const glowEnable = document.getElementById("glowEnable");
const glowBlur = document.getElementById("glowBlur");
const glowBlurVal = document.getElementById("glowBlurVal");
const glowColor = document.getElementById("glowColor");

const cropPad = document.getElementById("cropPad");
const cropPadVal = document.getElementById("cropPadVal");
const autoCropBtn = document.getElementById("autoCropBtn");

// Text tool
const textContent = document.getElementById("textContent");
const textSize = document.getElementById("textSize");
const textSizeVal = document.getElementById("textSizeVal");
const textFill = document.getElementById("textFill");
const textFont = document.getElementById("textFont");
const addTextBtn = document.getElementById("addTextBtn");
const updateTextBtn = document.getElementById("updateTextBtn");

const undoBtn = document.getElementById("undoBtn");
const redoBtn = document.getElementById("redoBtn");
const exportBtn = document.getElementById("exportBtn");
const debug = document.getElementById("debug");
const aiUserText = document.getElementById("aiUserText");
const aiRefineBtn = document.getElementById("aiRefineBtn");

// Magic candidates + refine
const candidatesBox = document.getElementById("candidates");
const candidatesGrid = document.getElementById("candidatesGrid");
const refineExpand = document.getElementById("refineExpand");
const refineExpandVal = document.getElementById("refineExpandVal");
const refineFeather = document.getElementById("refineFeather");
const refineFeatherVal = document.getElementById("refineFeatherVal");
const refineSmooth = document.getElementById("refineSmooth");
const refineSmoothVal = document.getElementById("refineSmoothVal");
const refineMinArea = document.getElementById("refineMinArea");
const refineMinAreaVal = document.getElementById("refineMinAreaVal");
const refineFillHoles = document.getElementById("refineFillHoles");
const refineDecontam = document.getElementById("refineDecontam");

// Change this if your backend port changes
const BACKEND = "http://127.0.0.1:8001";

function log(msg) {
	debug.textContent = msg + "\n" + debug.textContent;
	console.log(msg);
}

function clamp(v, a, b) {
	return Math.max(a, Math.min(b, v));
}

function hexToRgba(hex, alpha = 1) {
	// Accept #rgb or #rrggbb
	const h = (hex || "").replace("#", "").trim();
	if (h.length === 3) {
		const r = parseInt(h[0] + h[0], 16);
		const g = parseInt(h[1] + h[1], 16);
		const b = parseInt(h[2] + h[2], 16);
		return `rgba(${r},${g},${b},${alpha})`;
	}
	if (h.length === 6) {
		const r = parseInt(h.slice(0, 2), 16);
		const g = parseInt(h.slice(2, 4), 16);
		const b = parseInt(h.slice(4, 6), 16);
		return `rgba(${r},${g},${b},${alpha})`;
	}
	return `rgba(0,0,0,${alpha})`;
}

function defaultEffects() {
	return {
		strokeEnabled: false,
		strokeWidth: 0,
		strokeColor: "#ffffff",
		shadowEnabled: false,
		shadowBlur: 12,
		shadowOffsetX: 8,
		shadowOffsetY: 8,
		shadowColor: "#000000",
		glowEnabled: false,
		glowBlur: 20,
		glowColor: "#00ffff",
	};
}

function defaultLayout() {
	return {
		locked: false,
		blendMode: "source-over",
		opacity: 1,
		groupId: null,
	};
}

function normalizeEffects(eff) {
	return { ...defaultEffects(), ...(eff || {}) };
}

function normalizeLayout(l) {
	return { ...defaultLayout(), ...(l || {}) };
}

function getActiveEl() {
	if (activeIndex < 0 || activeIndex >= elements.length) return null;
	return elements[activeIndex];
}

const selected = new Set(); // indices

function getSelection() {
	if (selected.size > 0)
		return Array.from(selected).filter((i) => i >= 0 && i < elements.length);
	if (activeIndex >= 0) return [activeIndex];
	return [];
}

function setSelection(indices) {
	selected.clear();
	(indices || []).forEach((i) => {
		selected.add(i);
	});
	if (indices && indices.length > 0) activeIndex = indices[indices.length - 1];
	refreshSelect();
}

function setEffectsControlsEnabled(on) {
	const els = [
		strokeEnable,
		strokeWidth,
		strokeColor,
		shadowEnable,
		shadowBlur,
		shadowColor,
		shadowX,
		shadowY,
		glowEnable,
		glowBlur,
		glowColor,
		cropPad,
		autoCropBtn,
	];
	els.forEach((e) => {
		if (e) e.disabled = !on;
	});
}

function setTextControlsEnabled(on) {
	updateTextBtn.disabled = !on;
}

function syncUIFromActive() {
	const el = getActiveEl();
	const has = !!el;
	setEffectsControlsEnabled(has);
	autoCropBtn.disabled = !has;
	if (!has) {
		setTextControlsEnabled(false);
		return;
	}

	const eff = normalizeEffects(el.effects);
	strokeEnable.checked = !!eff.strokeEnabled;
	strokeWidth.value = String(eff.strokeWidth || 0);
	strokeWidthVal.textContent = String(eff.strokeWidth || 0);
	strokeColor.value = eff.strokeColor || "#ffffff";

	shadowEnable.checked = !!eff.shadowEnabled;
	shadowBlur.value = String(eff.shadowBlur || 0);
	shadowBlurVal.textContent = String(eff.shadowBlur || 0);
	shadowColor.value = eff.shadowColor || "#000000";
	shadowX.value = String(eff.shadowOffsetX || 0);
	shadowXVal.textContent = String(eff.shadowOffsetX || 0);
	shadowY.value = String(eff.shadowOffsetY || 0);
	shadowYVal.textContent = String(eff.shadowOffsetY || 0);

	glowEnable.checked = !!eff.glowEnabled;
	glowBlur.value = String(eff.glowBlur || 0);
	glowBlurVal.textContent = String(eff.glowBlur || 0);
	glowColor.value = eff.glowColor || "#00ffff";

	cropPadVal.textContent = String(cropPad.value);

	setTextControlsEnabled(el.type === "text");
	if (el.type === "text" && el.text) {
		textContent.value = el.text.content || "";
		textSize.value = String(el.text.size || 64);
		textSizeVal.textContent = String(el.text.size || 64);
		textFill.value = el.text.fill || "#ffffff";
		textFont.value = el.text.font || "system-ui";
	}

	const lay = normalizeLayout(el.layout);
	lockEnable.checked = !!lay.locked;
	blendMode.value = lay.blendMode || "source-over";
	const opPct = Math.round((lay.opacity ?? 1) * 100);
	opacity.value = String(opPct);
	opacityVal.textContent = String(opPct);
}

function markCanvasChanged(el) {
	el._canvasVersion = (el._canvasVersion || 0) + 1;
	el._strokeCache = null;
}

function ensureElementDefaults(el) {
	el.type = el.type || "image";
	el.effects = normalizeEffects(el.effects);
	el.layout = normalizeLayout(el.layout);
	el._canvasVersion = el._canvasVersion || 1;
	el._strokeCache = null;
	return el;
}

function getRefineParams() {
	return {
		expand: Number(refineExpand?.value || 0) || 0,
		feather: Number(refineFeather?.value || 0) || 0,
		smooth: Number(refineSmooth?.value || 0) || 0,
		fill_holes: !!refineFillHoles?.checked,
		remove_islands_min_area: Number(refineMinArea?.value || 0) || 0,
		decontam: !!refineDecontam?.checked,
		// keep backend defaults for advanced knobs
	};
}

function setCandidatesVisible(show) {
	if (!candidatesBox) return;
	candidatesBox.hidden = !show;
	if (!show && candidatesGrid) candidatesGrid.innerHTML = "";
}

async function loadCandidatesToLastMagicCutout(candidates) {
	// Render candidate cards and let user choose; sets lastMagicCutout
	if (!candidatesGrid || !candidatesBox) return;
	candidatesGrid.innerHTML = "";

	const MAX = 900;

	candidates.forEach((cand, idx) => {
		const card = document.createElement("div");
		card.className = "cand";

		const imgEl = document.createElement("img");
		imgEl.src = `data:image/png;base64,${cand.png_b64}`;
		imgEl.alt = `Candidate ${idx}`;
		card.appendChild(imgEl);

		const meta = document.createElement("div");
		meta.className = "candMeta";
		const score = document.createElement("div");
		score.textContent = `score: ${Number(cand.score).toFixed(3)}`;
		const btn = document.createElement("button");
		btn.className = "candBtn";
		btn.textContent = "Use";
		btn.addEventListener("click", async () => {
			const im = new Image();
			im.onload = () => {
				const c = document.createElement("canvas");
				c.width = im.width;
				c.height = im.height;
				c.getContext("2d").drawImage(im, 0, 0);

				// Downscale if needed
				const shrink = Math.min(1, MAX / Math.max(c.width, c.height));
				if (shrink < 1) {
					const s = document.createElement("canvas");
					s.width = Math.floor(c.width * shrink);
					s.height = Math.floor(c.height * shrink);
					s.getContext("2d").drawImage(c, 0, 0, s.width, s.height);
					lastMagicCutout = s;
				} else {
					lastMagicCutout = c;
				}

				magicAddBtn.disabled = false;
				setCandidatesVisible(false);
				log("Candidate selected. Click 'Add magic-selected element'.");
			};
			im.src = imgEl.src;
		});
		meta.appendChild(score);
		meta.appendChild(btn);
		card.appendChild(meta);

		candidatesGrid.appendChild(card);
	});

	setCandidatesVisible(true);
}

let img = null;
let uploadedFileBlob = null;

// Fit info for rendering original image into editor canvas
let render = { scale: 1, dx: 0, dy: 0, dw: 0, dh: 0 };

// Rectangle crop state (editor canvas coords)
let crop = null;
let selecting = false;
let start = { x: 0, y: 0 };

// Magic cutout result
let lastMagicCutout = null;

// Elements on final canvas
let elements = [];
let activeIndex = -1;

// Undo/Redo History
const MAX_HISTORY = 20;
let historyStack = [];
let historyStep = -1;

function saveState() {
	// Remove any future history if we are in the middle
	if (historyStep < historyStack.length - 1) {
		historyStack = historyStack.slice(0, historyStep + 1);
	}

	// Deep clone elements
	const snapshot = elements.map((el) => {
		const c = document.createElement("canvas");
		c.width = el.canvas.width;
		c.height = el.canvas.height;
		c.getContext("2d").drawImage(el.canvas, 0, 0);
		return {
			canvas: c,
			type: el.type || "image",
			x: el.x,
			y: el.y,
			scale: el.scale,
			rotation: el.rotation,
			effects: JSON.parse(JSON.stringify(el.effects || {})),
			layout: JSON.parse(JSON.stringify(el.layout || {})),
			text: el.text ? JSON.parse(JSON.stringify(el.text)) : null,
			_canvasVersion: el._canvasVersion || 1,
		};
	});

	historyStack.push(snapshot);
	if (historyStack.length > MAX_HISTORY) {
		historyStack.shift();
	} else {
		historyStep++;
	}
	updateUndoRedoUI();
}

function restoreState(step) {
	if (step < 0 || step >= historyStack.length) return;

	const snapshot = historyStack[step];
	// Restore from snapshot
	elements = snapshot.map((s) => {
		const c = document.createElement("canvas");
		c.width = s.canvas.width;
		c.height = s.canvas.height;
		c.getContext("2d").drawImage(s.canvas, 0, 0);
		return ensureElementDefaults({
			canvas: c,
			type: s.type || "image",
			x: s.x,
			y: s.y,
			scale: s.scale,
			rotation: s.rotation,
			effects: s.effects || null,
			layout: s.layout || null,
			text: s.text || null,
			_canvasVersion: s._canvasVersion || 1,
		});
	});

	historyStep = step;
	activeIndex = -1; // Deselect on undo/redo to avoid index mismatch
	refreshSelect();
	redrawFinal();
	updateUndoRedoUI();
}

function updateUndoRedoUI() {
	undoBtn.disabled = historyStep <= 0;
	redoBtn.disabled = historyStep >= historyStack.length - 1;
}

undoBtn.addEventListener("click", () => restoreState(historyStep - 1));
redoBtn.addEventListener("click", () => restoreState(historyStep + 1));

// Dragging elements
const drag = { on: false, idx: -1, ox: 0, oy: 0, startState: null };

// Brush prompting state
const brush = {
	on: false,
	pos: [], // positive points in ORIGINAL image coords
	neg: [], // negative points (erase)
	last: null, // last editor point for spacing
	_strokePreview: [], // editor points for overlay drawing
	_strokePreviewNeg: [], // editor points for overlay drawing (negative)
};

const BRUSH_SPACING = 10;

// ---------- Coordinates ----------
function getCanvasPos(evt, canvas) {
	const rect = canvas.getBoundingClientRect();
	const sx = canvas.width / rect.width;
	const sy = canvas.height / rect.height;
	return {
		x: (evt.clientX - rect.left) * sx,
		y: (evt.clientY - rect.top) * sy,
	};
}

function clampRect(r) {
	let { x, y, w, h } = r;
	if (w < 0) {
		x += w;
		w = -w;
	}
	if (h < 0) {
		y += h;
		h = -h;
	}
	return { x, y, w, h };
}

function dist(a, b) {
	const dx = a.x - b.x,
		dy = a.y - b.y;
	return Math.sqrt(dx * dx + dy * dy);
}

function isInsideRenderedImage(p) {
	return (
		p.x >= render.dx &&
		p.y >= render.dy &&
		p.x <= render.dx + render.dw &&
		p.y <= render.dy + render.dh
	);
}

function editorToImageCoords(p) {
	const insideX = p.x - render.dx;
	const insideY = p.y - render.dy;
	const ix = Math.floor(insideX / render.scale);
	const iy = Math.floor(insideY / render.scale);
	return { ix, iy };
}

// ---------- Editor rendering ----------
function computeFit() {
	const cw = editor.width,
		ch = editor.height;
	const iw = img.width,
		ih = img.height;
	const s = Math.min(cw / iw, ch / ih);

	const dw = Math.floor(iw * s);
	const dh = Math.floor(ih * s);
	const dx = Math.floor((cw - dw) / 2);
	const dy = Math.floor((ch - dh) / 2);

	render = { scale: s, dx, dy, dw, dh };
}

function drawEditor() {
	ctx.clearRect(0, 0, editor.width, editor.height);
	ctx.fillStyle = "#000";
	ctx.fillRect(0, 0, editor.width, editor.height);

	if (!img) return;

	ctx.drawImage(img, render.dx, render.dy, render.dw, render.dh);

	// Rectangle crop overlay
	if (selectMode.value === "rect" && crop) {
		const r = clampRect(crop);
		ctx.save();
		ctx.strokeStyle = "rgba(255,0,0,0.95)";
		ctx.lineWidth = 3;
		ctx.strokeRect(r.x, r.y, r.w, r.h);
		ctx.fillStyle = "rgba(255,0,0,0.12)";
		ctx.fillRect(r.x, r.y, r.w, r.h);
		ctx.restore();
	}

	// Brush overlay (current stroke)
	if (selectMode.value === "brush" && brush._strokePreview.length > 0) {
		ctx.save();
		ctx.strokeStyle = "rgba(0,255,0,0.9)";
		ctx.lineWidth = 3;
		ctx.beginPath();
		ctx.moveTo(brush._strokePreview[0].x, brush._strokePreview[0].y);
		for (let i = 1; i < brush._strokePreview.length; i++) {
			ctx.lineTo(brush._strokePreview[i].x, brush._strokePreview[i].y);
		}
		ctx.stroke();
		ctx.restore();
	}

	// Negative brush overlay (erase stroke)
	if (selectMode.value === "brush" && brush._strokePreviewNeg.length > 0) {
		ctx.save();
		ctx.strokeStyle = "rgba(255,0,0,0.9)";
		ctx.lineWidth = 3;
		ctx.beginPath();
		ctx.moveTo(brush._strokePreviewNeg[0].x, brush._strokePreviewNeg[0].y);
		for (let i = 1; i < brush._strokePreviewNeg.length; i++) {
			ctx.lineTo(brush._strokePreviewNeg[i].x, brush._strokePreviewNeg[i].y);
		}
		ctx.stroke();
		ctx.restore();
	}
}

function cropToElementCanvas() {
	if (!img || !crop) return null;
	const r = clampRect(crop);
	if (r.w < 10 || r.h < 10) return null;

	const insideX = r.x - render.dx;
	const insideY = r.y - render.dy;

	if (
		insideX < 0 ||
		insideY < 0 ||
		insideX + r.w > render.dw ||
		insideY + r.h > render.dh
	) {
		log("Rectangle must be inside the image area.");
		return null;
	}

	const ix = Math.floor(insideX / render.scale);
	const iy = Math.floor(insideY / render.scale);
	const iw = Math.floor(r.w / render.scale);
	const ih = Math.floor(r.h / render.scale);

	const MAX = 900;
	const shrink = Math.min(1, MAX / Math.max(iw, ih));
	const ew = Math.max(1, Math.floor(iw * shrink));
	const eh = Math.max(1, Math.floor(ih * shrink));

	const c = document.createElement("canvas");
	c.width = ew;
	c.height = eh;
	c.getContext("2d").drawImage(img, ix, iy, iw, ih, 0, 0, ew, eh);
	return c;
}

function autoCropCanvas(srcCanvas, padding = 0) {
	const w = srcCanvas.width;
	const h = srcCanvas.height;
	const sctx = srcCanvas.getContext("2d", { willReadFrequently: true });
	const imgData = sctx.getImageData(0, 0, w, h);
	const data = imgData.data;

	let minX = w,
		minY = h,
		maxX = -1,
		maxY = -1;
	for (let y = 0; y < h; y++) {
		for (let x = 0; x < w; x++) {
			const a = data[(y * w + x) * 4 + 3];
			if (a > 0) {
				if (x < minX) minX = x;
				if (y < minY) minY = y;
				if (x > maxX) maxX = x;
				if (y > maxY) maxY = y;
			}
		}
	}

	// Fully transparent
	if (maxX < minX || maxY < minY) return srcCanvas;

	const pad = Math.max(0, Math.floor(padding));
	minX = clamp(minX - pad, 0, w - 1);
	minY = clamp(minY - pad, 0, h - 1);
	maxX = clamp(maxX + pad, 0, w - 1);
	maxY = clamp(maxY + pad, 0, h - 1);

	const nw = Math.max(1, maxX - minX + 1);
	const nh = Math.max(1, maxY - minY + 1);
	const out = document.createElement("canvas");
	out.width = nw;
	out.height = nh;
	out.getContext("2d").drawImage(srcCanvas, minX, minY, nw, nh, 0, 0, nw, nh);
	return out;
}

function buildOutlineCanvas(srcCanvas, strokeW, colorHex) {
	const w = srcCanvas.width;
	const h = srcCanvas.height;
	const sw = Math.max(0, Math.floor(strokeW));
	if (sw <= 0) return null;

	const out = document.createElement("canvas");
	out.width = w + sw * 2;
	out.height = h + sw * 2;
	const octx = out.getContext("2d");

	// Draw dilated alpha by stamping the source around in a radius.
	octx.clearRect(0, 0, out.width, out.height);
	octx.globalCompositeOperation = "source-over";

	for (let dy = -sw; dy <= sw; dy++) {
		for (let dx = -sw; dx <= sw; dx++) {
			if (dx * dx + dy * dy > sw * sw) continue;
			octx.drawImage(srcCanvas, sw + dx, sw + dy);
		}
	}

	// Convert to solid color using alpha as mask
	octx.globalCompositeOperation = "source-in";
	octx.fillStyle = colorHex || "#ffffff";
	octx.fillRect(0, 0, out.width, out.height);

	// Remove interior (original)
	octx.globalCompositeOperation = "destination-out";
	octx.drawImage(srcCanvas, sw, sw);

	octx.globalCompositeOperation = "source-over";
	return out;
}

function getOutlineForElement(el) {
	const eff = normalizeEffects(el.effects);
	if (!eff.strokeEnabled || (eff.strokeWidth | 0) <= 0) return null;

	const sw = Math.floor(eff.strokeWidth);
	const col = eff.strokeColor || "#ffffff";

	const cache = el._strokeCache;
	if (
		cache &&
		cache.sw === sw &&
		cache.color === col &&
		cache.srcVersion === (el._canvasVersion || 1) &&
		cache.canvas
	) {
		return cache.canvas;
	}

	const outline = buildOutlineCanvas(el.canvas, sw, col);
	el._strokeCache = {
		sw,
		color: col,
		srcVersion: el._canvasVersion || 1,
		canvas: outline,
	};
	return outline;
}

function drawElementWithEffects(ctx2d, el) {
	const eff = normalizeEffects(el.effects);
	const w = el.canvas.width;
	const h = el.canvas.height;
	const outline = getOutlineForElement(el);
	const sw = eff.strokeEnabled ? Math.floor(eff.strokeWidth || 0) : 0;

	const drawBase = () => {
		if (outline) ctx2d.drawImage(outline, -(w / 2 + sw), -(h / 2 + sw));
		ctx2d.drawImage(el.canvas, -w / 2, -h / 2);
	};

	const shadowSilhouette = outline || el.canvas;
	const shadowOffsetForOutline = outline ? sw : 0;

	// Glow pass
	if (eff.glowEnabled && (eff.glowBlur || 0) > 0) {
		ctx2d.shadowColor = hexToRgba(eff.glowColor || "#00ffff", 0.75);
		ctx2d.shadowBlur = eff.glowBlur || 0;
		ctx2d.shadowOffsetX = 0;
		ctx2d.shadowOffsetY = 0;
		ctx2d.drawImage(
			shadowSilhouette,
			-(w / 2 + shadowOffsetForOutline),
			-(h / 2 + shadowOffsetForOutline),
		);
	}

	// Shadow pass
	if (
		eff.shadowEnabled &&
		((eff.shadowBlur || 0) > 0 ||
			(eff.shadowOffsetX || 0) !== 0 ||
			(eff.shadowOffsetY || 0) !== 0)
	) {
		ctx2d.shadowColor = hexToRgba(eff.shadowColor || "#000000", 0.55);
		ctx2d.shadowBlur = eff.shadowBlur || 0;
		ctx2d.shadowOffsetX = eff.shadowOffsetX || 0;
		ctx2d.shadowOffsetY = eff.shadowOffsetY || 0;
		ctx2d.drawImage(
			shadowSilhouette,
			-(w / 2 + shadowOffsetForOutline),
			-(h / 2 + shadowOffsetForOutline),
		);
	}

	// Draw actual sticker sharp (no shadow)
	ctx2d.shadowColor = "rgba(0,0,0,0)";
	ctx2d.shadowBlur = 0;
	ctx2d.shadowOffsetX = 0;
	ctx2d.shadowOffsetY = 0;
	drawBase();
}

function getElementAABB(el, dx = 0, dy = 0) {
	// Axis-aligned bbox of rotated+scaled rectangle in world coords.
	const w = el.canvas.width;
	const h = el.canvas.height;
	const s = el.scale || 1;
	const rad = ((el.rotation || 0) * Math.PI) / 180;
	const c = Math.cos(rad);
	const si = Math.sin(rad);
	const hw = (w * s) / 2;
	const hh = (h * s) / 2;
	const halfW = Math.abs(c) * hw + Math.abs(si) * hh;
	const halfH = Math.abs(si) * hw + Math.abs(c) * hh;
	const cx = el.x + w / 2 + dx;
	const cy = el.y + h / 2 + dy;
	return {
		cx,
		cy,
		left: cx - halfW,
		right: cx + halfW,
		top: cy - halfH,
		bottom: cy + halfH,
		width: halfW * 2,
		height: halfH * 2,
	};
}

let currentGuides = { xs: [], ys: [] }; // {xs:[number], ys:[number]}

function makeTextCanvas(text, fontSize, fontFamily, fill, strokeW, strokeCol) {
	const content = (text ?? "").toString();
	const size = Math.max(12, Number(fontSize) || 64);
	const font = `${size}px ${fontFamily || "system-ui"}`;

	const tmp = document.createElement("canvas");
	const tctx = tmp.getContext("2d");
	tctx.font = font;
	tctx.textBaseline = "alphabetic";

	const metrics = tctx.measureText(content || " ");
	const asc = metrics.actualBoundingBoxAscent || size * 0.8;
	const desc = metrics.actualBoundingBoxDescent || size * 0.25;
	const textW = Math.ceil(metrics.width);
	const textH = Math.ceil(asc + desc);

	const pad = Math.ceil(Math.max(2, (strokeW || 0) * 2 + 10));
	const out = document.createElement("canvas");
	out.width = textW + pad * 2;
	out.height = textH + pad * 2;
	const octx = out.getContext("2d");
	octx.font = font;
	octx.textBaseline = "alphabetic";

	const x = pad;
	const y = pad + asc;

	if ((strokeW || 0) > 0) {
		octx.lineJoin = "round";
		octx.miterLimit = 2;
		octx.lineWidth = strokeW;
		octx.strokeStyle = strokeCol || "#000000";
		octx.strokeText(content, x, y);
	}
	octx.fillStyle = fill || "#ffffff";
	octx.fillText(content, x, y);

	return out;
}

function rerenderTextElement(el) {
	if (!el || el.type !== "text") return;
	const eff = normalizeEffects(el.effects);
	const oldW = el.canvas.width;
	const oldH = el.canvas.height;
	const cx = el.x + oldW / 2;
	const cy = el.y + oldH / 2;

	el.canvas = makeTextCanvas(
		el.text?.content || "",
		el.text?.size || 64,
		el.text?.font || "system-ui",
		el.text?.fill || "#ffffff",
		eff.strokeEnabled ? eff.strokeWidth || 0 : 0,
		eff.strokeColor || "#000000",
	);
	markCanvasChanged(el);
	el.x = cx - el.canvas.width / 2;
	el.y = cy - el.canvas.height / 2;
}

// ---------- Final canvas ----------
function redrawFinal(transparentBg = false, hideSelection = false) {
	fctx.clearRect(0, 0, finalCanvas.width, finalCanvas.height);

	if (!transparentBg) {
		fctx.fillStyle = "#000";
		fctx.fillRect(0, 0, finalCanvas.width, finalCanvas.height);
	}

	elements.forEach((el, i) => {
		fctx.save();
		ensureElementDefaults(el);
		const lay = normalizeLayout(el.layout);

		// Center of the element
		const w = el.canvas.width;
		const h = el.canvas.height;
		const cx = el.x + w / 2;
		const cy = el.y + h / 2;

		// Apply transforms
		fctx.translate(cx, cy);
		fctx.rotate(((el.rotation || 0) * Math.PI) / 180);
		fctx.scale(el.scale || 1, el.scale || 1);

		// Per-element blend + opacity
		fctx.globalCompositeOperation = lay.blendMode || "source-over";
		fctx.globalAlpha = typeof lay.opacity === "number" ? lay.opacity : 1;

		// Draw centered at (0,0) with effects
		drawElementWithEffects(fctx, el);

		// Selection outline
		fctx.globalCompositeOperation = "source-over";
		fctx.globalAlpha = 1;
		if (!hideSelection && selected.has(i)) {
			fctx.strokeStyle = "rgba(0,255,255,0.9)";
			fctx.lineWidth = 2;
			fctx.strokeRect(-w / 2, -h / 2, w, h);
		}
		if (!hideSelection && i === activeIndex) {
			fctx.strokeStyle = "rgba(255,255,0,0.9)";
			fctx.lineWidth = 2;
			fctx.strokeRect(-w / 2 - 4, -h / 2 - 4, w + 8, h + 8);
		}

		fctx.restore();
	});

	// Guides overlay
	if (
		guidesEnable?.checked &&
		(currentGuides.xs.length || currentGuides.ys.length)
	) {
		fctx.save();
		fctx.globalCompositeOperation = "source-over";
		fctx.globalAlpha = 1;
		fctx.strokeStyle = "rgba(0,255,255,0.65)";
		fctx.lineWidth = 1;
		currentGuides.xs.forEach((x) => {
			fctx.beginPath();
			fctx.moveTo(x, 0);
			fctx.lineTo(x, finalCanvas.height);
			fctx.stroke();
		});
		currentGuides.ys.forEach((y) => {
			fctx.beginPath();
			fctx.moveTo(0, y);
			fctx.lineTo(finalCanvas.width, y);
			fctx.stroke();
		});
		fctx.restore();
	}
}

function refreshSelect() {
	activeSelect.innerHTML = "";
	elements.forEach((el, i) => {
		const opt = document.createElement("option");
		opt.value = String(i);
		const lay = normalizeLayout(el.layout);
		const flags = [
			selected.has(i) ? "✓" : "",
			lay.locked ? "🔒" : "",
			lay.groupId ? `G${lay.groupId}` : "",
		]
			.filter(Boolean)
			.join(" ");
		opt.textContent = `${el.type === "text" ? "Text" : "Image"} ${i}${flags ? "  " + flags : ""}`;
		activeSelect.appendChild(opt);
	});

	const has = elements.length > 0;
	activeSelect.disabled = !has;
	applyBtn.disabled = !has;

	// Layer & Transform controls
	toFrontBtn.disabled = !has;
	toBackBtn.disabled = !has;
	deleteBtn.disabled = !has;
	scaleRange.disabled = !has;
	rotRange.disabled = !has;
	setLayoutControlsEnabled(has);
	selectAllBtn.disabled = !has;
	clearSelBtn.disabled = !has;

	if (!has) {
		activeIndex = -1;
		return;
	}

	if (activeIndex < 0) activeIndex = 0;
	if (activeIndex >= elements.length) activeIndex = elements.length - 1;
	activeSelect.value = String(activeIndex);

	// Update sliders for active element
	const el = elements[activeIndex];
	ensureElementDefaults(el);
	scaleRange.value = el.scale || 1;
	scaleVal.textContent = (el.scale || 1).toFixed(1);
	rotRange.value = el.rotation || 0;
	rotVal.textContent = el.rotation || 0;

	applyBtn.disabled = el.type === "text";
	syncUIFromActive();

	// Enable/disable group/alignment buttons based on selection size
	const sel = getSelection();
	const multi = sel.length >= 2;
	groupBtn.disabled = !multi;
	distHBtn.disabled = sel.length < 3;
	distVBtn.disabled = sel.length < 3;
	alignLeftBtn.disabled = !multi;
	alignHCenterBtn.disabled = !multi;
	alignRightBtn.disabled = !multi;
	alignTopBtn.disabled = !multi;
	alignVCenterBtn.disabled = !multi;
	alignBottomBtn.disabled = !multi;

	// Ungroup enabled if any selected has groupId
	ungroupBtn.disabled = !sel.some(
		(idx) => normalizeLayout(elements[idx].layout).groupId,
	);
}

function hitTest(mx, my) {
	for (let i = elements.length - 1; i >= 0; i--) {
		const el = elements[i];
		ensureElementDefaults(el);
		const w = el.canvas.width;
		const h = el.canvas.height;
		const cx = el.x + w / 2;
		const cy = el.y + h / 2;

		// Transform mouse point to local element space
		// 1. Translate
		const dx = mx - cx;
		const dy = my - cy;

		// 2. Rotate (inverse)
		const rad = (-(el.rotation || 0) * Math.PI) / 180;
		const rx = dx * Math.cos(rad) - dy * Math.sin(rad);
		const ry = dx * Math.sin(rad) + dy * Math.cos(rad);

		// 3. Scale (inverse)
		const s = el.scale || 1;
		const lx = rx / s;
		const ly = ry / s;

		// Check bounds in local space (centered)
		if (lx >= -w / 2 && lx <= w / 2 && ly >= -h / 2 && ly <= h / 2) {
			return i;
		}
	}
	return -1;
}

// ---------- Upload ----------
fileInput.addEventListener("change", (e) => {
	const file = e.target.files?.[0];
	if (!file) return;

	uploadedFileBlob = file;
	lastMagicCutout = null;
	magicAddBtn.disabled = true;

	img = new Image();
	img.onload = () => {
		crop = null;
		addBtn.disabled = true;

		brush.on = false;
		brush.pos = [];
		brush.neg = [];
		brush.last = null;
		brush._strokePreview = [];

		computeFit();
		drawEditor();
		setBgBtn.disabled = false;
		log(`Loaded image: ${img.width}x${img.height}`);
	};
	img.onerror = () => log("Failed to load image.");
	img.src = URL.createObjectURL(file);
});

// ---------- Effects UI wiring ----------
strokeWidthVal.textContent = strokeWidth.value;
shadowBlurVal.textContent = shadowBlur.value;
shadowXVal.textContent = shadowX.value;
shadowYVal.textContent = shadowY.value;
glowBlurVal.textContent = glowBlur.value;
cropPadVal.textContent = cropPad.value;
textSizeVal.textContent = textSize.value;
opacityVal.textContent = opacity.value;
snapThreshVal.textContent = snapThresh.value;

// Refine UI defaults
if (refineExpandVal && refineExpand)
	refineExpandVal.textContent = refineExpand.value;
if (refineFeatherVal && refineFeather)
	refineFeatherVal.textContent = refineFeather.value;
if (refineSmoothVal && refineSmooth)
	refineSmoothVal.textContent = refineSmooth.value;
if (refineMinAreaVal && refineMinArea)
	refineMinAreaVal.textContent = refineMinArea.value;
if (refineExpand) {
	refineExpand.addEventListener("input", () => {
		refineExpandVal.textContent = refineExpand.value;
	});
}
if (refineFeather) {
	refineFeather.addEventListener("input", () => {
		refineFeatherVal.textContent = refineFeather.value;
	});
}
if (refineSmooth) {
	refineSmooth.addEventListener("input", () => {
		refineSmoothVal.textContent = refineSmooth.value;
	});
}
if (refineMinArea) {
	refineMinArea.addEventListener("input", () => {
		refineMinAreaVal.textContent = refineMinArea.value;
	});
}

// No active element at boot.
setEffectsControlsEnabled(false);
setTextControlsEnabled(false);
setCandidatesVisible(false);

function setLayoutControlsEnabled(on) {
	const els = [
		lockEnable,
		blendMode,
		opacity,
		groupBtn,
		ungroupBtn,
		selectAllBtn,
		clearSelBtn,
		alignLeftBtn,
		alignHCenterBtn,
		alignRightBtn,
		alignTopBtn,
		alignVCenterBtn,
		alignBottomBtn,
		distHBtn,
		distVBtn,
	];
	els.forEach((e) => {
		if (e) e.disabled = !on;
	});
}

setLayoutControlsEnabled(false);

snapThresh.addEventListener("input", () => {
	snapThreshVal.textContent = snapThresh.value;
});

function applyEffectsFromUI(save = false) {
	const el = getActiveEl();
	if (!el) return;
	if (save) saveState();

	const eff = normalizeEffects(el.effects);
	eff.strokeEnabled = !!strokeEnable.checked;
	eff.strokeWidth = Number(strokeWidth.value) || 0;
	eff.strokeColor = strokeColor.value || "#ffffff";

	eff.shadowEnabled = !!shadowEnable.checked;
	eff.shadowBlur = Number(shadowBlur.value) || 0;
	eff.shadowColor = shadowColor.value || "#000000";
	eff.shadowOffsetX = Number(shadowX.value) || 0;
	eff.shadowOffsetY = Number(shadowY.value) || 0;

	eff.glowEnabled = !!glowEnable.checked;
	eff.glowBlur = Number(glowBlur.value) || 0;
	eff.glowColor = glowColor.value || "#00ffff";

	el.effects = eff;
	el._strokeCache = null;

	// For text elements, outline is baked into the text canvas.
	if (el.type === "text") {
		rerenderTextElement(el);
	}

	redrawFinal();
}

function applyLayoutFromUI(save = false) {
	const el = getActiveEl();
	if (!el) return;
	if (save) saveState();
	ensureElementDefaults(el);

	const lay = normalizeLayout(el.layout);
	lay.locked = !!lockEnable.checked;
	lay.blendMode = blendMode.value || "source-over";
	lay.opacity = (Number(opacity.value) || 100) / 100;
	el.layout = lay;

	opacityVal.textContent = opacity.value;
	redrawFinal();
}

lockEnable.addEventListener("change", () => applyLayoutFromUI(true));
blendMode.addEventListener("change", () => applyLayoutFromUI(true));
opacity.addEventListener("input", () => applyLayoutFromUI(false));
opacity.addEventListener("change", () => applyLayoutFromUI(true));

selectAllBtn.addEventListener("click", () => {
	setSelection(elements.map((_, i) => i));
	redrawFinal();
});
clearSelBtn.addEventListener("click", () => {
	setSelection([]);
	activeIndex = elements.length ? 0 : -1;
	refreshSelect();
	redrawFinal();
});

let nextGroupId = 1;
groupBtn.addEventListener("click", () => {
	const sel = getSelection();
	if (sel.length < 2) return;
	saveState();
	const gid = String(nextGroupId++);
	sel.forEach((idx) => {
		const el = elements[idx];
		ensureElementDefaults(el);
		el.layout.groupId = gid;
	});
	refreshSelect();
	redrawFinal();
	log(`Grouped ${sel.length} elements (G${gid}).`);
});

ungroupBtn.addEventListener("click", () => {
	const sel = getSelection();
	if (sel.length < 1) return;
	saveState();
	sel.forEach((idx) => {
		const el = elements[idx];
		ensureElementDefaults(el);
		el.layout.groupId = null;
	});
	refreshSelect();
	redrawFinal();
	log("Ungrouped selection.");
});

function moveElementCenter(el, newCx, newCy) {
	el.x = newCx - el.canvas.width / 2;
	el.y = newCy - el.canvas.height / 2;
}

function alignSelection(mode) {
	const sel = getSelection();
	if (sel.length < 2) return;
	saveState();
	const aabbs = sel.map((i) => ({ i, a: getElementAABB(elements[i]) }));

	const left = Math.min(...aabbs.map((o) => o.a.left));
	const right = Math.max(...aabbs.map((o) => o.a.right));
	const top = Math.min(...aabbs.map((o) => o.a.top));
	const bottom = Math.max(...aabbs.map((o) => o.a.bottom));
	const cx = (left + right) / 2;
	const cy = (top + bottom) / 2;

	aabbs.forEach(({ i, a }) => {
		const el = elements[i];
		const d = { dx: 0, dy: 0 };
		if (mode === "left") d.dx = left - a.left;
		if (mode === "hcenter") d.dx = cx - a.cx;
		if (mode === "right") d.dx = right - a.right;
		if (mode === "top") d.dy = top - a.top;
		if (mode === "vcenter") d.dy = cy - a.cy;
		if (mode === "bottom") d.dy = bottom - a.bottom;
		moveElementCenter(el, a.cx + d.dx, a.cy + d.dy);
	});
	redrawFinal();
}

alignLeftBtn.addEventListener("click", () => alignSelection("left"));
alignHCenterBtn.addEventListener("click", () => alignSelection("hcenter"));
alignRightBtn.addEventListener("click", () => alignSelection("right"));
alignTopBtn.addEventListener("click", () => alignSelection("top"));
alignVCenterBtn.addEventListener("click", () => alignSelection("vcenter"));
alignBottomBtn.addEventListener("click", () => alignSelection("bottom"));

function distributeSelection(axis) {
	const sel = getSelection();
	if (sel.length < 3) return;
	saveState();
	const items = sel.map((i) => ({ i, a: getElementAABB(elements[i]) }));
	if (axis === "x") {
		items.sort((p, q) => p.a.left - q.a.left);
		const minL = items[0].a.left;
		const maxR = Math.max(...items.map((o) => o.a.right));
		const totalW = items.reduce((s, o) => s + o.a.width, 0);
		const gap = (maxR - minL - totalW) / (items.length - 1);
		let cur = minL;
		items.forEach((o) => {
			const el = elements[o.i];
			const desiredLeft = cur;
			const dx = desiredLeft - o.a.left;
			moveElementCenter(el, o.a.cx + dx, o.a.cy);
			cur += o.a.width + gap;
		});
	} else {
		items.sort((p, q) => p.a.top - q.a.top);
		const minT = items[0].a.top;
		const maxB = Math.max(...items.map((o) => o.a.bottom));
		const totalH = items.reduce((s, o) => s + o.a.height, 0);
		const gap = (maxB - minT - totalH) / (items.length - 1);
		let cur = minT;
		items.forEach((o) => {
			const el = elements[o.i];
			const desiredTop = cur;
			const dy = desiredTop - o.a.top;
			moveElementCenter(el, o.a.cx, o.a.cy + dy);
			cur += o.a.height + gap;
		});
	}
	redrawFinal();
}

distHBtn.addEventListener("click", () => distributeSelection("x"));
distVBtn.addEventListener("click", () => distributeSelection("y"));

strokeEnable.addEventListener("change", () => applyEffectsFromUI(true));
shadowEnable.addEventListener("change", () => applyEffectsFromUI(true));
glowEnable.addEventListener("change", () => applyEffectsFromUI(true));

strokeWidth.addEventListener("input", () => {
	strokeWidthVal.textContent = strokeWidth.value;
	applyEffectsFromUI(false);
});
strokeWidth.addEventListener("change", () => applyEffectsFromUI(true));
strokeColor.addEventListener("change", () => applyEffectsFromUI(true));

shadowBlur.addEventListener("input", () => {
	shadowBlurVal.textContent = shadowBlur.value;
	applyEffectsFromUI(false);
});
shadowBlur.addEventListener("change", () => applyEffectsFromUI(true));
shadowX.addEventListener("input", () => {
	shadowXVal.textContent = shadowX.value;
	applyEffectsFromUI(false);
});
shadowX.addEventListener("change", () => applyEffectsFromUI(true));
shadowY.addEventListener("input", () => {
	shadowYVal.textContent = shadowY.value;
	applyEffectsFromUI(false);
});
shadowY.addEventListener("change", () => applyEffectsFromUI(true));
shadowColor.addEventListener("change", () => applyEffectsFromUI(true));

glowBlur.addEventListener("input", () => {
	glowBlurVal.textContent = glowBlur.value;
	applyEffectsFromUI(false);
});
glowBlur.addEventListener("change", () => applyEffectsFromUI(true));
glowColor.addEventListener("change", () => applyEffectsFromUI(true));

cropPad.addEventListener("input", () => {
	cropPadVal.textContent = cropPad.value;
});

autoCropBtn.addEventListener("click", () => {
	const el = getActiveEl();
	if (!el) return;
	saveState();
	const oldW = el.canvas.width;
	const oldH = el.canvas.height;
	const cx = el.x + oldW / 2;
	const cy = el.y + oldH / 2;

	const cropped = autoCropCanvas(el.canvas, Number(cropPad.value) || 0);
	el.canvas = cropped;
	markCanvasChanged(el);
	el.x = cx - el.canvas.width / 2;
	el.y = cy - el.canvas.height / 2;
	redrawFinal();
	log("Auto-cropped active element.");
});

// ---------- Text tool ----------
addTextBtn.addEventListener("click", () => {
	const content = (textContent.value || "").trim();
	if (!content) {
		log("Text is empty.");
		return;
	}

	saveState();
	const eff = defaultEffects();
	eff.strokeEnabled = true;
	eff.strokeWidth = 6;
	eff.strokeColor = "#000000";

	const el = ensureElementDefaults({
		type: "text",
		text: {
			content,
			size: Number(textSize.value) || 64,
			font: textFont.value || "system-ui",
			fill: textFill.value || "#ffffff",
		},
		effects: eff,
		canvas: document.createElement("canvas"),
		x: 80 + elements.length * 20,
		y: 80 + elements.length * 20,
		scale: 1,
		rotation: 0,
	});

	el.canvas = makeTextCanvas(
		el.text.content,
		el.text.size,
		el.text.font,
		el.text.fill,
		el.effects.strokeEnabled ? el.effects.strokeWidth : 0,
		el.effects.strokeColor,
	);
	markCanvasChanged(el);

	elements.push(el);
	activeIndex = elements.length - 1;
	refreshSelect();
	redrawFinal();
	log(`Text element added: #${activeIndex}`);
});

updateTextBtn.addEventListener("click", () => {
	const el = getActiveEl();
	if (!el || el.type !== "text") return;
	const content = (textContent.value || "").trim();
	if (!content) {
		log("Text is empty.");
		return;
	}
	saveState();
	el.text = {
		content,
		size: Number(textSize.value) || 64,
		font: textFont.value || "system-ui",
		fill: textFill.value || "#ffffff",
	};
	rerenderTextElement(el);
	redrawFinal();
	log("Text updated.");
});

textSize.addEventListener("input", () => {
	textSizeVal.textContent = textSize.value;
});

// ---------- Clear ----------
clearCropBtn.addEventListener("click", () => {
	crop = null;
	lastMagicCutout = null;
	addBtn.disabled = true;
	magicAddBtn.disabled = true;

	brush.on = false;
	brush.pos = [];
	brush.neg = [];
	brush.last = null;
	brush._strokePreview = [];
	brush._strokePreviewNeg = [];
	setCandidatesVisible(false);

	drawEditor();
	log("Selection cleared.");
});

// ---------- Set Background ----------
setBgBtn.addEventListener("click", () => {
	if (!img) return;

	const MAX = 1200;
	const shrink = Math.min(1, MAX / Math.max(img.width, img.height));
	const ew = Math.floor(img.width * shrink);
	const eh = Math.floor(img.height * shrink);

	const c = document.createElement("canvas");
	c.width = ew;
	c.height = eh;
	c.getContext("2d").drawImage(img, 0, 0, ew, eh);

	saveState();
	// Add to BACK (beginning of array)
	elements.unshift(
		ensureElementDefaults({
			type: "image",
			layout: { locked: true },
			canvas: c,
			x: 0,
			y: 0,
			scale: 1,
			rotation: 0,
		}),
	);

	activeIndex = 0;
	refreshSelect();
	redrawFinal();
	log("Image set as background (layer 0).");
});

// ---------- Mode change ----------
selectMode.addEventListener("change", () => {
	crop = null;
	addBtn.disabled = true;
	magicAddBtn.disabled = true;
	lastMagicCutout = null;

	brush.on = false;
	brush.pos = [];
	brush.neg = [];
	brush.last = null;
	brush._strokePreview = [];
	brush._strokePreviewNeg = [];
	setCandidatesVisible(false);

	drawEditor();
	log(`Mode: ${selectMode.value}`);
});

// ---------- Rectangle selection ----------
editor.addEventListener("mousedown", (e) => {
	if (!img) return;
	if (selectMode.value !== "rect") return;

	const p = getCanvasPos(e, editor);
	selecting = true;
	start = { x: p.x, y: p.y };
	crop = { x: p.x, y: p.y, w: 0, h: 0 };
	drawEditor();
});

editor.addEventListener("mousemove", (e) => {
	if (!img) return;
	if (selectMode.value !== "rect") return;
	if (!selecting || !crop) return;

	const p = getCanvasPos(e, editor);
	crop.w = p.x - start.x;
	crop.h = p.y - start.y;
	drawEditor();
});

editor.addEventListener("mouseup", () => {
	if (!img) return;
	if (selectMode.value !== "rect") return;
	if (!selecting) return;

	selecting = false;
	const r = clampRect(crop);
	if (r.w < 15 || r.h < 15) {
		addBtn.disabled = true;
		log("Crop too small. Drag a bigger rectangle.");
		return;
	}
	addBtn.disabled = false;
	log(`Rect ready. Click 'Add rectangle as element'.`);
});

addBtn.addEventListener("click", () => {
	const c = cropToElementCanvas();
	if (!c) {
		log("Failed to add element. Ensure rectangle is inside image.");
		return;
	}

	saveState(); // Save before adding
	elements.push(
		ensureElementDefaults({
			type: "image",
			canvas: c,
			x: 40 + elements.length * 20,
			y: 40 + elements.length * 20,
			scale: 1,
			rotation: 0,
		}),
	);
	activeIndex = elements.length - 1;
	refreshSelect();
	redrawFinal();
	log(`Element added (rect): #${activeIndex}`);
});

// ---------- Magic click ----------
editor.addEventListener("click", async (e) => {
	if (!img) return;
	if (selectMode.value !== "magic") return;

	if (!uploadedFileBlob) {
		log("Re-upload image.");
		return;
	}

	const p = getCanvasPos(e, editor);
	if (!isInsideRenderedImage(p)) {
		log("Click inside image area.");
		return;
	}

	const { ix, iy } = editorToImageCoords(p);
	log(`Magic click: (${ix}, ${iy})`);

	const fd = new FormData();
	fd.append("image", uploadedFileBlob, "source.png");
	fd.append("click_x", String(ix));
	fd.append("click_y", String(iy));
	fd.append("refine", JSON.stringify(getRefineParams()));

	let res;
	try {
		res = await fetch(`${BACKEND}/api/magic_select_candidates`, {
			method: "POST",
			body: fd,
		});
	} catch {
		log(`Backend request failed: ${BACKEND}`);
		return;
	}
	if (!res.ok) {
		const text = await res.text().catch(() => "");
		log(`Magic select error ${res.status}: ${text}`);
		return;
	}

	const data = await res.json().catch(() => null);
	const candidates = data?.candidates || [];
	if (!Array.isArray(candidates) || candidates.length === 0) {
		log("No candidates returned.");
		return;
	}
	magicAddBtn.disabled = true;
	lastMagicCutout = null;
	await loadCandidatesToLastMagicCutout(candidates);
});

// ---------- Magic brush (hold & paint) ----------
editor.addEventListener("mousedown", (e) => {
	if (!img) return;
	if (selectMode.value !== "brush") return;
	// Prevent context menu so right-click can be used for negative points
	if (e.button === 2) e.preventDefault();

	const p = getCanvasPos(e, editor);
	if (!isInsideRenderedImage(p)) {
		log("Brush: start inside image area.");
		return;
	}

	brush.on = true;
	brush.pos = [];
	brush.neg = [];
	brush.last = p;
	brush._strokePreview = [p];
	brush._strokePreviewNeg = [];

	const { ix, iy } = editorToImageCoords(p);
	const negMode = e.button === 2 || e.shiftKey;
	if (negMode) {
		brush.neg.push([ix, iy]);
		brush._strokePreview = [];
		brush._strokePreviewNeg = [p];
	} else {
		brush.pos.push([ix, iy]);
	}

	lastMagicCutout = null;
	magicAddBtn.disabled = true;
	setCandidatesVisible(false);

	drawEditor();
});

editor.addEventListener("mousemove", (e) => {
	if (!img) return;
	if (selectMode.value !== "brush") return;
	if (!brush.on) return;

	const p = getCanvasPos(e, editor);
	if (!isInsideRenderedImage(p)) return;

	if (brush.last && dist(p, brush.last) < BRUSH_SPACING) return;

	brush.last = p;
	const negMode = (e.buttons & 2) === 2 || e.shiftKey;
	if (negMode) {
		brush._strokePreviewNeg.push(p);
	} else {
		brush._strokePreview.push(p);
	}

	const { ix, iy } = editorToImageCoords(p);
	if (negMode) {
		brush.neg.push([ix, iy]);
	} else {
		brush.pos.push([ix, iy]);
	}

	drawEditor();
});

editor.addEventListener("mouseup", async () => {
	if (!img) return;
	if (selectMode.value !== "brush") return;
	if (!brush.on) return;

	brush.on = false;
	drawEditor();

	if (!uploadedFileBlob) {
		log("Re-upload image.");
		return;
	}
	if (brush.pos.length < 2) {
		log("Brush too short. Paint longer.");
		return;
	}

	log(`Brush points: ${brush.pos.length}. Sending...`);

	const fd = new FormData();
	fd.append("image", uploadedFileBlob, "source.png");
	fd.append("points", JSON.stringify({ pos: brush.pos, neg: brush.neg }));
	fd.append("refine", JSON.stringify(getRefineParams()));

	let res;
	try {
		res = await fetch(`${BACKEND}/api/magic_brush_candidates`, {
			method: "POST",
			body: fd,
		});
	} catch {
		log(`Backend request failed: ${BACKEND}`);
		return;
	}
	if (!res.ok) {
		const text = await res.text().catch(() => "");
		log(`Magic brush error ${res.status}: ${text}`);
		return;
	}

	const data = await res.json().catch(() => null);
	const candidates = data?.candidates || [];
	if (!Array.isArray(candidates) || candidates.length === 0) {
		log("No candidates returned.");
		return;
	}
	magicAddBtn.disabled = true;
	lastMagicCutout = null;
	await loadCandidatesToLastMagicCutout(candidates);
});

// Allow right-click erase points on brush mode
editor.addEventListener("contextmenu", (e) => {
	if (selectMode.value === "brush") e.preventDefault();
});

// Add magic element (click or brush result)
magicAddBtn.addEventListener("click", () => {
	if (!lastMagicCutout) return;

	saveState(); // Save before adding
	const pad = Number(cropPad.value) || 12;
	const cropped = autoCropCanvas(lastMagicCutout, pad);
	elements.push(
		ensureElementDefaults({
			type: "image",
			canvas: cropped,
			x: 40 + elements.length * 20,
			y: 40 + elements.length * 20,
			scale: 1,
			rotation: 0,
		}),
	);
	activeIndex = elements.length - 1;
	refreshSelect();
	redrawFinal();

	lastMagicCutout = null;
	magicAddBtn.disabled = true;
	log(`Element added (magic): #${activeIndex}`);
});

// ---------- Active selection ----------
activeSelect.addEventListener("change", (e) => {
	activeIndex = Number(e.target.value);
	selected.clear();
	selected.add(activeIndex);
	refreshSelect(); // Update sliders + selection flags
	redrawFinal();
});

// ---------- Layer & Transform Controls ----------
toFrontBtn.addEventListener("click", () => {
	if (activeIndex < 0) return;
	saveState();
	const el = elements.splice(activeIndex, 1)[0];
	elements.push(el);
	activeIndex = elements.length - 1;
	refreshSelect();
	redrawFinal();
});

toBackBtn.addEventListener("click", () => {
	if (activeIndex < 0) return;
	saveState();
	const el = elements.splice(activeIndex, 1)[0];
	elements.unshift(el);
	activeIndex = 0;
	refreshSelect();
	redrawFinal();
});

deleteBtn.addEventListener("click", () => {
	if (activeIndex < 0) return;
	saveState();
	elements.splice(activeIndex, 1);
	activeIndex = -1;
	refreshSelect();
	redrawFinal();
});

scaleRange.addEventListener("input", (e) => {
	if (activeIndex < 0) return;
	elements[activeIndex].scale = Number(e.target.value);
	scaleVal.textContent = elements[activeIndex].scale.toFixed(1);
	redrawFinal();
});
scaleRange.addEventListener("change", () => saveState());

rotRange.addEventListener("input", (e) => {
	if (activeIndex < 0) return;
	elements[activeIndex].rotation = Number(e.target.value);
	rotVal.textContent = elements[activeIndex].rotation;
	redrawFinal();
});
rotRange.addEventListener("change", () => saveState());

// ---------- Dragging on final canvas ----------
finalCanvas.addEventListener("mousedown", (e) => {
	const p = getCanvasPos(e, finalCanvas);
	const idx = hitTest(p.x, p.y);
	if (idx === -1) return;

	// Multi-select: shift toggles selection
	if (e.shiftKey) {
		if (selected.has(idx)) selected.delete(idx);
		else selected.add(idx);
		if (selected.size === 0) selected.add(idx);
		activeIndex = idx;
	} else {
		selected.clear();
		selected.add(idx);
		activeIndex = idx;
	}
	refreshSelect();

	const el = elements[idx];
	ensureElementDefaults(el);
	if (normalizeLayout(el.layout).locked) {
		log("Layer locked.");
		return;
	}

	// Group drag: move all elements in the same groupId (if any)
	let groupIndices = [idx];
	const gid = normalizeLayout(el.layout).groupId;
	if (gid) {
		groupIndices = elements
			.map((_, i) => i)
			.filter((i) => normalizeLayout(elements[i].layout).groupId === gid);
		// If any in group is locked, block drag
		if (groupIndices.some((i) => normalizeLayout(elements[i].layout).locked)) {
			log("Group has locked layer; cannot drag.");
			return;
		}
	}

	drag.on = true;
	drag.idx = idx;
	drag.ox = p.x - elements[idx].x;
	drag.oy = p.y - elements[idx].y;
	drag.group = groupIndices;
	drag.startMouse = { x: p.x, y: p.y };
	drag.startPos = groupIndices.map((i) => ({
		i,
		x: elements[i].x,
		y: elements[i].y,
	}));

	drag.startState = JSON.stringify({ x: elements[idx].x, y: elements[idx].y });
});

finalCanvas.addEventListener("mousemove", (e) => {
	if (!drag.on) return;
	const p = getCanvasPos(e, finalCanvas);
	currentGuides = { xs: [], ys: [] };

	const baseDx = p.x - drag.startMouse.x;
	const baseDy = p.y - drag.startMouse.y;

	let dx = baseDx;
	let dy = baseDy;

	// Snap based on primary dragged element
	if (snapEnable?.checked) {
		const thr = Number(snapThresh.value) || 8;
		const primary = elements[drag.idx];
		const a = getElementAABB(primary, dx, dy);

		const xTargets = [];
		const yTargets = [];

		// Canvas guides
		xTargets.push(
			{ x: 0 },
			{ x: finalCanvas.width / 2 },
			{ x: finalCanvas.width },
		);
		yTargets.push(
			{ y: 0 },
			{ y: finalCanvas.height / 2 },
			{ y: finalCanvas.height },
		);

		// Other elements guides
		elements.forEach((other, i) => {
			if (i === drag.idx) return;
			const oa = getElementAABB(other, 0, 0);
			xTargets.push({ x: oa.left }, { x: oa.cx }, { x: oa.right });
			yTargets.push({ y: oa.top }, { y: oa.cy }, { y: oa.bottom });
		});

		let bestDx = 0;
		let bestDxAbs = thr + 1;
		let bestGuideX = null;

		const candidatesX = [
			{ v: a.left, type: "left" },
			{ v: a.cx, type: "center" },
			{ v: a.right, type: "right" },
		];
		xTargets.forEach((t) => {
			candidatesX.forEach((cnd) => {
				const diff = t.x - cnd.v;
				const ad = Math.abs(diff);
				if (ad <= thr && ad < bestDxAbs) {
					bestDxAbs = ad;
					bestDx = diff;
					bestGuideX = t.x;
				}
			});
		});

		let bestDy = 0;
		let bestDyAbs = thr + 1;
		let bestGuideY = null;
		const candidatesY = [
			{ v: a.top, type: "top" },
			{ v: a.cy, type: "center" },
			{ v: a.bottom, type: "bottom" },
		];
		yTargets.forEach((t) => {
			candidatesY.forEach((cnd) => {
				const diff = t.y - cnd.v;
				const ad = Math.abs(diff);
				if (ad <= thr && ad < bestDyAbs) {
					bestDyAbs = ad;
					bestDy = diff;
					bestGuideY = t.y;
				}
			});
		});

		dx += bestDx;
		dy += bestDy;
		if (bestGuideX != null) currentGuides.xs = [bestGuideX];
		if (bestGuideY != null) currentGuides.ys = [bestGuideY];
	}

	// Apply drag to group members
	(drag.startPos || []).forEach((s) => {
		const el = elements[s.i];
		el.x = s.x + dx;
		el.y = s.y + dy;
	});
	redrawFinal();
});

finalCanvas.addEventListener("mouseup", () => {
	if (drag.on) {
		const el = elements[drag.idx];
		const start = JSON.parse(drag.startState || "{}");
		// Only save state if moved
		if (el.x !== start.x || el.y !== start.y) {
			saveState();
		}
	}
	drag.on = false;
	drag.idx = -1;
	drag.group = null;
	drag.startMouse = null;
	drag.startPos = null;
	currentGuides = { xs: [], ys: [] };
	redrawFinal();
});

// ---------- Apply style ----------
applyBtn.addEventListener("click", async () => {
	if (activeIndex < 0 || activeIndex >= elements.length) {
		log("No active element.");
		return;
	}

	saveState(); // Save before modifying
	const el = elements[activeIndex];
	ensureElementDefaults(el);
	if (el.type === "text") {
		log("Text element cannot be stylized by backend.");
		return;
	}
	const blob = await new Promise((resolve) =>
		el.canvas.toBlob(resolve, "image/png"),
	);
	if (!blob) {
		log("Failed to export element.");
		return;
	}

	const fd = new FormData();
	fd.append("image", blob, "element.png");
	fd.append(
		"params",
		JSON.stringify({
			preset: preset.value,
			sat: Number(sat.value),
			bri: Number(bri.value),
		}),
	);

	let res;
	try {
		res = await fetch(`${BACKEND}/api/stylize`, { method: "POST", body: fd });
	} catch {
		log(`Backend request failed: ${BACKEND}`);
		return;
	}
	if (!res.ok) {
		const text = await res.text().catch(() => "");
		log(`Stylize error ${res.status}: ${text}`);
		return;
	}

	const outBlob = await res.blob();
	const im = new Image();
	im.onload = () => {
		const oldW = el.canvas.width;
		const oldH = el.canvas.height;
		const cx = el.x + oldW / 2;
		const cy = el.y + oldH / 2;

		el.canvas.width = im.width;
		el.canvas.height = im.height;
		el.canvas.getContext("2d").drawImage(im, 0, 0);
		markCanvasChanged(el);
		el.x = cx - el.canvas.width / 2;
		el.y = cy - el.canvas.height / 2;
		redrawFinal();
		log(`Style applied to element #${activeIndex}.`);
	};
	im.src = URL.createObjectURL(outBlob);
});

// ---------- Export ----------
exportBtn.addEventListener("click", () => {
	// Redraw with transparent background and no selection box
	redrawFinal(true, true);

	const a = document.createElement("a");
	a.download = "composition.png";
	a.href = finalCanvas.toDataURL("image/png");
	a.click();

	// Restore normal view (black bg + selection box)
	redrawFinal(false, false);

	log("Exported composition PNG (transparent bg, no selection).");
});

// ---------- AI refine (OpenRouter) ----------
aiRefineBtn.addEventListener("click", async () => {
	// Export current composition as PNG blob and send to backend.
	redrawFinal(true, true);
	const blob = await new Promise((resolve) =>
		finalCanvas.toBlob(resolve, "image/png"),
	);
	redrawFinal(false, false);
	if (!blob) {
		log("Failed to export PNG for AI refine.");
		return;
	}

	const fd = new FormData();
	fd.append("image", blob, "composition.png");
	fd.append("user_text", aiUserText?.value || "");

	let res;
	try {
		res = await fetch(`${BACKEND}/api/ai_refine_final`, {
			method: "POST",
			body: fd,
		});
	} catch {
		log(`Backend request failed: ${BACKEND}`);
		return;
	}
	if (!res.ok) {
		const text = await res.text().catch(() => "");
		log(`AI refine error ${res.status}: ${text}`);
		return;
	}
	const outBlob = await res.blob();
	const url = URL.createObjectURL(outBlob);

	// Replace composition in UI: turn refined output into a locked background layer.
	const im = new Image();
	im.onload = () => {
		saveState(); // allow undo

		// Match canvas size to refined output (best fidelity).
		finalCanvas.width = im.width;
		finalCanvas.height = im.height;

		const c = document.createElement("canvas");
		c.width = im.width;
		c.height = im.height;
		c.getContext("2d").drawImage(im, 0, 0);

		elements = [
			ensureElementDefaults({
				type: "image",
				canvas: c,
				x: 0,
				y: 0,
				scale: 1,
				rotation: 0,
				layout: { locked: true, blendMode: "source-over", opacity: 1 },
			}),
		];
		activeIndex = 0;
		selected.clear();
		selected.add(0);
		currentGuides = { xs: [], ys: [] };
		refreshSelect();
		redrawFinal();
		log("AI refined image applied to canvas (locked background).");
	};
	im.onerror = () => {
		log("Failed to load AI refined image.");
	};
	im.src = url;
});

// ---------- Templates ----------
applyTemplateBtn.addEventListener("click", () => {
	const v = templatePreset.value || "custom";
	if (v === "custom") return;
	const m = v.match(/_(\d+)x(\d+)$/);
	if (!m) return;
	const w = Number(m[1]);
	const h = Number(m[2]);
	if (!w || !h) return;
	finalCanvas.width = w;
	finalCanvas.height = h;
	currentGuides = { xs: [], ys: [] };
	redrawFinal();
	log(`Template applied: ${w}x${h}`);
});

// ---------- Init ----------
// Initialize history with empty state
saveState();

refreshSelect();
redrawFinal();
drawEditor();
log("Ready. Start backend + frontend server, then upload an image.");
