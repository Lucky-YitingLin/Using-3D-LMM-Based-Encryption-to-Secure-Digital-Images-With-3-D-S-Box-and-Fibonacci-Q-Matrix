# 3DSFF Image Encryption — Paper-Derived Reproduction

[中文说明](README_zh-CN.md) · [Paper-to-code map](docs/PAPER_IMPLEMENTATION_MAP.md) · [Reproduction notes](docs/REPRODUCTION_NOTES.md) · [Experiments](docs/EXPERIMENTS.md)

This repository is a clean-room, reproducibility-oriented implementation of the image-encryption scheme proposed in:

> Yunlong Liao, Yiting Lin, Zheng Xing, Qiutong Li, Guoheng Huang, Donglong Chen, and Xiaochen Yuan, **“Using 3D-LMM-Based Encryption to Secure Digital Images With 3-D S-Box and Fibonacci Q-Matrix,”** *IEEE Internet of Things Journal*, vol. 12, no. 24, 2025. DOI: `10.1109/JIOT.2025.3624032`.

The paper names the complete design **3DSFF**: a plaintext-bound 3D-LMM chaotic generator drives a dynamically perturbed 3-D S-box, a fractal-sorting-matrix (FSM) permutation, XOR confusion, and a chaos-selected Fibonacci Q-matrix (FQM) block transform.

> **Reconstruction status.** The material supplied for this work contained the paper PDF only; no original MATLAB source tree, scripts, datasets, `.mat` files, or Raspberry Pi implementation were provided. Therefore the code in this repository is a paper-derived Python reconstruction, not a claim of byte-for-byte identity with unavailable historical source code. Every material ambiguity is recorded in [`docs/REPRODUCTION_NOTES.md`](docs/REPRODUCTION_NOTES.md).

> **Security notice.** This is research reproduction code, not a production cryptographic library. It has not been designed as authenticated encryption, audited for side channels, or hardened for production key management.

## Why this repository exists

The goal is to make the paper understandable and executable as a conventional open-source research project: a reader should be able to trace each paper step to code, install the environment, run encryption/decryption, validate reversibility, execute the reproducible subset of security experiments, and distinguish published values from locally generated results.

The project organization follows the reproducibility principles of the requested reference repository, [Cryptanalyzing-an-image-cipher-using-multiple-chaos-and-DNA-operations](https://github.com/Lucky-YitingLin/Cryptanalyzing-an-image-cipher-using-multiple-chaos-and-DNA-operations)—separating `src`, `tests`, `examples`, `paper`, and documentation, and maintaining an explicit paper-to-code mapping—while the implementation and file taxonomy are specific to this 3DSFF paper. The proposed 3DSFF algorithm does **not** contain DNA encoding or DNA arithmetic; no DNA module is added merely to resemble the reference repository.

## Method overview

The reconstructed encryption path follows Fig. 1 and Sections II-A–II-D:

1. **Plaintext-bound key derivation** — SHA-512 is computed from the plaintext. Every eighth hexadecimal character, starting at three adjacent offsets, forms three 16-character samples that initialize `x0`, `y0`, and `z0`.
2. **3D-LMM** — Eq. (1) generates three nonlinear sequences `x_n`, `y_n`, and `z_n` with paper parameters `a=0.5`, `b=2`, `c=0.5`, `d=0.5`, `e=0.2`.
3. **3-D FSM S-box** — chaotic bytes are deduplicated, reordered, reshaped to an `8×8×4` S-box, and perturbed by eight 8×8 FSM operations. Each input byte indexes the S-box through a `3:3:2` bit split.
4. **FSM permutation** — the substituted image is spatially permuted for 16 rounds (paper default for color images), with a different rank-derived fractal matrix per round.
5. **XOR confusion** — `Seq2 = floor(mod(y_n × 10^10, 256))` is reshaped into an image-sized mask and XORed with the FSM output.
6. **Fibonacci Q-matrix** — `Seq3 = floor(mod(z_n × 10^10, 64))`; even values select `Q^n` for each 2×2 block, and the result is reduced modulo 256.

Decryption reverses those bijective stages: inverse FQM → XOR → inverse FSM rounds in reverse order → inverse S-box. The paper explicitly provides `Q^{-n}` but does not provide a complete decryption pseudocode block; the reverse pipeline is therefore clearly marked as a mathematically necessary reconstruction.

Detailed equations, compatibility choices, and decryption rationale are in [`docs/ALGORITHM.md`](docs/ALGORITHM.md).

## Important paper ambiguities handled explicitly

The implementation does not silently guess over contradictions. The main compatibility decisions are:

- the SHA-512 text prints division by `10^16` while also claiming a `[0,1]` result; `paper_literal` follows the printed denominator and alternative normalization modes are exposed;
- FSM Steps 1 and 2 duplicate the same Seq1 text;
- the printed FSM recurrence uses a constant factor `4`, which ceases to produce a sorting permutation at higher orders, so the implementation uses the sorting-preserving previous-block-size shift;
- the S-box is first called `8×4×4`, but Fig. 3, Step 3, and the `3:3:2` indexing require `8×8×4`;
- S-box Step 4 refers to undefined `S22`; the default compatibility choice uses the Step-2 `S12` driving values;
- Eq. (8) is interpreted as the standard Fibonacci identity `Q^n`, avoiding a second unintended exponentiation;
- the paper's Fig. 5 caption and body report two different Lyapunov-exponent triplets;
- exact NIST SP 800-22 preprocessing, SSIM windowing, correlation sampling, crop geometry, and benchmark-image provenance are not fully specified.

See [`docs/REPRODUCTION_NOTES.md`](docs/REPRODUCTION_NOTES.md) for the full audit trail.

## Project layout

```text
3dsff-image-encryption-reproduction/
├── src/threedsff/
│   ├── chaos.py                 # 3D-LMM Eq. (1)
│   ├── key_schedule.py          # SHA-512 plaintext binding / KeyMaterial
│   ├── fsm.py                   # fractal sorting matrix + inverse permutation
│   ├── sbox3d.py                # 8×8×4 S-box generation/substitution
│   ├── confusion.py             # Seq2 XOR stage, Eqs. (5)–(6)
│   ├── fibonacci.py             # Q^n / Q^-n and 2×2 FQM transform
│   ├── cipher.py                # end-to-end encrypt/decrypt pipeline
│   ├── io.py                    # image I/O and geometry validation
│   ├── cli.py                   # `threedsff` command line interface
│   └── analysis/
│       ├── metrics.py           # entropy, correlation, NPCR/UACI, SSIM
│       ├── sbox_metrics.py      # bijectivity, NL, SAC, BIC
│       ├── chaos_metrics.py     # Jacobian, Lyapunov, 0–1 test
│       └── robustness.py        # cropping/noise perturbations
├── experiments/                 # Section III reproduction scripts
├── tests/                       # deterministic regression/unit tests
├── configs/                     # paper-default and faster smoke configs
├── examples/                    # minimal example + synthetic test image
├── scripts/                     # auxiliary data-generation helper
├── data/                        # local user-supplied benchmark images
├── results/
│   ├── paper_reference/         # values transcribed from the paper
│   └── smoke/                   # local synthetic verification snapshot
├── docs/                        # algorithm, mapping, audit, experiment guide
├── paper/                       # paper metadata; PDF intentionally not redistributed
├── .github/workflows/ci.yml     # automated pytest workflow
├── CITATION.cff
├── LICENSE
├── pyproject.toml
└── requirements.txt
```

## Requirements

- Python 3.10 or newer.
- NumPy, Pillow, Matplotlib, SciPy, and scikit-image (declared in `pyproject.toml` / `requirements.txt`).
- Pytest for regression testing.

The paper's original experiment environment was MATLAB 2022b on 64-bit Windows 11 with an AMD Ryzen 7-7745HX and 16 GB RAM. This Python reconstruction is portable; timing and chaotic floating-point trajectories can differ from that environment.

## Installation

Recommended editable install from the repository root:

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
pip install -e ".[dev]"
```

For runtime dependencies only:

```bash
pip install -r requirements.txt
pip install -e . --no-deps
```

## Quick start

### 1. Run the exact round-trip test suite

```bash
pytest
```

The suite checks FSM invertibility, Fibonacci Q-matrix inversion, S-box bijectivity/inversion, metric sanity, the Table-I S-box nonlinearity/SAC calculations, and complete encryption → decryption recovery.

### 2. Run the included example

```bash
python examples/quickstart.py
```

Generated files are written under `outputs/` (ignored by Git).

### 3. Encrypt from the command line

```bash
threedsff encrypt \
  --input examples/assets/demo_64.png \
  --output results/generated/demo_cipher.png \
  --key-output results/generated/demo_key.json \
  --config configs/paper_default.json
```

`demo_key.json` contains the plaintext-derived initial states and exact compatibility configuration needed for decryption. Treat it as **secret key material**.

### 4. Decrypt

```bash
threedsff decrypt \
  --input results/generated/demo_cipher.png \
  --key results/generated/demo_key.json \
  --output results/generated/demo_recovered.png
```

### 5. Core reproducibility smoke run

```bash
python experiments/reproduce_core.py \
  --input examples/assets/demo_64.png \
  --config configs/paper_default.json
```

The included `results/smoke/core/metrics.json` records a verified exact round trip on the synthetic 64×64 test image. Its entropy/correlation values are **not** paper benchmark values and must not be compared as if they used the paper's 512×512 images.

## Data preparation

The supplied paper names Oakland, Splash, Mandrill, F-16, Sailboat, Peppers, and House, but the reconstruction package did not include those images or enough provenance to uniquely identify their exact source versions. Put legally obtained images in `data/raw/`.

The current FSM implementation expects a square power-of-two side length, and FQM requires even dimensions. Typical paper-like inputs are 256×256 or 512×512 RGB `uint8` images.

A deterministic copyright-free `64×64` synthetic image is included only for software verification. Regenerate it with:

```bash
python scripts/generate_demo_image.py --side 64 --output examples/assets/demo_64.png
```

## Experiment reproduction

The full command guide is in [`docs/EXPERIMENTS.md`](docs/EXPERIMENTS.md). Main entry points are:

```bash
# Section III-A: S-box metrics
python experiments/run_sbox_analysis.py --paper-table-i

# Section III-B: chaos diagnostics
python experiments/run_chaos_analysis.py

# NIST bitstream export (exact Table-X preprocessing is unspecified)
python experiments/export_nist_bitstream.py

# Section III-G: key sensitivity (paper uses d=1e-16)
python experiments/run_key_sensitivity.py --delta 1e-16 --axis x

# Sections III-C/G: NPCR/UACI plaintext sensitivity
python experiments/run_differential_analysis.py --input data/raw/Mandrill.png --trials 50

# Section III-D/J: local timing
python experiments/benchmark.py --input data/raw/Mandrill.png

# Section III-E: SSIM vs FSM rounds
python experiments/run_iteration_study.py --input data/raw/Mandrill.png --max-rounds 25

# Section III-F: histogram / correlation / entropy
python experiments/run_statistical_analysis.py --input results/generated/mandrill_cipher.png

# Section III-H: all-black / all-white probes
python experiments/run_chosen_plaintext.py --side 256

# Section III-I: crop / salt-and-pepper robustness
python experiments/run_robustness.py --input data/raw/Peppers.png
```

`experiments/run_all.py` executes the self-contained subset that does not need the unavailable paper image dataset.

## Main parameters

| Parameter | Paper/default value | Meaning |
|---|---:|---|
| `lmm.a` | `0.5` | 3D-LMM scale |
| `lmm.b` | `2.0` | sine-coupling parameter |
| `lmm.c` | `0.5` | cosine branch constant |
| `lmm.d` | `0.5` | cosine branch scale |
| `lmm.e` | `0.2` | sine branch constant |
| `fsm_rounds` | `16` | image FSM permutation rounds for color images |
| `sbox_fsm_rounds` | `8` | 8×8 S-box perturbation rounds |
| `sbox_fill_burnin` | `5000` | discard before `S11` |
| `sbox_index_burnin` | `10000` | discard before Step-2 index sequence |
| `sbox_scale` | `1024` | `2^10` S-box sequence scale |
| `confusion_scale` | `1e10` | Eq. (5) scale |
| `fqm_scale` | `1e10` | Eq. (10) scale |
| `fqm_modulus` | `64` | Eq. (10) residue modulus |
| `pixel_modulus` | `256` | final pixel modular arithmetic |
| `hash_normalization` | `paper_literal` | compatibility interpretation of Section II-A Step 2 |

Use `configs/paper_default.json` for the highest-fidelity paper interpretation and `configs/smoke_test.json` for faster development tests (fewer FSM/S-box perturbation rounds).

## Published results preserved for comparison

`results/paper_reference/` contains reference values transcribed from the supplied PDF, including:

- Table I reconstructed 16×16 S-box;
- Table X NIST SP 800-22 p-values;
- Table XI NPCR/UACI values;
- Table XIV reported timings (`0.5551 s` at 512×512 and `0.1942 s` at 256×256 for the proposed method);
- Table XV Mandrill adjacent-pixel correlations;
- Table XVI entropy values (generally around `7.9992–7.9994`);
- `paper_reported_summary.json` for headline/S-box/robustness values.

The paper abstract reports average information entropy `7.9993` and post-encryption correlation close to `0.01`. These are **published reference claims**, not automatically reproduced by the bundled 64×64 synthetic image.

### S-box metric validation from the paper's Table I

The implementation can evaluate the exact S-box printed in Table I independent of S-box-generation ambiguities:

```bash
python experiments/run_sbox_analysis.py --paper-table-i
```

For that table, the implementation obtains component nonlinearities
`[106, 104, 102, 104, 102, 102, 102, 108]` (mean `103.75`) and a standard SAC mean of `0.501708984375`, consistent with the paper's rounded SAC comparison value `0.5017`. The repository deliberately does not claim exact reproduction of the paper's BIC-SAC value because its precise computation formula is not provided.

## Paper-to-code traceability

See [`docs/PAPER_IMPLEMENTATION_MAP.md`](docs/PAPER_IMPLEMENTATION_MAP.md) for the complete mapping. In compact form:

| Paper concept | Code | Experiment |
|---|---|---|
| 3D-LMM, Eq. (1) | `chaos.py` | `run_chaos_analysis.py` |
| SHA-512 key binding | `key_schedule.py` | `reproduce_core.py` |
| FSM, Eqs. (2)/(4) | `fsm.py` | `run_iteration_study.py` |
| 3-D S-box, Eq. (3) | `sbox3d.py` | `run_sbox_analysis.py` |
| XOR, Eqs. (5)/(6) | `confusion.py` | core round trip |
| FQM, Eqs. (7)–(12) | `fibonacci.py` | core round trip / tests |
| Complete encryption/decryption | `cipher.py` | `reproduce_core.py` |
| NPCR/UACI, Eq. (16) | `analysis/metrics.py` | `run_differential_analysis.py` |
| SSIM, Eq. (17) | `analysis/metrics.py` | `run_iteration_study.py` |
| Correlation, Eq. (18) | `analysis/metrics.py` | `run_statistical_analysis.py` |
| Entropy, Eq. (19) | `analysis/metrics.py` | `run_statistical_analysis.py` |
| Crop/noise robustness | `analysis/robustness.py` | `run_robustness.py` |

## Output conventions

- `results/paper_reference/` — values from the paper; never overwritten by experiments.
- `results/smoke/` — local synthetic verification committed for transparency.
- `results/generated/` — local experimental output; ignored by Git.
- `outputs/` — example outputs; ignored by Git.
- key JSON files — contain decryption material and should not be published for real secrets.

## Known limitations

1. **No original source code was supplied.** The repository cannot claim historical source-code identity or perform literal legacy-code cleanup.
2. **Several paper details are internally inconsistent or underspecified.** Every execution-critical choice is documented and exposed where practical.
3. **Paper datasets are absent.** Exact Tables XI–XVII cannot be re-run until matching source images and preprocessing are identified.
4. **NIST SP 800-22 settings are incomplete.** Published p-values are kept as reference only.
5. **Chaotic numerics are implementation-sensitive.** MATLAB/Python floating-point trajectories may diverge after many iterations.
6. **Image geometry is constrained.** The reconstructed FSM expects square power-of-two images; the paper itself notes difficulty with non-square video frames.
7. **Large images are expensive.** Repeated FSM stages and block FQM add overhead, consistent with the paper's discussion.
8. **Side-channel resistance is out of scope.** No constant-time or hardware countermeasures are implemented.
9. **Raspberry Pi deployment is not reproduced.** The paper reports Raspberry Pi 5 / 4 GB execution, but no board-specific files were supplied. `benchmark.py` is portable for local measurement.

## Testing and CI

```bash
pytest
python -m compileall -q src experiments examples scripts
```

GitHub Actions runs the pytest suite on Python 3.11 for pushes and pull requests. Behavioral changes to reconstructed algorithm stages should include or update a regression test and must document any paper-compatibility impact.

## Citation

If this repository contributes to your research, cite the original paper. Machine-readable metadata is in [`CITATION.cff`](CITATION.cff).

```bibtex
@article{Liao2025ThreeDSFF,
  author  = {Liao, Yunlong and Lin, Yiting and Xing, Zheng and Li, Qiutong and Huang, Guoheng and Chen, Donglong and Yuan, Xiaochen},
  title   = {Using 3D-LMM-Based Encryption to Secure Digital Images With 3-D S-Box and Fibonacci Q-Matrix},
  journal = {IEEE Internet of Things Journal},
  volume  = {12},
  number  = {24},
  year    = {2025},
  doi     = {10.1109/JIOT.2025.3624032}
}
```

## License

The reconstruction code is released under the [MIT License](LICENSE). The research paper and any third-party datasets remain under their respective copyright/license terms and are not relicensed by this repository.

## Project note

Due to various factors, including personnel changes, laboratory relocation, and equipment damage, the version of the released source code may differ slightly from the version originally used in the experiments. Some parts of the code may originate from an early demonstration version or an intermediate version produced during iterative debugging and maintenance. Nevertheless, the core ideas, methodology, and principal implementation of the project remain consistent with those described in the corresponding research work.
