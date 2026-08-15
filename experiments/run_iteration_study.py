"""Section III-E: evaluate FSM round count with the paper's SSIM formula."""

from __future__ import annotations

import argparse
import csv
from dataclasses import replace
from pathlib import Path

import matplotlib.pyplot as plt

from threedsff import CipherConfig, encrypt_array
from threedsff.analysis.metrics import ssim_global
from threedsff.io import load_image


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--config", default="configs/paper_default.json")
    parser.add_argument("--max-rounds", type=int, default=25)
    parser.add_argument("--output-dir", default="results/generated/iteration")
    args = parser.parse_args()

    image, raw = load_image(args.input)
    base_config = CipherConfig.load(args.config)
    rows: list[tuple[int, float]] = []
    for rounds in range(1, args.max_rounds + 1):
        config = replace(base_config, fsm_rounds=rounds)
        cipher, _ = encrypt_array(image, config, file_bytes=raw)
        rows.append((rounds, ssim_global(image, cipher)))

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "ssim_by_round.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["fsm_rounds", "global_ssim"])
        writer.writerows(rows)

    plt.figure(figsize=(7, 4))
    plt.plot([rounds for rounds, _ in rows], [ssim for _, ssim in rows], marker="o", markersize=3)
    plt.xlabel("FSM rounds")
    plt.ylabel("SSIM")
    plt.tight_layout()
    plt.savefig(output_dir / "ssim_by_round.png", dpi=160)
    plt.close()
    print(output_dir / "ssim_by_round.csv")


if __name__ == "__main__":
    main()
