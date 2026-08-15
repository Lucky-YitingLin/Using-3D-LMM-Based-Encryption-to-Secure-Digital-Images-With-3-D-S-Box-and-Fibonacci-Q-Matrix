"""Plaintext-bound key derivation described in Section II-A.

The paper derives the three initial states of 3D-LMM from SHA-512 of the
plaintext image.  It does not define a serialized key format for decryption;
this project therefore stores the derived initial states and the exact config
used in a small JSON sidecar.  That sidecar is *key material* and should be
shared only through the secure mechanism assumed by the paper.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np

from .config import CipherConfig


@dataclass(frozen=True)
class KeyMaterial:
    """Derived information required to regenerate all chaotic sequences."""

    sha512: str
    sample_x: str
    sample_y: str
    sample_z: str
    x0: float
    y0: float
    z0: float
    hash_mode: str
    hash_normalization: str
    config: dict[str, Any]

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2, sort_keys=True)
            f.write("\n")

    @classmethod
    def load(cls, path: str | Path) -> "KeyMaterial":
        with Path(path).open("r", encoding="utf-8") as f:
            return cls(**json.load(f))


def _hash_plaintext(image: np.ndarray, mode: str, file_bytes: bytes | None = None) -> str:
    """Return the SHA-512 digest used by the plaintext-binding stage.

    The paper says to hash the plaintext image but does not state whether file
    bytes (which include format metadata) or decoded pixel values are hashed.
    ``pixel_bytes`` is the deterministic default; ``file_bytes`` is available
    when a caller needs that alternative interpretation.
    """

    if mode == "pixel_bytes":
        payload = np.ascontiguousarray(image, dtype=np.uint8).tobytes(order="C")
    elif mode == "file_bytes":
        if file_bytes is None:
            raise ValueError("hash_mode='file_bytes' requires the original file bytes")
        payload = file_bytes
    else:
        raise ValueError(f"Unsupported hash_mode: {mode}")
    return hashlib.sha512(payload).hexdigest()


def _normalize_sample(sample: str, config: CipherConfig) -> float:
    value = int(sample, 16)
    if config.hash_normalization == "paper_literal":
        return value / config.hash_divisor
    if config.hash_normalization == "hex_unit_interval":
        return value / float(16**len(sample))
    if config.hash_normalization == "paper_modulo_interval":
        return (value % int(config.hash_divisor)) / config.hash_divisor
    raise ValueError(f"Unsupported hash_normalization: {config.hash_normalization}")


def derive_key_material(
    image: np.ndarray,
    config: CipherConfig,
    *,
    file_bytes: bytes | None = None,
) -> KeyMaterial:
    """Derive x0, y0, z0 from SHA-512 exactly following the sampling pattern.

    Section II-A, Step 2 takes every eighth hexadecimal character beginning at
    offsets 1, 2, and 3 in one-based notation.  With Python's zero-based
    indexing these are digest[0::8], digest[1::8], and digest[2::8].
    """

    digest = _hash_plaintext(image, config.hash_mode, file_bytes=file_bytes)
    sx, sy, sz = digest[0::8], digest[1::8], digest[2::8]
    if not (len(sx) == len(sy) == len(sz) == 16):
        raise AssertionError("SHA-512 sampling should produce three 16-character strings")
    return KeyMaterial(
        sha512=digest,
        sample_x=sx,
        sample_y=sy,
        sample_z=sz,
        x0=_normalize_sample(sx, config),
        y0=_normalize_sample(sy, config),
        z0=_normalize_sample(sz, config),
        hash_mode=config.hash_mode,
        hash_normalization=config.hash_normalization,
        config=config.to_dict(),
    )
