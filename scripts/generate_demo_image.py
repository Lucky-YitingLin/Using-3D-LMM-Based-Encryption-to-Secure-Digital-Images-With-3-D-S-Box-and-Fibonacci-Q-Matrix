"""Generate a small copyright-free RGB image for smoke tests and examples."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image


def make_demo(side: int) -> np.ndarray:
    """Return a deterministic synthetic RGB pattern with power-of-two side length."""

    y, x = np.mgrid[0:side, 0:side]
    red = (4 * x + 2 * y) % 256
    green = (3 * y + (x // max(1, side // 8)) * 31) % 256
    blue = ((x ^ y) * 7 + 40) % 256
    return np.stack([red, green, blue], axis=-1).astype(np.uint8)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--side", type=int, default=64)
    parser.add_argument("--output", default="examples/assets/demo_64.png")
    args = parser.parse_args()
    if args.side < 2 or args.side & (args.side - 1):
        raise SystemExit("side must be a power of two")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(make_demo(args.side)).save(output)
    print(output)


if __name__ == "__main__":
    main()
