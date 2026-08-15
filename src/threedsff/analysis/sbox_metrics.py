"""S-box security metrics corresponding to paper Section III-A."""

from __future__ import annotations

import numpy as np


def _mapping(sbox_or_mapping: np.ndarray) -> np.ndarray:
    arr = np.asarray(sbox_or_mapping, dtype=np.uint8)
    if arr.size != 256:
        raise ValueError("S-box analysis requires exactly 256 output bytes")
    return arr.reshape(256)


def is_bijective(sbox_or_mapping: np.ndarray) -> bool:
    """Return True iff every input byte maps to a distinct output byte."""

    return np.unique(_mapping(sbox_or_mapping)).size == 256


def _fwht(values: np.ndarray) -> np.ndarray:
    a = np.asarray(values, dtype=np.int64).copy()
    h = 1
    while h < a.size:
        for i in range(0, a.size, 2 * h):
            x = a[i : i + h].copy()
            y = a[i + h : i + 2 * h].copy()
            a[i : i + h] = x + y
            a[i + h : i + 2 * h] = x - y
        h *= 2
    return a


def component_nonlinearity(sbox_or_mapping: np.ndarray) -> np.ndarray:
    """Walsh-spectrum nonlinearity of all eight output Boolean functions."""

    sbox = _mapping(sbox_or_mapping)
    result = []
    for bit in range(8):
        f = ((sbox >> bit) & 1).astype(np.int8)
        spectrum = _fwht(1 - 2 * f)
        result.append(int(128 - np.max(np.abs(spectrum)) // 2))
    return np.asarray(result, dtype=np.int64)


def sac_matrix(sbox_or_mapping: np.ndarray) -> np.ndarray:
    """Strict Avalanche Criterion matrix (input-bit x output-bit)."""

    sbox = _mapping(sbox_or_mapping)
    inputs = np.arange(256, dtype=np.uint16)
    result = np.empty((8, 8), dtype=np.float64)
    for in_bit in range(8):
        diff = np.bitwise_xor(sbox, sbox[inputs ^ (1 << in_bit)])
        for out_bit in range(8):
            result[in_bit, out_bit] = np.mean((diff >> out_bit) & 1)
    return result


def bic_nonlinearity_matrix(sbox_or_mapping: np.ndarray) -> np.ndarray:
    """Nonlinearity of XORs of output-bit pairs (standard BIC-NL measure)."""

    sbox = _mapping(sbox_or_mapping)
    bits = ((sbox[:, None] >> np.arange(8)) & 1).astype(np.int8)
    out = np.full((8, 8), np.nan, dtype=np.float64)
    for i in range(8):
        for j in range(i + 1, 8):
            f = bits[:, i] ^ bits[:, j]
            spectrum = _fwht(1 - 2 * f)
            nl = 128 - np.max(np.abs(spectrum)) // 2
            out[i, j] = out[j, i] = float(nl)
    return out


def bic_sac_matrix(sbox_or_mapping: np.ndarray) -> np.ndarray:
    """Standard BIC-SAC estimate using pairwise avalanche XORs.

    The paper reports a BIC-SAC table but does not state its computational
    formula.  This implementation uses the common definition: for each pair of
    output bits, evaluate the avalanche probability of their XOR over all eight
    single-input-bit flips.  Exact Table VI reproduction is therefore not
    asserted; see the reproduction notes.
    """

    sbox = _mapping(sbox_or_mapping)
    bits = ((sbox[:, None] >> np.arange(8)) & 1).astype(np.int8)
    inputs = np.arange(256, dtype=np.uint16)
    out = np.full((8, 8), np.nan, dtype=np.float64)
    for i in range(8):
        for j in range(i + 1, 8):
            f = bits[:, i] ^ bits[:, j]
            probs = [np.mean(f != f[inputs ^ (1 << in_bit)]) for in_bit in range(8)]
            out[i, j] = out[j, i] = float(np.mean(probs))
    return out
