"""Export 3D-LMM bytes for use with an external NIST SP 800-22 suite.

Section III-B/Table X reports NIST SP 800-22 p-values, but the paper does not
specify sequence length, quantization/bit extraction, suite version, or test
parameters.  This helper therefore exposes one deterministic byte extraction
path without claiming that it reproduces the published p-values.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from threedsff.chaos import generate_3d_lmm
from threedsff.config import LMMParameters


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--length", type=int, default=1_000_000)
    parser.add_argument("--output", default="results/generated/lmm_nist.bin")
    args = parser.parse_args()

    sequence = generate_3d_lmm(
        args.length,
        x0=0.1,
        y0=0.2,
        z0=0.3,
        params=LMMParameters(),
    )
    byte_stream = np.floor(np.mod(sequence.x * 1e10, 256)).astype(np.uint8)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(byte_stream.tobytes())
    print(output)


if __name__ == "__main__":
    main()
