"""Image I/O and input validation helpers."""

from __future__ import annotations

from pathlib import Path
import numpy as np
from PIL import Image


def load_image(path: str | Path, *, force_rgb: bool = True) -> tuple[np.ndarray, bytes]:
    """Load an image as uint8 and also return original file bytes for hash-mode experiments."""

    path = Path(path)
    raw = path.read_bytes()
    with Image.open(path) as im:
        if force_rgb:
            im = im.convert("RGB")
        elif im.mode not in {"L", "RGB"}:
            im = im.convert("RGB")
        array = np.asarray(im, dtype=np.uint8)
    return array, raw


def save_image(path: str | Path, image: np.ndarray) -> None:
    """Save uint8 image, creating parent directories."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(np.asarray(image, dtype=np.uint8)).save(path)


def validate_paper_image_shape(image: np.ndarray, *, require_square_power_of_two: bool = True) -> None:
    """Validate the geometry supported by the paper-derived FSM/FQM pipeline."""

    h, w = image.shape[:2]
    if h % 2 or w % 2:
        raise ValueError("Image dimensions must be even for 2x2 FQM blocks")
    if require_square_power_of_two:
        if h != w:
            raise ValueError("Paper-derived FSM reproduction currently requires a square image")
        if h < 2 or (h & (h - 1)):
            raise ValueError("Paper-derived FSM reproduction requires power-of-two side length")
