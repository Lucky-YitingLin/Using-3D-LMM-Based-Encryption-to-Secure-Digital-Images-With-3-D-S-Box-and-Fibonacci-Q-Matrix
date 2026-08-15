"""Ciphertext perturbations used for cropping/noise robustness experiments."""

from __future__ import annotations

import numpy as np


def crop_ciphertext(image: np.ndarray, ratio: float, *, location: str = "center") -> np.ndarray:
    """Zero a rectangular ciphertext region occupying approximately ``ratio`` area."""

    if not (0.0 < ratio < 1.0):
        raise ValueError("ratio must be in (0,1)")
    out = np.asarray(image, dtype=np.uint8).copy()
    h, w = out.shape[:2]
    side_fraction = ratio ** 0.5
    ch = max(1, int(round(h * side_fraction)))
    cw = max(1, int(round(w * side_fraction)))
    if location == "center":
        r0, c0 = (h - ch) // 2, (w - cw) // 2
    elif location == "top_left":
        r0, c0 = 0, 0
    elif location == "left":
        r0, c0 = (h - ch) // 2, 0
    else:
        raise ValueError("location must be center, top_left, or left")
    out[r0 : r0 + ch, c0 : c0 + cw] = 0
    return out


def salt_pepper_noise(image: np.ndarray, density: float, *, seed: int = 0) -> np.ndarray:
    """Add salt-and-pepper noise at the requested pixel density."""

    if not (0.0 <= density <= 1.0):
        raise ValueError("density must be in [0,1]")
    out = np.asarray(image, dtype=np.uint8).copy()
    rng = np.random.default_rng(seed)
    h, w = out.shape[:2]
    mask = rng.random((h, w)) < density
    salt = rng.random((h, w)) < 0.5
    if out.ndim == 2:
        out[mask & salt] = 255
        out[mask & ~salt] = 0
    else:
        out[mask & salt, :] = 255
        out[mask & ~salt, :] = 0
    return out
