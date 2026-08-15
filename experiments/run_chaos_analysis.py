"""Section III-B: phase portraits, Lyapunov estimate, bifurcation, and 0-1 test."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from threedsff.analysis.chaos_metrics import gottwald_melbourne_k, lyapunov_exponents, pq_trajectory
from threedsff.chaos import generate_3d_lmm
from threedsff.config import LMMParameters


def _save_phase(x: np.ndarray, y: np.ndarray, xlabel: str, ylabel: str, output: Path) -> None:
    plt.figure(figsize=(5, 4))
    plt.scatter(x, y, s=0.2)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(output, dpi=160)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="results/generated/chaos")
    parser.add_argument("--length", type=int, default=12_000)
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    params = LMMParameters()
    sequence = generate_3d_lmm(args.length, x0=0.1, y0=0.2, z0=0.3, params=params)

    lyapunov = lyapunov_exponents(params=params)
    k_value = gottwald_melbourne_k(sequence.y[500:5000])
    metrics = {
        "lyapunov_qr": lyapunov.tolist(),
        "gottwald_melbourne_K": k_value,
        # The PDF itself is internally inconsistent; both published values are
        # retained rather than silently choosing one.
        "paper_caption_lyapunov": [2.005, 1.852, 1.5527],
        "paper_body_lyapunov": [4.3080, 4.0041, 3.4112],
    }
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n",
        encoding="utf-8",
    )

    use = slice(500, None)
    _save_phase(sequence.x[use], sequence.y[use], "x(n)", "y(n)", output_dir / "phase_xy.png")
    _save_phase(sequence.x[use], sequence.z[use], "x(n)", "z(n)", output_dir / "phase_xz.png")
    _save_phase(sequence.y[use], sequence.z[use], "y(n)", "z(n)", output_dir / "phase_yz.png")

    p_values, q_values = pq_trajectory(sequence.y[500:5000])
    plt.figure(figsize=(5, 4))
    plt.plot(p_values, q_values, linewidth=0.5)
    plt.xlabel("p")
    plt.ylabel("q")
    plt.tight_layout()
    plt.savefig(output_dir / "gottwald_pq.png", dpi=160)
    plt.close()

    parameter_values = np.linspace(0.3, 1.6, 220)
    plot_b: list[float] = []
    plot_y: list[float] = []
    for b_value in parameter_values:
        test_sequence = generate_3d_lmm(
            800,
            x0=0.1,
            y0=0.2,
            z0=0.3,
            params=LMMParameters(b=float(b_value)),
        )
        plot_b.extend([float(b_value)] * 100)
        plot_y.extend(test_sequence.y[-100:].tolist())

    plt.figure(figsize=(7, 4))
    plt.scatter(plot_b, plot_y, s=0.1)
    plt.xlabel("b")
    plt.ylabel("y(n)")
    plt.tight_layout()
    plt.savefig(output_dir / "bifurcation_b.png", dpi=160)
    plt.close()
    print(output_dir / "metrics.json")


if __name__ == "__main__":
    main()
