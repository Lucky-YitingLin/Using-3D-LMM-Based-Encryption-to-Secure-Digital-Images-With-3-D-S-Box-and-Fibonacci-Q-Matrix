# 3DSFF Algorithm Walkthrough

## 1. Inputs and configuration

Input is an 8-bit grayscale or RGB image. The paper applies the same encryption treatment to the red, green, and blue channels. The reconstructed FSM currently requires a square power-of-two spatial size; FQM also requires even height and width because it operates on 2×2 blocks.

Paper defaults exposed by `configs/paper_default.json`:

- 3D-LMM: `a=0.5, b=2, c=0.5, d=0.5, e=0.2`;
- FSM rounds for color images: 16;
- S-box FSM perturbation rounds: 8;
- S-box burn-ins: 5000 and 10000;
- S-box scale: `2^10`;
- XOR/FQM scale: `10^10`;
- FQM exponent residue modulus: 64;
- output pixel modulus: 256.

## 2. Plaintext-bound key generation

1. Serialize the plaintext (`pixel_bytes` by default) and compute SHA-512.
2. From the 128-character hexadecimal digest, sample every eighth character starting at offsets 0, 1, and 2. Each sample contains 16 hex characters.
3. Convert each sample to an integer and normalize it according to the configured compatibility mode to obtain `x0`, `y0`, and `z0`.
4. Iterate Eq. (1) to produce `x_n`, `y_n`, and `z_n`.

The paper describes this as plaintext binding. Since the plaintext is unavailable at the receiver before decryption, the derived states/configuration are serialized in `KeyMaterial` for reproducible decryption. The sidecar is secret key material, not public metadata.

## 3. 3-D S-box generation

### 3.1 Filling values

From `x_n` after a 5000-state burn-in:

`byte = floor(mod(abs(x_n) * 2^10, 256))`.

Perform order-preserving deduplication until 256 unique bytes are obtained (`S11`).

### 3.2 Index-driving values

Repeat after a 10000-state burn-in to obtain 256 unique bytes (`S12`). Stable `argsort(S12)` is used as the reorder index for `S11`.

### 3.3 3-D layout and FSM perturbation

Reshape to `8×8×4`. Eight 8×8 FSM permutations are then applied to each 2-D layer. The exact treatment of the paper's undefined `S22` is documented in `REPRODUCTION_NOTES.md`.

### 3.4 Byte substitution

For input byte `p`:

- `m = p >> 5` (top 3 bits),
- `n = (p >> 2) & 0x7` (middle 3 bits),
- `z = p & 0x3` (low 2 bits),
- `C1 = Sbox[m,n,z]`.

Because the generated S-box is a permutation of all 256 bytes, an inverse lookup table exists for decryption.

## 4. FSM spatial permutation

A four-value chaotic group is ranked to a 2×2 `A^(1)` containing ranks 1–4. The fractal recurrence expands this matrix until its side matches the image. For each round, Eq. (4) is implemented as:

`C2[A_k(i)] = C1[i]`.

Color channels move together at each spatial position. The paper uses 16 rounds for color images.

## 5. XOR confusion

From `y_n`:

`Seq2 = floor(mod(y_n * 10^10, 256))`.

Reshape the needed values to image height × width and broadcast across color channels:

`C3 = C2 XOR Seq2`.

XOR is self-inverse.

## 6. Fibonacci Q-matrix transform

From `z_n`:

`raw = floor(mod(z_n * 10^10, 64))`.

Keep only even residues, then assign one exponent to each 2×2 spatial block. With the standard Fibonacci Q matrix

`Q = [[1,1],[1,0]]`,

compute each encrypted block as

`f = Cf × Q^n (mod 256)`.

The same exponent is used independently for R/G/B components of the block. The implementation performs matrix exponentiation directly modulo 256 to avoid unnecessarily large Fibonacci integers.

## 7. Decryption

Given the ciphertext and matching `KeyMaterial`:

1. regenerate 3D-LMM sequences and all deterministic artifacts;
2. multiply each ciphertext block by `Q^{-n} mod 256`;
3. XOR the same `Seq2` mask;
4. invert each FSM round in reverse order;
5. apply the inverse S-box lookup.

`tests/test_cipher.py` verifies exact byte-for-byte recovery.

## 8. Security-analysis modules

- `analysis/sbox_metrics.py`: bijectivity, component nonlinearity, SAC, BIC-SAC, BIC-NL;
- `analysis/chaos_metrics.py`: Jacobian, QR/Benettin Lyapunov estimate, Gottwald-Melbourne 0–1 statistic;
- `analysis/metrics.py`: Shannon entropy, NPCR, UACI, four-direction adjacent-pixel correlation, SSIM variant;
- `analysis/robustness.py`: controlled crop and salt-and-pepper ciphertext perturbations.

No DNA encoding or DNA operation is part of the paper's proposed 3DSFF method, so none is implemented.
