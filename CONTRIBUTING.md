# Contributing

Contributions are welcome when they improve reproducibility without obscuring the distinction between paper text, reconstruction choices, and newly proposed extensions.

## Ground rules

1. Preserve the published 3DSFF algorithm unless a change is explicitly presented as an optional extension.
2. If a paper ambiguity is resolved differently, document the alternative in `docs/REPRODUCTION_NOTES.md` and expose it through a clearly named configuration option when practical.
3. Do not label locally generated data as a paper result. Published values belong in `results/paper_reference/`; generated outputs belong in `results/generated/`.
4. Add or update a regression test for any behavioral change in encryption, decryption, FSM, S-box, key derivation, FQM, or security metrics.
5. Avoid committing copyrighted benchmark images, secrets, generated key files, NIST temporary streams, caches, or large experiment outputs.
6. Keep public functions documented and use descriptive English names/comments for new implementation code.

## Local checks

```bash
pip install -e ".[dev]"
pytest
python -m compileall -q src experiments examples scripts
```

## Reporting paper/source discrepancies

An issue about a discrepancy is most useful when it includes the paper section/equation/figure/table, the observed code path, a minimal reproducer, and the proposed interpretation. When a claim depends on an external source, include a stable citation.
