"""Section III-H: all-black and all-white chosen-plaintext demonstrations."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from threedsff import CipherConfig, encrypt_array
from threedsff.confusion import xor_confuse
from threedsff.fibonacci import fqm_transform
from threedsff.io import save_image


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--side", type=int, default=256)
    parser.add_argument("--config", default="configs/paper_default.json")
    parser.add_argument("--output-dir", default="results/generated/chosen_plaintext")
    args = parser.parse_args()

    config = CipherConfig.load(args.config)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for name, value in (("black", 0), ("white", 255)):
        plain = np.full((args.side, args.side, 3), value, dtype=np.uint8)
        cipher, key, artifacts = encrypt_array(plain, config, return_artifacts=True)
        save_image(output_dir / f"{name}_plain.png", plain)
        save_image(output_dir / f"{name}_cipher.png", cipher)
        key.save(output_dir / f"{name}_key.json")

        # Fig. 14 also shows an all-black result after the confusion + FQM
        # stages. The paper does not fully define that ablation path, so we
        # record the explicit interpretation used here: apply XOR and FQM
        # directly to the chosen plaintext, without S-box/FSM.
        if name == "black":
            confusion_only = xor_confuse(plain, artifacts.confusion_mask)
            confusion_fqm = fqm_transform(
                confusion_only,
                artifacts.fqm_exponents,
                inverse=False,
                modulus=config.pixel_modulus,
            )
            save_image(output_dir / "black_confusion_fqm.png", confusion_fqm)

    print(output_dir)


if __name__ == "__main__":
    main()
