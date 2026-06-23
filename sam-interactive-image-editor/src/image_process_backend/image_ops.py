from PIL import Image, ImageEnhance
import numpy as np
import cv2


class StyleProcessor:
    @staticmethod
    def apply_style(image, style_name):
        """Apply preset style using OpenCV"""
        if style_name == "sketch":
            return StyleProcessor.sketch_style(image)
        elif style_name == "watercolor":
            return StyleProcessor.watercolor_style(image)
        elif style_name == "oil":
            return StyleProcessor.oil_painting_style(image)
        elif style_name == "vintage":
            return StyleProcessor.vintage_style(image)
        elif style_name == "gray":
            return StyleProcessor.grayscale_style(image)
        elif style_name == "cartoon":
            return StyleProcessor.cartoon_style(image)
        else:
            return image

    @staticmethod
    def sketch_style(image):
        """Sketch style"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        inverted = 255 - gray
        blur = cv2.GaussianBlur(inverted, (21, 21), 0)
        inverted_blur = 255 - blur
        # Avoid division by zero
        sketch = cv2.divide(gray, inverted_blur, scale=256.0)
        return cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)

    @staticmethod
    def watercolor_style(image):
        """Watercolor style"""
        try:
            # sigma_s controls the size of the neighborhood. Range 1 - 200
            # sigma_r controls the how dissimilar colors within the neighborhood will be averaged. Range 0 - 1
            watercolor = cv2.stylization(image, sigma_s=60, sigma_r=0.6)
        except Exception:
            # Fallback if stylization not available in this opencv build
            watercolor = cv2.bilateralFilter(image, 9, 75, 75)

        # Enhance edges
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 2
        )
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        # Blend
        return cv2.addWeighted(watercolor, 0.9, edges, 0.1, 0)

    @staticmethod
    def oil_painting_style(image):
        """Oil painting style"""
        # pyrMeanShiftFiltering
        res = cv2.pyrMeanShiftFiltering(image, 20, 50, 3)
        return res

    @staticmethod
    def vintage_style(image):
        """Vintage / Sepia style"""
        # Standard sepia filter matrix
        kernel = np.array([[0.272, 0.534, 0.131], [0.349, 0.686, 0.168], [0.393, 0.769, 0.189]])
        # cv2.transform applies matrix to each pixel
        return cv2.transform(image, kernel)

    @staticmethod
    def grayscale_style(image):
        """Grayscale style"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    @staticmethod
    def cartoon_style(image):
        """Cartoon style"""
        num_down = 2
        num_bilateral = 7

        img_color = image
        for _ in range(num_down):
            img_color = cv2.pyrDown(img_color)

        for _ in range(num_bilateral):
            img_color = cv2.bilateralFilter(img_color, d=9, sigmaColor=9, sigmaSpace=7)

        for _ in range(num_down):
            img_color = cv2.pyrUp(img_color)

        if img_color.shape[:2] != image.shape[:2]:
            img_color = cv2.resize(img_color, (image.shape[1], image.shape[0]))

        img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        img_blur = cv2.medianBlur(img_gray, 7)

        edges = cv2.adaptiveThreshold(
            img_blur,
            255,
            cv2.ADAPTIVE_THRESH_MEAN_C,
            cv2.THRESH_BINARY,
            9,
            2,
        )
        edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

        cartoon = cv2.bitwise_and(img_color, edges)
        return cartoon


def stylize(
    img: Image.Image, preset: str = "none", sat: float = 1.0, bri: float = 1.0
) -> Image.Image:
    """
    Apply preset + saturation + brightness (non-destructive to alpha channel).
    """
    # 1. Separate Alpha
    base = img.convert("RGBA")
    arr = np.array(base)
    alpha = arr[..., 3]
    rgb = arr[..., :3]

    # 2. Convert RGB (PIL) to BGR (OpenCV)
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

    # 3. Apply Style
    preset = (preset or "none").lower()
    styled_bgr = bgr

    if preset in ["sketch", "watercolor", "oil", "vintage", "gray", "cartoon"]:
        styled_bgr = StyleProcessor.apply_style(bgr, preset)
    elif preset == "warm":
        styled_bgr = bgr.astype(np.float32)
        styled_bgr[..., 2] *= 1.15  # R
        styled_bgr[..., 0] *= 0.9  # B
        styled_bgr = np.clip(styled_bgr, 0, 255).astype(np.uint8)
    elif preset == "cold":
        styled_bgr = bgr.astype(np.float32)
        styled_bgr[..., 0] *= 1.15  # B
        styled_bgr[..., 2] *= 0.9  # R
        styled_bgr = np.clip(styled_bgr, 0, 255).astype(np.uint8)
    elif preset == "vivid":
        hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[..., 1] *= 1.2  # Saturation
        hsv[..., 2] *= 1.1  # Value
        hsv = np.clip(hsv, 0, 255).astype(np.uint8)
        styled_bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    # 4. Convert back to RGB (PIL)
    styled_rgb_arr = cv2.cvtColor(styled_bgr, cv2.COLOR_BGR2RGB)
    styled_rgb = Image.fromarray(styled_rgb_arr)

    # 5. Apply Saturation / Brightness (using PIL)
    if sat != 1.0:
        styled_rgb = ImageEnhance.Color(styled_rgb).enhance(sat)
    if bri != 1.0:
        styled_rgb = ImageEnhance.Brightness(styled_rgb).enhance(bri)

    # 6. Recombine with Alpha
    final_rgb_arr = np.array(styled_rgb)
    # Ensure shapes match
    if final_rgb_arr.shape[:2] != alpha.shape:
        final_rgb_arr = cv2.resize(final_rgb_arr, (alpha.shape[1], alpha.shape[0]))

    out_arr = np.dstack([final_rgb_arr, alpha])

    return Image.fromarray(out_arr, mode="RGBA")
