"""Fractal-sorting matrix (FSM) construction and permutation.

Section II-B prints a recurrence with a constant factor 4 in every generation.
Taken literally, that expression ceases to be a sorting matrix after the second
generation because values overlap.  The implementation therefore uses the
sorting-preserving interpretation: each quadrant is shifted by the number of
elements in A^(k-1), i.e. 4^(k-1).  See ``docs/REPRODUCTION_NOTES.md``.
"""

from __future__ import annotations

import math
import numpy as np


def rank_group(values: np.ndarray) -> np.ndarray:
    """Convert four driving values to a 2x2 rank matrix A^(1).

    Ranks are 1-based as in the paper.  Stable sorting makes the behavior
    deterministic if finite-precision ties occur.
    """

    values = np.asarray(values, dtype=np.float64).reshape(-1)
    if values.size != 4:
        raise ValueError("FSM initialization requires exactly four values")
    order = np.argsort(values, kind="stable")
    ranks = np.empty(4, dtype=np.int64)
    ranks[order] = np.arange(1, 5, dtype=np.int64)
    return ranks.reshape(2, 2)


def fractal_sorting_matrix(a1: np.ndarray, order: int) -> np.ndarray:
    """Build A^(order), an integer permutation matrix of size 2^order square."""

    a1 = np.asarray(a1, dtype=np.int64)
    if a1.shape != (2, 2) or set(a1.ravel()) != {1, 2, 3, 4}:
        raise ValueError("a1 must be a 2x2 permutation of {1,2,3,4}")
    if order < 1:
        raise ValueError("order must be >= 1")
    current = a1.copy()
    for _ in range(2, order + 1):
        block_size = current.size  # 4^(k-1), preserves disjoint rank ranges.
        current = np.block(
            [
                [current + block_size * (a1[0, 0] - 1), current + block_size * (a1[0, 1] - 1)],
                [current + block_size * (a1[1, 0] - 1), current + block_size * (a1[1, 1] - 1)],
            ]
        )
    return current


def order_for_side(side: int) -> int:
    """Return k such that 2^k == side, or raise for unsupported sizes."""

    if side < 2 or side & (side - 1):
        raise ValueError("FSM reconstruction currently requires a power-of-two side length >= 2")
    return int(math.log2(side))


def permutation_from_matrix(matrix: np.ndarray) -> np.ndarray:
    """Convert an FSM rank matrix to zero-based target positions (paper Eq. (4))."""

    flat = np.asarray(matrix, dtype=np.int64).ravel(order="C") - 1
    n = flat.size
    if np.min(flat) != 0 or np.max(flat) != n - 1 or np.unique(flat).size != n:
        raise ValueError("FSM matrix is not a valid sorting permutation")
    return flat


def permute_spatial(image: np.ndarray, permutation: np.ndarray) -> np.ndarray:
    """Apply C2(A^(k)(i)) = C1(i) to a grayscale/RGB image."""

    h, w = image.shape[:2]
    if permutation.size != h * w:
        raise ValueError("permutation size does not match image size")
    flat = image.reshape(h * w, -1)
    out = np.empty_like(flat)
    out[permutation, :] = flat
    return out.reshape(image.shape)


def inverse_permute_spatial(image: np.ndarray, permutation: np.ndarray) -> np.ndarray:
    """Invert ``permute_spatial`` exactly."""

    h, w = image.shape[:2]
    flat = image.reshape(h * w, -1)
    restored = flat[permutation, :]
    return restored.reshape(image.shape)


def make_round_permutations(x: np.ndarray, y: np.ndarray, side: int, rounds: int) -> list[np.ndarray]:
    """Construct the per-round image FSM permutations described in Section II-B.

    The duplicated Step 1/Step 2 in the paper is treated as one Seq1 rule:
    concatenate the first half of x states with the second half of y states,
    then consume consecutive groups of four to form distinct A^(1) matrices.
    """

    needed = 4 * rounds
    if len(x) < needed or len(y) < needed:
        raise ValueError("chaotic sequences are too short for requested FSM rounds")
    half = needed // 2
    seq1 = np.concatenate([x[:half], y[half:needed]])
    order = order_for_side(side)
    permutations: list[np.ndarray] = []
    for r in range(rounds):
        a1 = rank_group(seq1[4 * r : 4 * (r + 1)])
        ak = fractal_sorting_matrix(a1, order)
        permutations.append(permutation_from_matrix(ak))
    return permutations
