import numpy as np

from threedsff.fsm import (
    fractal_sorting_matrix,
    inverse_permute_spatial,
    permutation_from_matrix,
    permute_spatial,
)


def test_fsm_is_a_permutation_and_roundtrips():
    a1 = np.array([[3, 1], [4, 2]], dtype=np.int64)
    ak = fractal_sorting_matrix(a1, order=5)
    assert ak.shape == (32, 32)
    assert np.array_equal(np.sort(ak.ravel()), np.arange(1, 1025))

    perm = permutation_from_matrix(ak)
    image = np.arange(32 * 32, dtype=np.uint16).reshape(32, 32)
    encrypted = permute_spatial(image, perm)
    restored = inverse_permute_spatial(encrypted, perm)
    assert np.array_equal(restored, image)
