from enum import Enum
from PIL import Image
import numpy as np

class DitherAlgorithm(Enum):
    ATKINSON = 1
    FLOYD_STEINBERG = 2

class ImageProcessor:
    def __init__(self):
        # The Spectra 6 Palette
        # Black, White, Green, Blue, Red, Yellow, Orange
        self.palette = [
            (0, 0, 0),       # Black
            (255, 255, 255), # White
            (0, 255, 0),     # Green
            (0, 0, 255),     # Blue
            (255, 0, 0),     # Red
            (255, 255, 0),   # Yellow
            (255, 128, 0)    # Orange
        ]

    def _get_luma(self, r, g, b):
        return r * 0.250 + g * 0.350 + b * 0.400

    def _color_distance(self, c1, c2):
        r1, g1, b1 = c1
        r2, g2, b2 = c2
        
        # Asymmetric RGB distance
        rgb_dist = np.sqrt(0.250 * ((r1 - r2) ** 2) +
                           0.350 * ((g1 - g2) ** 2) +
                           0.400 * ((b1 - b2) ** 2)) * 0.75
        
        luma1 = self._get_luma(r1, g1, b1)
        luma2 = self._get_luma(r2, g2, b2)
        luma_dist = abs(luma1 - luma2)
        
        # Total distance formula
        return 1.5 * rgb_dist + 0.60 * luma_dist

    def _closest_color(self, py_color):
        min_dist = float('inf')
        closest = self.palette[0]
        for p_color in self.palette:
            d = self._color_distance(py_color, p_color)
            if d < min_dist:
                min_dist = d
                closest = p_color
        return closest

    def crop_image(self, img: Image.Image, box: tuple) -> Image.Image:
        """Crop the image down to the specified box."""
        return img.crop(box)

    def slice_image(self, img: Image.Image, layout: dict) -> dict:
        """Slice the dithered image into multiple smaller images based on the layout offsets."""
        slices = {}
        for disp in layout.get("displays", []):
            d_id = disp["id"]
            x = disp["x_offset"]
            y = disp["y_offset"]
            w = disp["width"]
            h = disp["height"]
            slices[d_id] = img.crop((x, y, x + w, y + h))
        return slices

    def dither(self, img: Image.Image, alg: DitherAlgorithm) -> Image.Image:
        """Apply Spectra 6 specific dithering."""
        # Convert to numpy array for fast manipulation
        img = img.convert('RGB')
        arr = np.array(img, dtype=float)
        h, w, _ = arr.shape
        
        for y in range(h):
            for x in range(w):
                old_pixel = arr[y, x].copy()
                new_pixel = self._closest_color(old_pixel)
                arr[y, x] = new_pixel
                
                quant_error = old_pixel - new_pixel
                
                if alg == DitherAlgorithm.ATKINSON:
                    # Atkinson uses 1/8 for all weights, total 5/8
                    # right, bottom-left, bottom, bottom-right, right-right, bottom-bottom
                    # Wait, the repo noted: "forward-only error distribution approach for speed. Error is only distributed to not-yet-processed pixels (right and down directions) with the following weights: Right: 1/8, Bottom-left: 1/8, Bottom: 1/4, Bottom-right: 1/8"
                    if x + 1 < w:
                        arr[y, x + 1] += quant_error * (1/8)
                    if y + 1 < h:
                        if x - 1 >= 0:
                            arr[y + 1, x - 1] += quant_error * (1/8)
                        arr[y + 1, x] += quant_error * (1/4)
                        if x + 1 < w:
                            arr[y + 1, x + 1] += quant_error * (1/8)
                            
                elif alg == DitherAlgorithm.FLOYD_STEINBERG:
                    # standard FS: right 7/16, bot-left 3/16, bot 5/16, bot-right 1/16
                    if x + 1 < w:
                        arr[y, x + 1] += quant_error * (7/16)
                    if y + 1 < h:
                        if x - 1 >= 0:
                            arr[y + 1, x - 1] += quant_error * (3/16)
                        arr[y + 1, x] += quant_error * (5/16)
                        if x + 1 < w:
                            arr[y + 1, x + 1] += quant_error * (1/16)
                            
        # Clip max/min
        arr = np.clip(arr, 0, 255)
        return Image.fromarray(np.uint8(arr), 'RGB')
