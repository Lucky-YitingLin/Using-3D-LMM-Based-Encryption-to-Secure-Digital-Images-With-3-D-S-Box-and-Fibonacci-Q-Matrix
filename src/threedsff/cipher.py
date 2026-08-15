"""End-to-end 3DSFF encryption/decryption pipeline.

Encryption follows Fig. 1 and Eqs. (3)--(12):
3D-FSM S-box substitution -> 16 FSM permutations -> XOR confusion -> FQM.
Decryption is the mathematically necessary reverse pipeline.  The paper only
states Q^{-n} for decryption and does not publish a full decryption algorithm;
that distinction is explicitly documented in the repository.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .chaos import ChaoticSequences, generate_3d_lmm, sequence_length_for_image
from .config import CipherConfig
from .confusion import confusion_mask, xor_confuse
from .fibonacci import fqm_iteration_values, fqm_transform
from .fsm import make_round_permutations, permute_spatial, inverse_permute_spatial
from .io import validate_paper_image_shape
from .key_schedule import KeyMaterial, derive_key_material
from .sbox3d import generate_3d_sbox, substitute, inverse_substitute


@dataclass(frozen=True)
class CipherArtifacts:
    """Intermediate objects useful for experiments and auditing."""

    key: KeyMaterial
    chaos: ChaoticSequences
    sbox: np.ndarray
    fsm_permutations: tuple[np.ndarray, ...]
    confusion_mask: np.ndarray
    fqm_exponents: np.ndarray


def _generate_sequences_for_shape(key: KeyMaterial, config: CipherConfig, h: int, w: int) -> ChaoticSequences:
    length = sequence_length_for_image(h, w, sbox_index_burnin=config.sbox_index_burnin)
    while True:
        seq = generate_3d_lmm(length, x0=key.x0, y0=key.y0, z0=key.z0, params=config.lmm)
        nblocks = (h // 2) * (w // 2)
        try:
            fqm_iteration_values(
                seq.z,
                nblocks,
                scale=config.fqm_scale,
                residue_modulus=config.fqm_modulus,
            )
            return seq
        except ValueError:
            # Extremely unlikely for a roughly balanced mod-64 sequence, but
            # deterministic extension is preferable to silently reusing values.
            length *= 2


def prepare_artifacts(
    image: np.ndarray,
    config: CipherConfig,
    *,
    key: KeyMaterial | None = None,
    file_bytes: bytes | None = None,
) -> CipherArtifacts:
    """Prepare all deterministic key-dependent objects for an image shape."""

    validate_paper_image_shape(image, require_square_power_of_two=config.require_square_power_of_two)
    h, w = image.shape[:2]
    if key is None:
        key = derive_key_material(image, config, file_bytes=file_bytes)
    seq = _generate_sequences_for_shape(key, config, h, w)
    sbox = generate_3d_sbox(seq.x, config)
    perms = make_round_permutations(seq.x, seq.y, h, config.fsm_rounds)
    mask = confusion_mask(seq.y, h, w, scale=config.confusion_scale)
    exponents = fqm_iteration_values(
        seq.z,
        (h // 2) * (w // 2),
        scale=config.fqm_scale,
        residue_modulus=config.fqm_modulus,
    )
    return CipherArtifacts(
        key=key,
        chaos=seq,
        sbox=sbox,
        fsm_permutations=tuple(perms),
        confusion_mask=mask,
        fqm_exponents=exponents,
    )


def encrypt_array(
    image: np.ndarray,
    config: CipherConfig | None = None,
    *,
    file_bytes: bytes | None = None,
    return_artifacts: bool = False,
) -> tuple[np.ndarray, KeyMaterial] | tuple[np.ndarray, KeyMaterial, CipherArtifacts]:
    """Encrypt a uint8 image according to the reconstructed paper pipeline."""

    config = config or CipherConfig()
    image = np.asarray(image, dtype=np.uint8)
    art = prepare_artifacts(image, config, file_bytes=file_bytes)

    current = substitute(image, art.sbox)
    for perm in art.fsm_permutations:
        current = permute_spatial(current, perm)
    current = xor_confuse(current, art.confusion_mask)
    cipher = fqm_transform(current, art.fqm_exponents, inverse=False, modulus=config.pixel_modulus)

    if return_artifacts:
        return cipher, art.key, art
    return cipher, art.key


def decrypt_array(
    cipher: np.ndarray,
    key: KeyMaterial,
    config: CipherConfig | None = None,
    *,
    return_artifacts: bool = False,
) -> np.ndarray | tuple[np.ndarray, CipherArtifacts]:
    """Decrypt by reversing FQM -> XOR -> FSM rounds -> S-box substitution.

    This reverse sequence is a paper-consistent reconstruction rather than a
    verbatim published pseudocode block; the paper only explicitly gives the
    inverse Fibonacci Q-matrix in Eq. (9).
    """

    if config is None:
        config = CipherConfig.from_dict(key.config)
    cipher = np.asarray(cipher, dtype=np.uint8)
    # ``prepare_artifacts`` normally derives a key from the supplied image; for
    # decryption we explicitly pass the stored key to avoid that circularity.
    art = prepare_artifacts(cipher, config, key=key)

    current = fqm_transform(cipher, art.fqm_exponents, inverse=True, modulus=config.pixel_modulus)
    current = xor_confuse(current, art.confusion_mask)
    for perm in reversed(art.fsm_permutations):
        current = inverse_permute_spatial(current, perm)
    plain = inverse_substitute(current, art.sbox)
    if return_artifacts:
        return plain, art
    return plain
