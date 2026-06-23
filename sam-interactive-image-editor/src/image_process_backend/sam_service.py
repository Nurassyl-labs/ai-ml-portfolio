import io
import numpy as np
import cv2
import torch
from PIL import Image

from segment_anything import sam_model_registry, SamPredictor


class SAMService:
    def __init__(self, checkpoint_path: str, model_type: str = "vit_b", device: str | None = None):
        """
        model_type: 'vit_b' | 'vit_l' | 'vit_h'
        """
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        self.device = device

        sam = sam_model_registry[model_type](checkpoint=checkpoint_path)
        sam.to(device=self.device)
        self.predictor = SamPredictor(sam)

    @staticmethod
    def _pil_to_bgr_uint8(pil: Image.Image) -> np.ndarray:
        rgb = np.array(pil.convert("RGB"), dtype=np.uint8)
        bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
        return bgr

    def _set_image(self, pil_image: Image.Image):
        bgr = self._pil_to_bgr_uint8(pil_image)
        rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
        self.predictor.set_image(rgb)

    def predict_mask_from_point(
        self,
        pil_image: Image.Image,
        point_xy: tuple[int, int],
        point_label: int = 1,
        multimask: bool = True,
    ) -> np.ndarray:
        """
        Single point prompting.
        Returns mask as uint8 array {0,255}.
        """
        self._set_image(pil_image)

        input_point = np.array([point_xy], dtype=np.float32)
        input_label = np.array([point_label], dtype=np.int32)

        masks, scores, _ = self.predictor.predict(
            point_coords=input_point,
            point_labels=input_label,
            multimask_output=multimask,
        )

        best_idx = int(np.argmax(scores))
        return masks[best_idx].astype(np.uint8) * 255

    def predict_masks_from_point(
        self,
        pil_image: Image.Image,
        point_xy: tuple[int, int],
        point_label: int = 1,
        multimask: bool = True,
    ) -> tuple[list[np.ndarray], list[float]]:
        """
        Single point prompting.
        Returns (masks_u8, scores) where masks_u8 are uint8 {0,255}.
        """
        self._set_image(pil_image)

        input_point = np.array([point_xy], dtype=np.float32)
        input_label = np.array([point_label], dtype=np.int32)

        masks, scores, _ = self.predictor.predict(
            point_coords=input_point,
            point_labels=input_label,
            multimask_output=multimask,
        )
        masks_u8 = [(m.astype(np.uint8) * 255) for m in masks]
        return masks_u8, [float(s) for s in scores]

    def predict_mask_from_points(
        self,
        pil_image: Image.Image,
        points_xy: list[tuple[int, int]],
        labels: list[int],
        multimask: bool = True,
    ) -> np.ndarray:
        """
        Multi-point prompting (brush).
        points_xy: [(x,y), ...]
        labels: [1,1,1,0,0,...] (1=foreground, 0=background)
        Returns mask {0,255}.
        """
        self._set_image(pil_image)

        input_points = np.array(points_xy, dtype=np.float32)
        input_labels = np.array(labels, dtype=np.int32)

        masks, scores, _ = self.predictor.predict(
            point_coords=input_points,
            point_labels=input_labels,
            multimask_output=multimask,
        )

        best_idx = int(np.argmax(scores))
        return masks[best_idx].astype(np.uint8) * 255

    def predict_masks_from_points(
        self,
        pil_image: Image.Image,
        points_xy: list[tuple[int, int]],
        labels: list[int],
        multimask: bool = True,
    ) -> tuple[list[np.ndarray], list[float]]:
        """
        Multi-point prompting (brush).
        Returns (masks_u8, scores) where masks_u8 are uint8 {0,255}.
        """
        self._set_image(pil_image)

        input_points = np.array(points_xy, dtype=np.float32)
        input_labels = np.array(labels, dtype=np.int32)

        masks, scores, _ = self.predictor.predict(
            point_coords=input_points,
            point_labels=input_labels,
            multimask_output=multimask,
        )
        masks_u8 = [(m.astype(np.uint8) * 255) for m in masks]
        return masks_u8, [float(s) for s in scores]

    @staticmethod
    def cutout_rgba(pil_image: Image.Image, mask_u8: np.ndarray) -> Image.Image:
        """
        Create RGBA cutout. Also clears RGB where alpha==0 to avoid dark/dirty fringes
        after canvas scaling (premultiplied alpha artifacts).
        """
        img_rgba = pil_image.convert("RGBA")
        arr = np.array(img_rgba, dtype=np.uint8)

        alpha = mask_u8
        if alpha.ndim == 3:
            alpha = alpha[..., 0]
        alpha = alpha.astype(np.uint8)

        arr[..., 3] = alpha

        # IMPORTANT: clear RGB for fully transparent pixels
        transparent = alpha == 0
        arr[transparent, 0] = 0
        arr[transparent, 1] = 0
        arr[transparent, 2] = 0

        return Image.fromarray(arr, mode="RGBA")

    @staticmethod
    def encode_png(pil: Image.Image) -> bytes:
        buf = io.BytesIO()
        pil.save(buf, format="PNG", optimize=True)
        return buf.getvalue()
