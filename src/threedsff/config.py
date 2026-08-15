"""Configuration objects for the paper-derived 3DSFF reconstruction.

The defaults mirror the explicit constants in Sections II-A--II-D of the
paper whenever the paper is unambiguous.  Ambiguous choices are exposed as
configuration fields and documented in ``docs/REPRODUCTION_NOTES.md``.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class LMMParameters:
    """Parameters of the proposed 3D-LMM map (paper Eq. (1))."""

    a: float = 0.5
    b: float = 2.0
    c: float = 0.5
    d: float = 0.5
    e: float = 0.2


@dataclass(frozen=True)
class CipherConfig:
    """Reproducibility configuration for the 3DSFF pipeline.

    ``hash_normalization`` controls an ambiguity in Section II-A, Step 2.
    The paper prints a divisor of 10^16 while simultaneously saying the
    resulting value is in [0, 1].  ``paper_literal`` follows the printed
    denominator exactly; ``hex_unit_interval`` divides by 16^16, which is
    the natural normalization for 16 hexadecimal digits.
    """

    lmm: LMMParameters = field(default_factory=LMMParameters)
    fsm_rounds: int = 16
    sbox_fsm_rounds: int = 8
    sbox_fill_burnin: int = 5000
    sbox_index_burnin: int = 10000
    sbox_scale: int = 2**10
    confusion_scale: float = 1e10
    fqm_scale: float = 1e10
    fqm_modulus: int = 64
    pixel_modulus: int = 256
    hash_mode: str = "pixel_bytes"
    hash_normalization: str = "paper_literal"
    hash_divisor: float = 1e16
    require_square_power_of_two: bool = True
    sbox_undefined_s22_source: str = "s12_values"
    fsm_recurrence: str = "sorting_preserving"

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CipherConfig":
        data = dict(data)
        lmm_data = data.pop("lmm", {})
        return cls(lmm=LMMParameters(**lmm_data), **data)

    @classmethod
    def load(cls, path: str | Path) -> "CipherConfig":
        with Path(path).open("r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))

    def save(self, path: str | Path) -> None:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2, sort_keys=True)
            f.write("\n")
