# Code Guide

This guide describes the role and provenance of every implementation/experiment file that is expected to be committed.

## Package: `src/threedsff/`

- `__init__.py` — public Python API: configuration, key material, `encrypt_array`, `decrypt_array`.
- `__main__.py` — enables `python -m threedsff`.
- `config.py` — dataclasses for explicit paper parameters and named compatibility choices. No algorithm is hidden in configuration.
- `key_schedule.py` — SHA-512 plaintext hashing, every-eighth-character sampling, normalization alternatives, and serializable `KeyMaterial`.
- `chaos.py` — Eq. (1) 3D-LMM recurrence, sequence generation, and sequence-length planning.
- `fsm.py` — group ranking, sorting-preserving fractal expansion, spatial permutation and inverse, per-round permutation generation.
- `sbox3d.py` — chaotic byte extraction/deduplication, 8×8×4 S-box construction, FSM perturbation, `3:3:2` substitution, and inverse mapping.
- `confusion.py` — Eq. (5) `Seq2` conversion and Eq. (6) XOR.
- `fibonacci.py` — modular 2×2 power, Fibonacci Q-matrix/inverse powers, Eq. (10) even iteration selection, FQM block transform/inverse.
- `io.py` — image load/save and geometry validation.
- `cipher.py` — composes the published encryption order and the documented reverse decryption order; exposes intermediate `CipherArtifacts` for audits/experiments.
- `cli.py` — `encrypt`, `decrypt`, and `metrics` commands.

## Analysis package: `src/threedsff/analysis/`

- `metrics.py` — per-channel Shannon entropy, NPCR/UACI, four-direction adjacent-pixel correlation, and a documented global SSIM variant using the paper's constants.
- `sbox_metrics.py` — bijectivity, Walsh nonlinearity, SAC, standard BIC-NL, and a documented common BIC-SAC interpretation.
- `chaos_metrics.py` — analytic Jacobian, QR/Benettin Lyapunov estimator, compact Gottwald-Melbourne 0–1 test, p–q trajectory.
- `robustness.py` — deterministic crop and salt-and-pepper perturbations of ciphertext.

## Experiment scripts

- `reproduce_core.py` — canonical one-image encrypt/decrypt/entropy/correlation run and exact recovery check.
- `run_sbox_analysis.py` — Section III-A metrics for either a generated S-box or the exact Table-I S-box.
- `run_chaos_analysis.py` — phase plots, Lyapunov, bifurcation, p–q / 0–1 diagnostics.
- `run_key_sensitivity.py` — Fig.-12-style `10^-16` initial-state perturbation with explicit axis selection.
- `export_nist_bitstream.py` — deterministic external NIST STS input; does not claim unavailable Table-X preprocessing.
- `run_differential_analysis.py` — 50-trial style plaintext `+1` probes with NPCR/UACI.
- `run_iteration_study.py` — FSM-round sweep with SSIM output.
- `run_statistical_analysis.py` — histogram, correlation, entropy.
- `run_chosen_plaintext.py` — all-black/all-white probes plus documented confusion+FQM-only black-image ablation interpretation.
- `run_robustness.py` — crop/noise attacks followed by decryption.
- `benchmark.py` — environment-local encryption/decryption timing.
- `run_all.py` — self-contained convenience subset.

## Tests

- `test_fsm.py` — verifies high-order FSM remains a complete permutation and is invertible.
- `test_fibonacci.py` — verifies `Q^n Q^-n = I (mod 256)` and RGB FQM round trip.
- `test_sbox.py` — verifies generated 3-D S-box bijectivity and inverse substitution.
- `test_cipher.py` — complete deterministic RGB encrypt/decrypt equality.
- `test_metrics.py` — basic entropy/NPCR/UACI correctness cases.
- `test_paper_sbox_metrics.py` — validates metric implementation against values computable directly from paper Table I.

## Supporting files

- `configs/paper_default.json` — paper-oriented defaults plus explicitly named reconstruction choices.
- `configs/smoke_test.json` — reduced-round development profile; never presented as the paper configuration.
- `scripts/generate_demo_image.py` — deterministic, redistribution-safe synthetic example generator.
- `examples/quickstart.py` — minimal programmatic API usage.
- `results/paper_reference/*` — published values transcribed from the paper, separated from generated output.
- `results/smoke/*` — local construction-time verification on the synthetic example.
- `data/README.md` — missing dataset/provenance explanation.
- `paper/README.md` — bibliographic information and PDF redistribution policy.

No file in this guide is claimed to be an original historical author source file because no source archive was supplied to the reconstruction session.
