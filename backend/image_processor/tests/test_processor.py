import pytest
from PIL import Image
import numpy as np
from src.processor import ImageProcessor, DitherAlgorithm

@pytest.fixture
def dummy_image():
    # Create a simple 1600x480 RGB image (e.g., matching a 2x1 grid of 800x480 displays)
    img = Image.new("RGB", (1600, 480))
    # Give it a simple gradient or some colors
    pixels = img.load()
    for x in range(1600):
        for y in range(480):
            pixels[x, y] = (x % 256, (x+y) % 256, y % 256)
    return img

def test_spectra6_palette_colors():
    """Verify that the Spectra 6 palette contains the 7 intended colors."""
    proc = ImageProcessor()
    assert len(proc.palette) == 7
    # Expected: Black, White, Green, Blue, Red, Yellow, Orange
    # (Checking expected types rather than exact values unless we know them precisely)
    assert (0, 0, 0) in proc.palette # Black
    assert (255, 255, 255) in proc.palette # White

def test_crop_image(dummy_image):
    proc = ImageProcessor()
    # Crop the right half
    crop_box = (800, 0, 1600, 480)
    cropped = proc.crop_image(dummy_image, crop_box)
    assert cropped.size == (800, 480)

def test_slice_image(dummy_image):
    proc = ImageProcessor()
    
    # 2 columns, 1 row layout, display sizes 800x480
    layout = {
        "displays": [
            {"id": "disp_1", "x_offset": 0, "y_offset": 0, "width": 800, "height": 480},
            {"id": "disp_2", "x_offset": 800, "y_offset": 0, "width": 800, "height": 480}
        ]
    }
    
    slices = proc.slice_image(dummy_image, layout)
    
    assert len(slices) == 2
    assert "disp_1" in slices
    assert "disp_2" in slices
    assert slices["disp_1"].size == (800, 480)
    assert slices["disp_2"].size == (800, 480)

def test_dithering_atkinson(dummy_image):
    proc = ImageProcessor()
    # Use Atkinson algorithm
    dithered = proc.dither(dummy_image, alg=DitherAlgorithm.ATKINSON)
    
    # Output should use only palette colors
    img_data = np.array(dithered)
    assert img_data.shape == (480, 1600, 3)
    
    # Take a sample pixel, ensure it's in the palette
    pixel_tuple = tuple(img_data[0, 0])
    assert pixel_tuple in proc.palette

def test_dithering_floyd_steinberg(dummy_image):
    proc = ImageProcessor()
    # Use Floyd-Steinberg algorithm
    dithered = proc.dither(dummy_image, alg=DitherAlgorithm.FLOYD_STEINBERG)
    
    # Output should use only palette colors
    img_data = np.array(dithered)
    assert img_data.shape == (480, 1600, 3)
    
    # Take a sample pixel, ensure it's in the palette
    pixel_tuple = tuple(img_data[0, 0])
    assert pixel_tuple in proc.palette
