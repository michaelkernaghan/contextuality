---
source: ks_search.py
date_ingested: 2026-04-03
type: computation
---

# KS Search — Randomized KS Minimization

## Purpose

The original alphabet-based KS search tool. Generates all rays from a coordinate alphabet, tests the full pool for KS-uncolorability, then uses randomized greedy minimization to find the smallest critical KS subset. This is the foundational search script from which the project grew.

The primary target is the integer alphabet {0, ±1, ±2} — the alphabet that produces CK-31. The script also defines and surveys several other predefined alphabets: Peres ({0, ±1, ±sqrt(2)}), {0, ±1, ±sqrt(3)}, golden ratio, and minimal {0, ±1}.

## Inputs

- Coordinate alphabet: a list of scalar values
- `num_trials`: number of randomized minimization trials (default 200; 1000 for deep integer search)
- CK-31 vectors hardcoded as `CK_31` for verification

## Outputs

- Console output per alphabet search
- Phase 1: verification of CK-31 (ray count, pair count, triad count, colorability)
  - If colorable (bug): shows the found coloring and diagnostic info
- Phase 2: per-alphabet results — best KS subset size, pair/triad counts, and explicit vector coordinates
- Size distribution across all minimization trials

## Key Results

**Phase 1 — CK-31 Verification:**
Verifies that the hardcoded CK-31 vectors form a KS-uncolorable set. Shows all triads. If the script finds CK-31 colorable, it runs diagnostics (which rays are not in any triad, which CK-31 rays are outside the integer alphabet pool).

**Phase 2 — Integer Alphabet Deep Search:**
The main result: alphabet {0, ±1, ±2} generates the pool containing CK-31. Running 1000 trials of randomized minimization consistently finds the minimum at 31 vectors, confirming CK-31 as the minimum for this alphabet.

**Other Alphabets:**
- Peres {0, ±1, ±sqrt(2)}: minimum 33 (Peres set)
- {0, ±1, ±sqrt(3)}: expected colorable (sqrt(3) produces no cancellation identity)
- Golden ratio: tested but expected no sub-31 set
- Extended {0, ±1, ±sqrt(2), ±2}: merges two islands; minimum expected at 31

## Predefined Alphabets

```python
ALPHABETS = {
    'peres':    {0, ±1, ±sqrt(2)},
    'integer_2': {0, ±1, ±2},
    'sqrt3':    {0, ±1, ±sqrt(3)},
    'extended': {0, ±1, ±sqrt(2), ±2},
    'golden':   {0, ±1, ±phi},
    'small':    {0, ±1},
}
```

## Key Functions

- `generate_rays(alphabet)` — generates all distinct rays from 3D coordinate combinations
- `canonicalize_ray(v)` — makes first nonzero component positive, normalizes by max component
- `is_colorable(vectors)` — backtracking coloring solver (green/red assignment)
- `minimize_ks_set(vectors)` — deterministic greedy minimization (order-dependent)
- `minimize_ks_set_randomized(vectors)` — randomized greedy (different removal orders reach different local minima)
- `multi_trial_minimize(vectors, num_trials)` — runs many randomized trials, reports size distribution
- `search_alphabet(alphabet, label, num_trials)` — full pipeline for one alphabet

## Dependencies

- Standard library only (`math`, `itertools`, `random`, `time`, `fractions`)
- [[kochen-specker-theorem]] — the coloring problem being solved
- [[algebraic-islands-main]] — the integer and Peres islands are primary targets
- [[ks-sat]] — provides a faster SAT-based `is_uncolorable` (ks_search.py has its own backtracker)
