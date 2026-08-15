"""Minimal programmatic 3DSFF encryption/decryption example."""

from pathlib import Path

import numpy as np

from threedsff import CipherConfig, decrypt_array, encrypt_array
from threedsff.io import load_image, save_image


ROOT = Path(__file__).resolve().parents[1]
image, raw_bytes = load_image(ROOT / "examples/assets/demo_64.png")
config = CipherConfig.load(ROOT / "configs/smoke_test.json")
cipher, key = encrypt_array(image, config, file_bytes=raw_bytes)
recovered = decrypt_array(cipher, key, config)
assert np.array_equal(image, recovered)

save_image(ROOT / "outputs/quickstart_cipher.png", cipher)
save_image(ROOT / "outputs/quickstart_decrypted.png", recovered)
key.save(ROOT / "outputs/quickstart_key.json")
print("Round-trip OK")
