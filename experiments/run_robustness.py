"""Section III-I: cropping and salt-and-pepper ciphertext robustness tests."""

from __future__ import annotations

import argparse
from pathlib import Path

from threedsff import CipherConfig, decrypt_array, encrypt_array
from threedsff.analysis.robustness import crop_ciphertext, salt_pepper_noise
from threedsff.io import load_image, save_image


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--config", default="configs/paper_default.json")
    parser.add_argument("--output-dir", default="results/generated/robustness")
    args = parser.parse_args()

    image, raw = load_image(args.input)
    config = CipherConfig.load(args.config)
    cipher, key = encrypt_array(image, config, file_bytes=raw)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for ratio in (0.125, 0.25):
        attacked = crop_ciphertext(cipher, ratio, location="center")
        save_image(output_dir / f"crop_{ratio:.3f}_cipher.png", attacked)
        save_image(
            output_dir / f"crop_{ratio:.3f}_decrypted.png",
            decrypt_array(attacked, key, config),
        )

    for density in (0.10, 0.20, 0.30):
        attacked = salt_pepper_noise(cipher, density, seed=0)
        save_image(output_dir / f"noise_{density:.2f}_cipher.png", attacked)
        save_image(
            output_dir / f"noise_{density:.2f}_decrypted.png",
            decrypt_array(attacked, key, config),
        )

    print(output_dir)


if __name__ == "__main__":
    main()
