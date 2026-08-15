# Project Audit and Reconstruction Scope

## 1. Input inventory

The material supplied for this reconstruction contained **one item only**:

- the 14-page IEEE paper *Using 3D-LMM-Based Encryption to Secure Digital Images With 3-D S-Box and Fibonacci Q-Matrix* (3DSFF), DOI `10.1109/JIOT.2025.3624032`.

No original MATLAB source files, historical source snapshots, experiment scripts, input-image dataset, saved `.mat` workspaces, hardware deployment files, or project archive were supplied. Consequently, this repository is a **clean-room, paper-derived Python reconstruction**. There is no factual basis for claiming that any file here is an original author file, or for classifying unavailable source files as “core / obsolete / duplicated”.

This distinction is deliberate: whenever the paper is underspecified, contradictory, or silent, the repository records the issue rather than silently inventing an undocumented algorithm.

## 2. What was reconstructed

The following modules are supported directly by Sections II–III of the paper:

- 3D-LMM chaotic recurrence (Eq. 1);
- SHA-512 plaintext binding and sampled initial states (Section II-A, Steps 1–3);
- fractal-sorting-matrix initialization and iterative spatial permutation (Section II-B / Eq. 2 / Eq. 4);
- 3-D S-box byte substitution using the `3:3:2` bit split (Section II-C / Eq. 3);
- XOR confusion sequence from `y_n` (Eqs. 5–6);
- Fibonacci Q-matrix 2×2 block transform driven by even values from `z_n` (Eqs. 7–12);
- the mathematically necessary inverse pipeline for decryption;
- S-box, chaos, differential, statistical, sensitivity, chosen-plaintext, robustness, iteration-count, and local timing experiments described in Section III.

## 3. What was not invented

The current paper does **not** use DNA encoding or DNA arithmetic in the proposed 3DSFF pipeline. DNA operations appear only in related-work references. Therefore this repository intentionally contains no DNA module.

Likewise, this repository does not fabricate:

- the paper's missing exact dataset files or preprocessing steps;
- undocumented MATLAB helper functions;
- an undocumented exact NIST SP 800-22 bit-extraction procedure;
- a Raspberry Pi implementation that was not supplied;
- bit-for-bit reproduction of figures whose exact plotting/test settings are not specified.

## 4. Reference repository

The repository requested as an organizational reference,
`Lucky-YitingLin/Cryptanalyzing-an-image-cipher-using-multiple-chaos-and-DNA-operations`, uses a useful research-code pattern: separate `src`, `examples`, `tests`, `paper`, and `docs` areas; explicit implementation notes; paper-to-code mapping; self-contained generated examples; citation metadata; and repository audit documentation. This project adopts those *organizational principles* while using a structure and implementation specific to 3DSFF. No DNA code or algorithm from that repository is copied into this project.

## 5. Repository cleanup policy

Because the input contained no historical source tree, there were no unrelated legacy files to delete. The generated repository keeps only:

- source code needed by the paper reconstruction;
- runnable experiment scripts;
- tests;
- a small synthetic example image;
- reference values transcribed from the paper;
- documentation and packaging/CI files.

Generated experiment output is ignored under `results/generated/`. The small `results/smoke/` snapshot is retained only as a local verification record and is explicitly identified as **not a paper result**.
