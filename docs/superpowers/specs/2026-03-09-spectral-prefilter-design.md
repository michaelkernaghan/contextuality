# Spectral Pre-Filter for KS Set Search

**Date**: 2026-03-09
**Status**: Design approved

## Problem

Searching for KS sets with fewer than 31 vectors in R^3 is computationally expensive. The existing pipelines (algebraic ray subset enumeration, abstract graph search, stitching) generate thousands of candidate orthogonality graphs, each tested for KS-uncolorability via SAT solver. Most candidates are colorable. A fast pre-filter that rejects obviously-colorable candidates before invoking SAT would significantly reduce search time.

## Solution

A cascading spectral filter module (`ks_spectral_filter.py`) that computes cheap graph-theoretic invariants from the adjacency matrix eigenvalues and rejects candidates that cannot be KS-uncolorable.

## Architecture

```
Candidate graph (n, pairs, triads)
        |
        v
  Layer 1: Fast eigenvalue filters (~us)
  - Hoffman bound, spectral gap, energy,
    algebraic connectivity, edge density, triad density
        | reject <---- fails thresholds
        v
  Layer 2: Lovasz theta SDP (~100ms)
  - Rigorous independence/chromatic bounds
        | reject <---- theta(G) too low
        v
  Layer 3: SAT solver (existing code)
```

## Module: ks_spectral_filter.py

### Public API

- `spectral_profile(n, pairs) -> dict`: Compute all Layer 1 invariants
- `profile_known_sets() -> None`: Profile all known KS sets + colorable controls, print analysis
- `determine_thresholds(profiles) -> dict`: Analyze profiles, return threshold constants
- `passes_fast_filter(n, pairs) -> bool`: Layer 1 check (eigenvalue-based)
- `passes_theta_filter(n, pairs) -> bool`: Layer 2 check (SDP, optional)
- `passes_spectral_filter(n, pairs) -> bool`: Combined Layer 1 + Layer 2

### Layer 1 Invariants

| Invariant | Formula | Intuition |
|-----------|---------|-----------|
| Hoffman bound | n * (-lambda_min) / (lambda_max - lambda_min) | Upper bound on independence number. Too large = too sparse for KS |
| Spectral gap | lambda_1 - lambda_2 | Expansion/connectivity. KS needs high connectivity |
| Algebraic connectivity | 2nd smallest eigenvalue of Laplacian L = D - A | Near-zero = nearly disconnected, constraints can't propagate |
| Energy | sum(abs(lambda_i)) | Total spectral weight, correlates with constraint density |
| Edge density | 2 * edges / (n * (n-1)) | Capped by R^3 geometry |
| Triad density | triads / n | CK-31: 17/31 ~ 0.55 |

### Layer 2: Lovasz Theta

Computed via SDP (cvxpy): maximize sum(M_ij) subject to M positive semidefinite, M_ij = 0 for edges, trace(M) = 1. Bounds independence number: alpha(G) <= theta(G) <= chi_bar(G). If theta suggests too much room for independent sets, the graph can't be KS-uncolorable.

### Threshold Determination

Empirical, via `profile_known_sets()`:

1. Compute invariants for all known KS-uncolorable sets (CK-31, 6 MUS-31s, Peres-33, Eisenstein-33, Z[sqrt(-2)]-33, golden-52)
2. Generate ~1000 colorable controls per KS set:
   - Remove 1, 2, 3 rays (colorable since all known sets are critical)
   - Random subsets of same size from parent pool
   - Random geometric configurations (rays on S^2)
3. For each invariant, find KS minimum vs colorable distribution
4. Invariants with clean separation become filters; overlapping ones are dropped

### Dependencies

- numpy (existing)
- scipy (existing)
- cvxpy (new, Layer 2 only, optional with graceful fallback)

### Data Sources

- CK-31: `CK31_INT` from `ks_30_budget.py`
- Peres, Eisenstein, Z[sqrt(-2)], Heegner-7 pools: `ks_graph_analysis.py`
- Minimized sets: `sat_minimize()` from `ks_new_islands.py`
- Golden ratio island: `ks_new_islands.py`

## Integration

One-line addition to each search pipeline:

```python
from ks_spectral_filter import passes_spectral_filter
if not passes_spectral_filter(n, pairs):
    continue  # skip SAT
```

Applies to:
- `ks_sub31_search.py` (algebraic ray subset enumeration)
- `ks_sat.py` (abstract graph search)
- `ks_stitching_search.py` (modular stitching)
- `ks_integer_pool_exhaustive.py` (exhaustive integer pool)

## Deliverables

1. `ks_spectral_filter.py` with profiling and filter functions
2. Profiling output showing which invariants discriminate KS from colorable
3. Hardcoded thresholds based on profiling results
4. Integration into search pipelines

## Research Value

Even if spectral filtering proves weak (invariants of KS and colorable graphs overlap), that is itself a result: KS-uncolorability would not be a spectral graph property, constraining future proof strategies. Either outcome advances understanding of the minimum KS set problem.
