# Reproduction Notes, Ambiguities, and Compatibility Decisions

This document separates paper-faithful implementation from details that had to be reconstructed. The source of truth is the supplied paper; choices below are made only when execution would otherwise be impossible or internally inconsistent.

## 1. SHA-512 normalization

Section II-A says that sixteen hexadecimal characters are converted to a decimal number and divided by `10^16`, *and* says the result lies in `[0,1]`. Those statements are not simultaneously true for an arbitrary 16-hex-digit integer.

The configuration exposes three modes:

- `paper_literal` (**default**): `int(hex_sample, 16) / 1e16`, exactly following the printed divisor;
- `hex_unit_interval`: divide by `16^16`, giving the natural `[0,1)` normalization;
- `paper_modulo_interval`: reduce modulo `1e16`, then divide by `1e16`.

Published tables cannot determine which historical MATLAB interpretation was used, so no mode is claimed to be the unavailable source-code behavior.

## 2. What bytes are hashed

The paper says “calculate the SHA-512 hash value of the plaintext image” without defining serialization. The default `pixel_bytes` hashes decoded row-major uint8 pixels, which is deterministic across file formats. An optional `file_bytes` mode hashes the original encoded file. The chosen mode is stored in key material.

## 3. FSM Step 1 / Step 2 duplication

Section II-B prints Step 1 and Step 2 with the same Seq1 construction text. The implementation treats them as one rule: build the driving sequence from a first-half `x_n` segment and second-half `y_n` segment, then consume groups of four to generate distinct `A^(1)` rank matrices.

## 4. FSM recurrence in Eq. (2)

Eq. (2) is typeset with a constant multiplier `4` in each generation. Taken literally, the third and later generations no longer form a permutation of `1..4^k`, so they cannot be used as the sorting index required by Eq. (4).

`fsm.py` therefore uses the sorting-preserving fractal recurrence in which each quadrant is shifted by the size of the previous matrix, `4^(k-1)`. This is a reconstruction required to preserve the defining property of an FSM. The choice is named `sorting_preserving` in configuration.

## 5. 3-D S-box dimensions

The prose initially states `8×4×4`, while Step 3, Fig. 3, and the `3:3:2` input-bit split in Fig. 4 require `8×8×4 = 256` entries. The code uses `8×8×4`.

## 6. S-box Step 2 “sort ... as index values”

Step 2 forms a deduplicated byte sequence and says to sort it in ascending order for use as index values. Sorting the values themselves would produce `0..255` and would not define a reorder unless the associated permutation is retained. The code therefore uses the stable `argsort` permutation of the Step-2 sequence to reorder `S11`.

## 7. Undefined `S22`

S-box Step 4 refers to `S22`, but the preceding text defines `S11` and `S12`, not `S22`. The default compatibility choice uses the nearest defined Step-2 driving values (`S12` before `argsort`) as the second-half source. This is exposed as `sbox_undefined_s22_source="s12_values"` and explicitly marked as reconstructed.

## 8. Eight S-box perturbation operations

The paper says that distinct `8×8` `A^(3)` perturbation matrices are applied through eight iterative operations, but does not specify exact layer scheduling. The implementation applies each reconstructed 8×8 FSM permutation to every one of the four S-box layers, successively for eight rounds.

## 9. Fibonacci Q-matrix typography

The standard Fibonacci identity is

`Q^n = [[F_(n+1), F_n], [F_n, F_(n-1)]]`.

The paper's Eq. (8) visually places an additional superscript `n` outside a matrix already written in terms of `F_n`. Exponentiating that Fibonacci matrix again would effectively double-apply the power. The implementation uses the standard identity and computes `Q^n` directly by modular exponentiation. Eq. (9)'s inverse is implemented as `Q^{-n}` modulo 256.

## 10. Complete decryption is not listed

The paper gives `Q^{-n}` but no full decryption flow. `decrypt_array` performs the unique natural inverse of the implemented bijective stages: inverse FQM → XOR → reverse inverse-FSM → inverse S-box.

## 11. NIST SP 800-22 exact reproduction

Table X provides p-values but not the tested bitstream length, float-to-bit quantization, selected sequence(s), suite version, significance setup, or individual test parameters. `export_nist_bitstream.py` provides a deterministic byte stream for external testing but does **not** claim to reproduce Table X exactly. The published p-values are preserved verbatim in `results/paper_reference/table_X_nist_800_22.csv`.

## 12. Lyapunov inconsistency inside the paper

The Fig. 5 caption states that the exponents tend to `2.005, 1.852, 1.5527`, whereas the nearby body text states `4.3080, 4.0041, 3.4112`. Both are preserved in `run_chaos_analysis.py` output. The QR/Benettin implementation reports its own computed values rather than choosing one published triplet as ground truth.

## 13. SSIM settings

Eq. (17) gives the standard SSIM formula and constants `C1=6.5025`, `C2=58.5225` but not window size, weighting, padding, or channel aggregation. The iteration script therefore uses a documented deterministic global-statistics variant. It should be treated as a trend reproduction, not a pixel-for-pixel recreation of Fig. 9.

## 14. Adjacent-pixel correlation sampling

The paper defines the correlation coefficient but does not state whether all adjacent pairs or a random subset were used for Table XV/Fig. 11. This project uses all valid adjacent pairs in horizontal, vertical, diagonal, and anti-diagonal directions.

## 15. Crop geometry

The paper gives 12.5% and 25% crop ratios and shows different locations visually, but does not fully define rectangular dimensions/coordinates. `crop_ciphertext` uses a square region with the requested area ratio and configurable center/top-left/left placement.

## 16. Paper datasets and image preprocessing

The paper names images such as Oakland, Splash, Mandrill, F-16, Sailboat, Peppers, and House but does not bundle the files here or fully specify their exact source versions/preprocessing. Paper tables are preserved as reference CSVs; no synthetic image is presented as a reproduction of those tables.

## 17. MATLAB vs Python floating-point behavior

The paper experiments used MATLAB 2022b. Python `float`/NumPy `float64` uses IEEE-754 binary64 and is a close numerical analogue, but chaotic systems amplify tiny implementation differences. Long sequences therefore should not be expected to be bit-identical to an unavailable MATLAB run unless all historical numerical details are known.

## 18. Security-use warning

This repository is research reproduction code, not a recommendation to deploy a custom image cipher in production. The paper itself notes future work on side-channel threats; this Python implementation has not been hardened for constant-time execution, key erasure, authenticated encryption, or production key management.
