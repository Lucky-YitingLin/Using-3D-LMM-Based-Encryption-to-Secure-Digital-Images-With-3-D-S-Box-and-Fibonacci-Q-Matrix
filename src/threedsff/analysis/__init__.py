"""Security/statistical analysis utilities for 3DSFF reproduction."""

from .metrics import adjacent_correlation, information_entropy, npcr_uaci, ssim_global
from .sbox_metrics import (
    bic_nonlinearity_matrix,
    bic_sac_matrix,
    component_nonlinearity,
    is_bijective,
    sac_matrix,
)

__all__ = [
    "adjacent_correlation",
    "information_entropy",
    "npcr_uaci",
    "ssim_global",
    "bic_nonlinearity_matrix",
    "bic_sac_matrix",
    "component_nonlinearity",
    "is_bijective",
    "sac_matrix",
]
