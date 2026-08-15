"""XOR confusion stage from paper Eqs. (5)--(6)."""

from __future__ import annotations

import numpy as np


def confusion_mask(y: np.ndarray, height: int, width: int, scale: float = 1e10) -> np.ndarray:
    """Build Seq2 = floor(mod(y_n * 10^10, 256)) and reshape to HxW."""

    count = height * width
    if len(y) < count:
        raise ValueError("y sequence is too short for XOR confusion")
    seq2 = np.floor(np.mod(y[:count] * scale, 256)).astype(np.uint8)
    return seq2.reshape(height, width)


def xor_confuse(image: np.ndarray, mask: np.ndarray) -> np.ndarray:
    """Apply C3 = C2 XOR Seq2 (Eq. (6)); XOR is its own inverse."""

    image = np.asarray(image, dtype=np.uint8)
    if image.shape[:2] != mask.shape:
        raise ValueError("mask dimensions do not match image")
    if image.ndim == 2:
        return np.bitwise_xor(image, mask)
    return np.bitwise_xor(image, mask[:, :, None])
