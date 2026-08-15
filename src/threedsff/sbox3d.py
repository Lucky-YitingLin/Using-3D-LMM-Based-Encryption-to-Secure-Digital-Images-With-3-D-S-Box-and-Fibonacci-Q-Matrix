"""3-D S-box generation and byte substitution (Section II-C, Eq. (3))."""

from __future__ import annotations

import numpy as np

from .config import CipherConfig
from .fsm import fractal_sorting_matrix, permutation_from_matrix, rank_group


def _byte_sequence(values: np.ndarray, scale: int) -> np.ndarray:
    """Paper Step 1/2 conversion: floor(mod(abs(x) * 2^10, 256))."""

    return np.floor(np.mod(np.abs(values) * scale, 256)).astype(np.uint16)


def _first_unique(values: np.ndarray, count: int = 256) -> np.ndarray:
    """Order-preserving deduplication required by Section II-C."""

    seen: set[int] = set()
    out: list[int] = []
    for value in values.tolist():
        iv = int(value)
        if iv not in seen:
            seen.add(iv)
            out.append(iv)
            if len(out) == count:
                return np.asarray(out, dtype=np.uint8)
    raise ValueError(f"Could not obtain {count} unique byte values from chaotic sequence")


def _apply_layer_permutation(sbox: np.ndarray, permutation: np.ndarray) -> np.ndarray:
    """Apply one 8x8 FSM permutation to every z-layer of the 8x8x4 S-box."""

    out = np.empty_like(sbox)
    for z in range(sbox.shape[2]):
        layer = sbox[:, :, z].reshape(-1)
        moved = np.empty_like(layer)
        moved[permutation] = layer
        out[:, :, z] = moved.reshape(8, 8)
    return out


def generate_3d_sbox(x: np.ndarray, config: CipherConfig) -> np.ndarray:
    """Generate the paper-derived 8x8x4 3D-FSM S-box.

    Reproduction choices forced by paper inconsistencies:
    - Section II-C first says 8x4x4, but Step 3, Fig. 3, and the <3:3:2>
      indexing in Fig. 4 require 8x8x4.  This implementation uses 8x8x4.
    - S22 in Step 4 is undefined.  By default this code uses the nearest
      defined index-driving sequence S12 before argsort (``s12_values``).
    - The eight "iterative operations" are implemented as eight successive
      8x8 FSM permutations applied to all four z-layers.
    """

    if len(x) <= config.sbox_index_burnin + 256:
        raise ValueError("x sequence is too short for S-box construction")

    s11 = _first_unique(_byte_sequence(x[config.sbox_fill_burnin :], config.sbox_scale))
    s12_values = _first_unique(_byte_sequence(x[config.sbox_index_burnin :], config.sbox_scale))

    # "sort ... and use as index values" is interpreted as the stable sort index.
    s12_index = np.argsort(s12_values, kind="stable")
    flat = s11[s12_index]
    sbox = flat.reshape(8, 8, 4)

    if config.sbox_undefined_s22_source != "s12_values":
        raise ValueError("Only the documented s12_values compatibility interpretation is implemented")
    perturb_source = np.concatenate([s11[:128], s12_values[128:]]).astype(np.float64)

    for r in range(config.sbox_fsm_rounds):
        group = perturb_source[4 * r : 4 * (r + 1)]
        a1 = rank_group(group)
        a3 = fractal_sorting_matrix(a1, order=3)  # 8x8, as stated in Step 4.
        perm = permutation_from_matrix(a3)
        sbox = _apply_layer_permutation(sbox, perm)
    return sbox.astype(np.uint8)


def mapping_from_3d_sbox(sbox: np.ndarray) -> np.ndarray:
    """Return the 256-entry byte substitution represented by an 8x8x4 S-box."""

    if sbox.shape != (8, 8, 4):
        raise ValueError("S-box must have shape (8, 8, 4)")
    inputs = np.arange(256, dtype=np.uint16)
    m = inputs >> 5
    n = (inputs >> 2) & 0x7
    z = inputs & 0x3
    return sbox[m, n, z].astype(np.uint8)


def inverse_mapping(mapping: np.ndarray) -> np.ndarray:
    """Build the inverse byte lookup table; bijectivity is required for decryption."""

    mapping = np.asarray(mapping, dtype=np.uint8).reshape(256)
    if np.unique(mapping).size != 256:
        raise ValueError("S-box is not bijective; decryption is undefined")
    inv = np.empty(256, dtype=np.uint8)
    inv[mapping] = np.arange(256, dtype=np.uint8)
    return inv


def substitute(image: np.ndarray, sbox: np.ndarray) -> np.ndarray:
    """Apply the <3:3:2> index split in Fig. 4 / paper Eq. (3)."""

    values = np.asarray(image, dtype=np.uint8)
    m = values >> 5
    n = (values >> 2) & 0x7
    z = values & 0x3
    return sbox[m, n, z]


def inverse_substitute(image: np.ndarray, sbox: np.ndarray) -> np.ndarray:
    """Invert the S-box substitution using its reconstructed 256-byte mapping."""

    inv = inverse_mapping(mapping_from_3d_sbox(sbox))
    return inv[np.asarray(image, dtype=np.uint8)]
