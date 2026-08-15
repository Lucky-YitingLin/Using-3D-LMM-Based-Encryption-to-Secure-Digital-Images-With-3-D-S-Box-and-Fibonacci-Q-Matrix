import numpy as np

from threedsff.chaos import generate_3d_lmm
from threedsff.config import CipherConfig
from threedsff.sbox3d import generate_3d_sbox, mapping_from_3d_sbox, substitute, inverse_substitute


def test_generated_sbox_is_bijective_and_roundtrips():
    cfg = CipherConfig(sbox_fsm_rounds=2)
    seq = generate_3d_lmm(16000, x0=0.1, y0=0.2, z0=0.3, params=cfg.lmm)
    sbox = generate_3d_sbox(seq.x, cfg)
    mapping = mapping_from_3d_sbox(sbox)
    assert sbox.shape == (8, 8, 4)
    assert np.unique(mapping).size == 256

    values = np.arange(256, dtype=np.uint8).reshape(16, 16)
    cipher = substitute(values, sbox)
    restored = inverse_substitute(cipher, sbox)
    assert np.array_equal(restored, values)
