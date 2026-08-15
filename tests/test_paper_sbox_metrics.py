from pathlib import Path

import numpy as np

from threedsff.analysis.sbox_metrics import bic_nonlinearity_matrix, component_nonlinearity, sac_matrix


def _paper_sbox():
    path = Path(__file__).resolve().parents[1] / "results" / "paper_reference" / "table_I_reconstructed_sbox.csv"
    return np.loadtxt(path, delimiter=",", dtype=np.uint8).reshape(-1)


def test_paper_table_i_nonlinearity_and_sac():
    sbox = _paper_sbox()
    nl = component_nonlinearity(sbox)
    assert nl.tolist() == [106, 104, 102, 104, 102, 102, 102, 108]
    assert float(np.mean(nl)) == 103.75

    sac = sac_matrix(sbox)
    # Paper Table V reports 0.5017; the exact mean of Table-I-derived SAC is
    # 0.501708984375 using the standard definition implemented here.
    assert abs(float(np.mean(sac)) - 0.501708984375) < 1e-12


def test_paper_table_i_bic_nonlinearity_standard_definition():
    sbox = _paper_sbox()
    bic = bic_nonlinearity_matrix(sbox)
    vals = bic[np.triu_indices(8, 1)]
    # The paper's comparison table rounds the BIC-nonlinearity average to 104.
    assert abs(float(np.mean(vals)) - 104.5) < 1e-12
