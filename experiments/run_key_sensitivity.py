"""Section III-G: visualize 3D-LMM sensitivity to a 1e-16 initial-state perturbation.

The paper states that Fig. 12 uses an initial-value difference d=10^-16 but does
not specify which state variable is perturbed.  This script makes that choice
explicit through ``--axis`` (default: x) instead of hiding it.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from threedsff.chaos import generate_3d_lmm
from threedsff.config import LMMParameters


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--length", type=int, default=500)
    parser.add_argument("--delta", type=float, default=1e-16)
    parser.add_argument("--axis", choices=("x", "y", "z"), default="x")
    parser.add_argument("--output-dir", default="results/generated/key_sensitivity")
    args = parser.parse_args()

    initial = {"x0": 0.1, "y0": 0.2, "z0": 0.3}
    perturbed = dict(initial)
    perturbed[f"{args.axis}0"] += args.delta
    params = LMMParameters()

    base = generate_3d_lmm(args.length, params=params, **initial)
    changed = generate_3d_lmm(args.length, params=params, **perturbed)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    payload = {
        "delta": args.delta,
        "perturbed_axis": args.axis,
        "initial": initial,
        "perturbed_initial": perturbed,
        "max_absolute_difference": {
            "x": float(np.max(np.abs(base.x - changed.x))),
            "y": float(np.max(np.abs(base.y - changed.y))),
            "z": float(np.max(np.abs(base.z - changed.z))),
        },
    }
    (output_dir / "metrics.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )

    iterations = np.arange(args.length)
    for name, first, second in (
        ("x", base.x, changed.x),
        ("y", base.y, changed.y),
        ("z", base.z, changed.z),
    ):
        plt.figure(figsize=(8, 4))
        plt.plot(iterations, first, linewidth=0.8, label="baseline")
        plt.plot(iterations, second, linewidth=0.8, label=f"{args.axis}0 + {args.delta:g}")
        plt.xlabel("iteration")
        plt.ylabel(f"{name}(n)")
        plt.legend()
        plt.tight_layout()
        plt.savefig(output_dir / f"{name}_timing.png", dpi=160)
        plt.close()

    print(output_dir / "metrics.json")


if __name__ == "__main__":
    main()
