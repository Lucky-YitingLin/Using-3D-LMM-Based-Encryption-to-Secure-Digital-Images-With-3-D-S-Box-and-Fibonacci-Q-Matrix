import numpy as np

from threedsff.cipher import decrypt_array, encrypt_array
from threedsff.config import CipherConfig


def test_end_to_end_roundtrip():
    y, x = np.mgrid[0:32, 0:32]
    image = np.stack(
        [
            (7 * x + 3 * y) % 256,
            (11 * x + y) % 256,
            (x ^ y) % 256,
        ],
        axis=-1,
    ).astype(np.uint8)
    cfg = CipherConfig(fsm_rounds=4, sbox_fsm_rounds=2)
    cipher, key = encrypt_array(image, cfg)
    restored = decrypt_array(cipher, key, cfg)
    assert not np.array_equal(cipher, image)
    assert np.array_equal(restored, image)
