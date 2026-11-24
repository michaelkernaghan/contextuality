# Archived scripts (not used by the current paper)

Scripts written for versions 1-9 of *The Algebraic Landscape of Kochen-Specker Sets in Dimension
Three*, for the letters in [`../letters/`](../letters), and the drivers that sent drafts to a
second language model for review. None of them is named by version 11 of the paper, the README
or the ledger, and none is imported by a script that is.

**Do not use these to reproduce the current paper.** Several compute quantities that version 11
withdraws (the "islands" lists, BPQS and Cabello-Severini-Winter tables, rigidity, "merge
saturation"). The scripts were not re-run or re-checked when they were moved here.

## Running one

About half of them import modules that remain in the repository root (`ks_complex`,
`ks_new_islands`, `ks_sat`, `ks_islands`, `ks_graph_analysis`). Run from the repository root with
the root on the module path:

```bash
PYTHONPATH=. python archive/scripts/NAME.py
```

Some scripts open data files by relative path and expect the repository root as the working
directory. The review drivers (`oxford_review*.py`, `peer_review_galois*.py`,
`build_review_bundle.py`, `submit_site_review.py`) contain absolute paths on the author's machine,
some to paper files that have since moved to [`../paper/`](../paper) and
[`../letters/`](../letters); they are kept as a record of how each review was requested and will
not run elsewhere unchanged.
