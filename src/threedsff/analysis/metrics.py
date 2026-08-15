"""Image security metrics used in Section III-C/F/G of the paper."""

from __future__ import annotations

import math
from typing import Iterable
import numpy as np


def _as_channels(image: np.ndarray) -> np.ndarray:
    image = np.asarray(image, dtype=np.uint8)
    return image[:, :, None] if image.ndim == 2 else image


def information_entropy(image: np.ndarray) -> np.ndarray:
    """Shannon entropy per channel, corresponding to paper Eq. (19)."""

    chans = _as_channels(image)
    result = []
    for c in range(chans.shape[2]):
        counts = np.bincount(chans[:, :, c].ravel(), minlength=256).astype(np.float64)
        p = counts[counts > 0] / counts.sum()
        result.append(float(-(p * np.log2(p)).sum()))
    return np.asarray(result)


def npcr_uaci(cipher1: np.ndarray, cipher2: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """NPCR (%) and UACI (%) per channel, matching paper Eq. (16)."""

    a, b = _as_channels(cipher1), _as_channels(cipher2)
    if a.shape != b.shape:
        raise ValueError("images must have identical shapes")
    npcr = np.mean(a != b, axis=(0, 1)) * 100.0
    uaci = np.mean(np.abs(a.astype(np.int16) - b.astype(np.int16)) / 255.0, axis=(0, 1)) * 100.0
    return npcr, uaci


def _pair_vectors(channel: np.ndarray, direction: str) -> tuple[np.ndarray, np.ndarray]:
    if direction == "horizontal":
        return channel[:, :-1].ravel(), channel[:, 1:].ravel()
    if direction == "vertical":
        return channel[:-1, :].ravel(), channel[1:, :].ravel()
    if direction == "diagonal":
        return channel[:-1, :-1].ravel(), channel[1:, 1:].ravel()
    if direction == "anti_diagonal":
        return channel[:-1, 1:].ravel(), channel[1:, :-1].ravel()
    raise ValueError(f"unknown direction: {direction}")


def adjacent_correlation(image: np.ndarray, directions: Iterable[str] = ("horizontal", "vertical", "diagonal", "anti_diagonal")) -> dict[str, np.ndarray]:
    """Pearson adjacent-pixel correlation per channel (paper Eq. (18))."""

    chans = _as_channels(image)
    out: dict[str, np.ndarray] = {}
    for direction in directions:
        values = []
        for c in range(chans.shape[2]):
            x, y = _pair_vectors(chans[:, :, c].astype(np.float64), direction)
            x -= x.mean()
            y -= y.mean()
            denom = math.sqrt(float(np.mean(x * x) * np.mean(y * y)))
            values.append(float(np.mean(x * y) / denom) if denom else float("nan"))
        out[direction] = np.asarray(values)
    return out


def ssim_global(image1: np.ndarray, image2: np.ndarray, c1: float = 6.5025, c2: float = 58.5225) -> float:
    """Global SSIM using the exact constants printed in paper Eq. (17).

    The paper writes the standard local-statistics SSIM formula but does not
    state a window size.  This deterministic global variant is used for the
    iteration study unless scikit-image is selected by an experiment script.
    """

    x = np.asarray(image1, dtype=np.float64)
    y = np.asarray(image2, dtype=np.float64)
    if x.shape != y.shape:
        raise ValueError("images must have the same shape")
    mux, muy = float(x.mean()), float(y.mean())
    varx, vary = float(x.var()), float(y.var())
    cov = float(np.mean((x - mux) * (y - muy)))
    return ((2 * mux * muy + c1) * (2 * cov + c2)) / ((mux * mux + muy * muy + c1) * (varx + vary + c2))
