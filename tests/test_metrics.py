import numpy as np

from threedsff.analysis.metrics import information_entropy, npcr_uaci


def test_entropy_constant_image_is_zero():
    image = np.zeros((16, 16), dtype=np.uint8)
    entropy = information_entropy(image)
    assert np.allclose(entropy, [0.0])


def test_npcr_uaci_identical_images_are_zero():
    image = np.arange(256, dtype=np.uint8).reshape(16, 16)
    npcr, uaci = npcr_uaci(image, image)
    assert np.allclose(npcr, [0.0])
    assert np.allclose(uaci, [0.0])
