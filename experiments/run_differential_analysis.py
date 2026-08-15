"""Section III-C/G: plaintext sensitivity measured with NPCR and UACI."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from threedsff import CipherConfig, encrypt_array
from threedsff.analysis.metrics import npcr_uaci
from threedsff.io import load_image


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--config", default="configs/paper_default.json")
    parser.add_argument("--trials", type=int, default=50)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--output", default="results/generated/differential.json")
    args = parser.parse_args()

    image, raw = load_image(args.input)
    config = CipherConfig.load(args.config)
    baseline_cipher, _ = encrypt_array(image, config, file_bytes=raw)
    rng = np.random.default_rng(args.seed)
    rows = []

    for trial in range(args.trials):
        changed = image.copy()
        row = int(rng.integers(image.shape[0]))
        column = int(rng.integers(image.shape[1]))
        channel_count = image.shape[2] if image.ndim == 3 else 1
        channel = int(rng.integers(channel_count))
        if image.ndim == 3:
            changed[row, column, channel] = np.uint8((int(changed[row, column, channel]) + 1) % 256)
        else:
            changed[row, column] = np.uint8((int(changed[row, column]) + 1) % 256)

        changed_cipher, _ = encrypt_array(changed, config)
        npcr, uaci = npcr_uaci(baseline_cipher, changed_cipher)
        rows.append(
            {
                "trial": trial,
                "pixel": [row, column, channel],
                "npcr": npcr.tolist(),
                "uaci": uaci.tolist(),
            }
        )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
