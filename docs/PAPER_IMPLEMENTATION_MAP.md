# Paper → Algorithm → Code → Experiment Mapping

The table below is the primary traceability map for this repository. “Direct” means the paper gives enough information to implement the operation substantially as written. “Reconstructed” means a missing or contradictory detail required an explicit compatibility choice. “Reference-only” means the paper reports a result but does not provide enough information for exact reproduction.

| Paper location | Paper content | Algorithm/module | Primary code | Experiment / validation | Status |
|---|---|---|---|---|---|
| Sec. II-A, Eq. (1) | 3D-LMM recurrence | chaotic state generator | `src/threedsff/chaos.py` | `experiments/run_chaos_analysis.py` | Direct |
| Sec. II-A, Steps 1–3 | SHA-512 plaintext binding; sample every 8th digest character | key derivation | `src/threedsff/key_schedule.py` | `experiments/reproduce_core.py` | Reconstructed normalization choice |
| Sec. II-B, Eq. (2) | FSM generation from ranked groups of four | fractal sorting matrix | `src/threedsff/fsm.py` | round-trip tests; iteration study | Reconstructed recurrence shift |
| Sec. II-B | 16 FSM rounds for color images | spatial permutation | `src/threedsff/fsm.py`, `cipher.py` | `run_iteration_study.py` | Direct round count; reconstructed Seq1 consumption |
| Sec. II-C, Fig. 3 | chaotic 3-D S-box; 8 FSM perturbations | S-box generation | `src/threedsff/sbox3d.py` | `run_sbox_analysis.py` | Reconstructed due 8×4×4/8×8×4 and undefined `S22` |
| Sec. II-C, Eq. (3), Fig. 4 | split byte as `3:3:2`, index 3-D S-box | byte substitution | `sbox3d.py` | S-box inversion test | Direct |
| Eq. (4) | FSM relocation `C2(A^(k)(i)) = C1(i)` | forward/inverse spatial permutation | `fsm.py` | `test_fsm.py`, core round-trip | Direct |
| Eqs. (5)–(6) | `Seq2=floor(mod(y_n*10^10,256))`, XOR | confusion mask | `src/threedsff/confusion.py` | core round-trip | Direct |
| Eqs. (7)–(9) | Fibonacci sequence and Q-matrix / inverse | modular Q powers | `src/threedsff/fibonacci.py` | `test_fibonacci.py` | Reconstructed standard Q identity |
| Eqs. (10)–(12) | even `Seq3`; 2×2 block multiplication modulo 256 | FQM diffusion | `fibonacci.py` | core round-trip | Direct except Eq. 8 typography |
| Sec. III-A, Tables I–IX | S-box bijectivity, NL, SAC, BIC | S-box security metrics | `analysis/sbox_metrics.py` | `run_sbox_analysis.py` | Direct for bijective/NL/SAC; BIC formula underspecified |
| Sec. III-B, Figs. 5–7 | Lyapunov, bifurcation, 0–1 test | chaos diagnostics | `analysis/chaos_metrics.py` | `run_chaos_analysis.py` | Diagnostic reproduction; exact settings partly missing |
| Sec. III-B, Table X | NIST SP 800-22 | external randomness suite input | `export_nist_bitstream.py` | external NIST STS | Reference-only for exact p-values |
| Sec. III-C, Eq. (16), Tables XI–XIII | NPCR / UACI | differential metrics | `analysis/metrics.py` | `run_differential_analysis.py` | Direct metric; dataset unavailable |
| Sec. III-D, Table XIV | timing and approx. `O(N^2)` | benchmark | `experiments/benchmark.py` | local benchmark | Environment-dependent |
| Sec. III-E, Eq. (17), Figs. 8–9 | SSIM vs FSM rounds | iteration study | `analysis/metrics.py` | `run_iteration_study.py` | Reconstructed global SSIM because window unspecified |
| Sec. III-F, Figs. 10–11, Eq. (18) | histogram and adjacent-pixel correlation | statistical analysis | `analysis/metrics.py` | `run_statistical_analysis.py` | Direct metric; sampling convention not specified |
| Sec. III-F, Eq. (19), Tables XVI–XVII | information entropy | entropy metric | `analysis/metrics.py` | `run_statistical_analysis.py` | Direct metric |
| Sec. III-G | key sensitivity `d=10^-16`; plaintext `+1` sensitivity | sensitivity analysis | chaos / differential modules | `run_key_sensitivity.py`, `run_differential_analysis.py` | Reproducible concept; perturbed state axis not specified |
| Sec. III-H, Fig. 14 | all-black / all-white chosen plaintext | chosen-plaintext probe | cipher API | `run_chosen_plaintext.py` | Direct experiment concept |
| Sec. III-I, Figs. 15–16 | 12.5/25% crop; 10/20/30% salt-and-pepper noise | robustness perturbations | `analysis/robustness.py` | `run_robustness.py` | Reconstructed crop location/geometry where unspecified |
| Sec. III-J, Fig. 17 | Raspberry Pi 5, 4 GB deployment | deployment | portable Python package | `benchmark.py` | Hardware result not reproduced here |

## Decryption mapping

The paper explicitly gives the inverse Fibonacci Q-matrix `Q^{-n}` but does not provide a complete decryption pseudocode listing. Because every encryption stage is bijective under the reconstructed choices, decryption is implemented by reversing the published pipeline:

1. apply `Q^{-Seq3}` to every 2×2 block modulo 256;
2. XOR with the same `Seq2` mask;
3. apply the inverse FSM permutations in reverse round order;
4. apply the inverse 256-byte mapping of the 3-D S-box.

The SHA-512 digest is plaintext-bound, so it cannot be regenerated from ciphertext alone. `KeyMaterial` stores the derived initial conditions (plus the exact configuration) as the decryption sidecar. It must be treated as secret key material.
