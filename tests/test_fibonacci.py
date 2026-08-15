import numpy as np

from threedsff.fibonacci import fqm_transform, q_inverse_power_mod, q_power_mod


def test_q_power_inverse_mod_256():
    eye = np.eye(2, dtype=np.int64)
    for n in (0, 2, 14, 62):
        q = np.asarray(q_power_mod(n), dtype=np.int64)
        qi = np.asarray(q_inverse_power_mod(n), dtype=np.int64)
        assert np.array_equal((q @ qi) % 256, eye)


def test_fqm_rgb_roundtrip():
    rng = np.random.default_rng(1234)
    image = rng.integers(0, 256, size=(8, 8, 3), dtype=np.uint8)
    exponents = np.array([0, 2, 4, 6] * 4, dtype=np.int64)
    cipher = fqm_transform(image, exponents)
    plain = fqm_transform(cipher, exponents, inverse=True)
    assert np.array_equal(plain, image)
