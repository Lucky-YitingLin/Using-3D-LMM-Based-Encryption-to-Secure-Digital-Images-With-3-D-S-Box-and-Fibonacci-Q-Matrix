"""Run encryption, decryption, and core statistical checks on one image."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

import numpy as np

from threedsff import CipherConfig, decrypt_array, encrypt_array
from threedsff.analysis.metrics import adjacent_correlation, information_entropy
from threedsff.io import load_image, save_image


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="examples/assets/demo_64.png")
    parser.add_argument("--config", default="configs/paper_default.json")
    parser.add_argument("--output-dir", default="results/generated/core")
    args = parser.parse_args()

    image, raw = load_image(args.input)
    config = CipherConfig.load(args.config)

    start = time.perf_counter()
    cipher, key = encrypt_array(image, config, file_bytes=raw)
    encryption_seconds = time.perf_counter() - start

    start = time.perf_counter()
    recovered = decrypt_array(cipher, key, config)
    decryption_seconds = time.perf_counter() - start
    exact = bool(np.array_equal(image, recovered))

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    save_image(output_dir / "cipher.png", cipher)
    save_image(output_dir / "decrypted.png", recovered)
    key.save(output_dir / "key.json")

    metrics = {
        "roundtrip_exact": exact,
        "encryption_seconds": encryption_seconds,
        "decryption_seconds": decryption_seconds,
        "cipher_entropy": information_entropy(cipher).tolist(),
        "cipher_correlation": {
            direction: values.tolist()
            for direction, values in adjacent_correlation(cipher).items()
        },
    }
    (output_dir / "metrics.json").write_text(
        json.dumps(metrics, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(metrics, indent=2))
    if not exact:
        raise SystemExit("decryption mismatch")


if __name__ == "__main__":
    main()
