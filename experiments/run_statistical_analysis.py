"""Section III-F: histogram, adjacent correlation, and information entropy."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt

from threedsff.analysis.metrics import adjacent_correlation, information_entropy
from threedsff.io import load_image


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir", default="results/generated/statistical")
    args = parser.parse_args()

    image, _ = load_image(args.input)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    entropy = information_entropy(image)
    correlation = adjacent_correlation(image)
    payload = {
        "entropy": entropy.tolist(),
        "correlation": {direction: values.tolist() for direction, values in correlation.items()},
    }
    (output_dir / "metrics.json").write_text(
        json.dumps(payload, indent=2) + "\n",
        encoding="utf-8",
    )

    labels = ["R", "G", "B"] if image.ndim == 3 else ["Gray"]
    figure, axes = plt.subplots(len(labels), 1, figsize=(8, 2.8 * len(labels)), squeeze=False)
    for channel, label in enumerate(labels):
        values = image[..., channel].ravel() if image.ndim == 3 else image.ravel()
        axes[channel, 0].hist(values, bins=256)
        axes[channel, 0].set_title(f"{label} histogram")
    figure.tight_layout()
    figure.savefig(output_dir / "histogram.png", dpi=160)
    plt.close(figure)
    print(output_dir / "metrics.json")


if __name__ == "__main__":
    main()
