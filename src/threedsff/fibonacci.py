"""Fibonacci Q-matrix block transformation (Section II-D, Eqs. (7)--(12))."""

from __future__ import annotations

from functools import lru_cache
import numpy as np


_Q = np.array([[1, 1], [1, 0]], dtype=np.int64)
_Q_INV_MOD_256 = np.array([[0, 1], [1, -1]], dtype=np.int64) % 256


def _matmul2_mod(a: np.ndarray, b: np.ndarray, modulus: int) -> np.ndarray:
    return (a.astype(np.int64) @ b.astype(np.int64)) % modulus


def matrix_power_mod(base: np.ndarray, exponent: int, modulus: int = 256) -> np.ndarray:
    """Fast 2x2 matrix power in Z_modulus."""

    if exponent < 0:
        raise ValueError("exponent must be non-negative")
    result = np.eye(2, dtype=np.int64)
    power = np.asarray(base, dtype=np.int64) % modulus
    n = int(exponent)
    while n:
        if n & 1:
            result = _matmul2_mod(result, power, modulus)
        power = _matmul2_mod(power, power, modulus)
        n >>= 1
    return result % modulus


@lru_cache(maxsize=64)
def q_power_mod(exponent: int, modulus: int = 256) -> tuple[tuple[int, int], tuple[int, int]]:
    """Return Q^n mod 256.

    Paper Eq. (8) is interpreted using the standard Fibonacci identity
    Q^n = [[F_(n+1), F_n], [F_n, F_(n-1)]], rather than exponentiating that
    already-powered Fibonacci matrix a second time.
    """

    m = matrix_power_mod(_Q, int(exponent), modulus)
    return tuple(map(tuple, m.tolist()))  # hashable cache result


@lru_cache(maxsize=64)
def q_inverse_power_mod(exponent: int, modulus: int = 256) -> tuple[tuple[int, int], tuple[int, int]]:
    """Return Q^{-n} mod 256 for decryption (paper Eq. (9))."""

    m = matrix_power_mod(_Q_INV_MOD_256, int(exponent), modulus)
    return tuple(map(tuple, m.tolist()))


def fqm_iteration_values(z: np.ndarray, count: int, *, scale: float = 1e10, residue_modulus: int = 64) -> np.ndarray:
    """Generate the even Seq3 values specified in paper Eq. (10)."""

    raw = np.floor(np.mod(z * scale, residue_modulus)).astype(np.int64)
    even = raw[(raw % 2) == 0]
    if even.size < count:
        raise ValueError(f"Need {count} even Seq3 values but obtained only {even.size}")
    return even[:count]


def _blocks_from_image(image: np.ndarray) -> tuple[np.ndarray, int, int, bool]:
    image = np.asarray(image, dtype=np.uint8)
    squeeze = image.ndim == 2
    if squeeze:
        image = image[:, :, None]
    h, w, c = image.shape
    if h % 2 or w % 2:
        raise ValueError("FQM requires even image height and width (2x2 blocks)")
    blocks = (
        image.reshape(h // 2, 2, w // 2, 2, c)
        .transpose(0, 2, 1, 3, 4)
        .reshape(-1, 2, 2, c)
    )
    return blocks, h, w, squeeze


def _image_from_blocks(blocks: np.ndarray, h: int, w: int, squeeze: bool) -> np.ndarray:
    c = blocks.shape[-1]
    image = (
        blocks.reshape(h // 2, w // 2, 2, 2, c)
        .transpose(0, 2, 1, 3, 4)
        .reshape(h, w, c)
        .astype(np.uint8)
    )
    return image[:, :, 0] if squeeze else image


def _q_stack(exponents: np.ndarray, inverse: bool) -> np.ndarray:
    mats = []
    fn = q_inverse_power_mod if inverse else q_power_mod
    for n in exponents.tolist():
        mats.append(np.asarray(fn(int(n)), dtype=np.int64))
    return np.stack(mats, axis=0)


def fqm_transform(image: np.ndarray, exponents: np.ndarray, *, inverse: bool = False, modulus: int = 256) -> np.ndarray:
    """Encrypt/decrypt all 2x2 blocks with a chaos-selected Q^n matrix.

    Each spatial block reuses the same exponent for R/G/B, matching the paper's
    statement that the same treatment is applied separately to all channels.
    """

    blocks, h, w, squeeze = _blocks_from_image(image)
    if len(exponents) != blocks.shape[0]:
        raise ValueError("one FQM exponent is required per spatial 2x2 block")
    q = _q_stack(np.asarray(exponents), inverse=inverse)
    transformed = np.einsum("bikc,bkj->bijc", blocks.astype(np.int64), q, optimize=True) % modulus
    return _image_from_blocks(transformed, h, w, squeeze)
