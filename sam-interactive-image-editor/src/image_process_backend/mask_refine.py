from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import cv2


@dataclass
class RefineParams:
    # Positive = dilate, Negative = erode
    expand: int = 0
    # Morphology smoothing radius (close+open)
    smooth: int = 0
    # Blur radius (Gaussian) applied to alpha
    feather: int = 0
    # Fill interior holes in binary mask
    fill_holes: bool = True
    # Remove connected components smaller than this area (0 disables)
    remove_islands_min_area: int = 0
    # Edge decontamination via inpainting (reduces background bleed on semi-transparent edges)
    decontam: bool = False
    decontam_threshold: int = 220  # alpha < threshold considered "edge"
    decontam_radius: int = 3


def _odd_ksize(r: int) -> int:
    r = int(max(0, r))
    return r * 2 + 1 if r > 0 else 1


def _kernel(r: int) -> np.ndarray:
    k = _odd_ksize(r)
    return cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k))


def _to_u8_mask(mask_u8: np.ndarray) -> np.ndarray:
    m = mask_u8
    if m.ndim == 3:
        m = m[..., 0]
    if m.dtype != np.uint8:
        m = m.astype(np.uint8)
    # Normalize to {0,255}
    if m.max() <= 1:
        m = m * 255
    return m


def fill_holes(mask_u8: np.ndarray) -> np.ndarray:
    """
    Fill holes in a binary mask using flood fill on the inverted mask.
    """
    m = _to_u8_mask(mask_u8)
    h, w = m.shape[:2]

    inv = cv2.bitwise_not(m)
    flood = inv.copy()
    ff_mask = np.zeros((h + 2, w + 2), dtype=np.uint8)
    cv2.floodFill(flood, ff_mask, (0, 0), 0)  # fill background in inverted space

    holes = cv2.bitwise_not(flood)  # remaining non-background in inverted space = holes
    filled = cv2.bitwise_or(m, holes)
    return filled


def remove_small_islands(mask_u8: np.ndarray, min_area: int) -> np.ndarray:
    """
    Remove connected components smaller than min_area.
    """
    m = _to_u8_mask(mask_u8)
    min_area = int(max(0, min_area))
    if min_area <= 0:
        return m

    bin01 = (m > 0).astype(np.uint8)
    num, labels, stats, _ = cv2.connectedComponentsWithStats(bin01, connectivity=8)
    if num <= 1:
        return m

    out = np.zeros_like(bin01)
    for i in range(1, num):
        area = int(stats[i, cv2.CC_STAT_AREA])
        if area >= min_area:
            out[labels == i] = 1
    return (out * 255).astype(np.uint8)


def refine_mask(mask_u8: np.ndarray, p: RefineParams) -> np.ndarray:
    """
    Produce a refined alpha mask uint8 [0..255].
    """
    m = _to_u8_mask(mask_u8)

    # Expand / shrink
    if p.expand > 0:
        m = cv2.dilate(m, _kernel(p.expand), iterations=1)
    elif p.expand < 0:
        m = cv2.erode(m, _kernel(abs(p.expand)), iterations=1)

    # Smooth (close then open)
    if p.smooth > 0:
        k = _kernel(p.smooth)
        m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, k, iterations=1)
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, k, iterations=1)

    if p.fill_holes:
        m = fill_holes(m)

    if p.remove_islands_min_area > 0:
        m = remove_small_islands(m, p.remove_islands_min_area)

    # Feather / soften alpha
    if p.feather > 0:
        k = _odd_ksize(p.feather)
        m = cv2.GaussianBlur(m, (k, k), sigmaX=0, sigmaY=0)

    return m.astype(np.uint8)


def decontaminate_rgb(
    rgb_u8: np.ndarray, alpha_u8: np.ndarray, threshold: int, radius: int
) -> np.ndarray:
    """
    Reduce background color bleed near semi-transparent edges via inpainting.
    """
    a = _to_u8_mask(alpha_u8)
    thr = int(np.clip(threshold, 1, 254))
    r = int(max(1, radius))

    # Only inpaint on edge pixels (semi-transparent)
    inpaint_mask = ((a > 0) & (a < thr)).astype(np.uint8) * 255
    if inpaint_mask.max() == 0:
        return rgb_u8

    # cv2.inpaint expects 8-bit 3-channel
    bgr = cv2.cvtColor(rgb_u8, cv2.COLOR_RGB2BGR)
    bgr2 = cv2.inpaint(bgr, inpaint_mask, inpaintRadius=r, flags=cv2.INPAINT_TELEA)
    return cv2.cvtColor(bgr2, cv2.COLOR_BGR2RGB)
