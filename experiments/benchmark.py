"""Section III-D/J: benchmark encryption and decryption on the local machine.

The paper reports MATLAB 2022b timings on a specific Windows/AMD system.  This
script records measurements for the current Python environment and never labels
them as a reproduction of Table XIV unless the environment is actually matched.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

from threedsff import CipherConfig, decrypt_array, encrypt_array
from threedsff.io import load_image


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--config", default="configs/paper_default.json")
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--output", default="results/generated/benchmark.json")
    args = parser.parse_args()

    image, raw = load_image(args.input)
    config = CipherConfig.load(args.config)
    encryption_times: list[float] = []
    decryption_times: list[float] = []

    for _ in range(args.repeat):
        start = time.perf_counter()
        cipher, key = encrypt_array(image, config, file_bytes=raw)
        encryption_times.append(time.perf_counter() - start)

        start = time.perf_counter()
        recovered = decrypt_array(cipher, key, config)
        decryption_times.append(time.perf_counter() - start)
        if recovered.shape != image.shape:
            raise RuntimeError("decryption produced an unexpected image shape")

    payload = {
        "shape": list(image.shape),
        "encrypt_seconds": encryption_times,
        "decrypt_seconds": decryption_times,
        "encrypt_mean": sum(encryption_times) / len(encryption_times),
        "decrypt_mean": sum(decryption_times) / len(decryption_times),
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
