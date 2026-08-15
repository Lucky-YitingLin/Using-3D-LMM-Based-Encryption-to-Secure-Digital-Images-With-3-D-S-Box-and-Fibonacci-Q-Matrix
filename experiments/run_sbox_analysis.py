"""Section III-A: bijectivity, nonlinearity, SAC, BIC-SAC, and BIC-NL."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from threedsff import CipherConfig
from threedsff.analysis.sbox_metrics import (
    bic_nonlinearity_matrix,
    bic_sac_matrix,
    component_nonlinearity,
    is_bijective,
    sac_matrix,
)
from threedsff.cipher import encrypt_array
from threedsff.io import load_image
from threedsff.sbox3d import mapping_from_3d_sbox


def analyze(mapping: np.ndarray) -> dict[str, object]:
    """Return all implemented Section III-A metrics for one 256-byte S-box."""

    nonlinearity = component_nonlinearity(mapping)
    sac = sac_matrix(mapping)
    bic_nl = bic_nonlinearity_matrix(mapping)
    bic_sac = bic_sac_matrix(mapping)
    return {
        "bijective": is_bijective(mapping),
        "nonlinearity": nonlinearity.tolist(),
        "nonlinearity_average": float(nonlinearity.mean()),
        "sac_average": float(sac.mean()),
        "bic_sac_average": float(np.nanmean(bic_sac)),
        "bic_nonlinearity_average": float(np.nanmean(bic_nl)),
        "sac_matrix": sac.tolist(),
        "bic_sac_matrix": bic_sac.tolist(),
        "bic_nonlinearity_matrix": bic_nl.tolist(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="examples/assets/demo_64.png")
    parser.add_argument("--config", default="configs/paper_default.json")
    parser.add_argument("--paper-table-i", action="store_true")
    parser.add_argument("--output", default="results/generated/sbox_analysis.json")
    args = parser.parse_args()

    if args.paper_table_i:
        mapping = np.loadtxt(
            "results/paper_reference/table_I_reconstructed_sbox.csv",
            delimiter=",",
            dtype=np.uint8,
        ).ravel()
    else:
        image, raw = load_image(args.input)
        config = CipherConfig.load(args.config)
        _, _, artifacts = encrypt_array(image, config, file_bytes=raw, return_artifacts=True)
        mapping = mapping_from_3d_sbox(artifacts.sbox)

    result = analyze(mapping)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, allow_nan=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, allow_nan=True))


if __name__ == "__main__":
    main()
