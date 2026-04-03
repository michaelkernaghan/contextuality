---
source: ks_complex.py
date_ingested: 2026-04-03
type: computation
---

# KS Complex — Roots of Unity and Eisenstein Integer Analysis

## Purpose

Extends the real-valued KS search to complex vector spaces using Hermitian inner products. Generates and tests rays whose coordinates are Eisenstein integers Z[omega] (where omega = e^{2*pi*i/3} is a primitive cube root of unity). The cancellation engine here is the identity 1 + omega + omega^2 = 0, which replaces the real-valued 2 - 1 - 1 = 0 used by the Peres sqrt(2) island.

This is the primary library for complex KS computations. It is imported by `ks_islands.py` and indirectly used throughout.

## Inputs

- `max_coeff`: maximum absolute value of Eisenstein integer coefficients a, b in a + b*omega
- `norm_cutoff`: optional filter |v|^2 <= cutoff applied to component vectors
- `n_root`: for roots-of-unity generation, the order of the root (e.g., n_root=6 gives 6th roots)
- `num_trials`: number of randomized minimization trials

## Outputs

- Console output from search pipelines
- Per-search reports: ray count, orthogonal pair count, triad count, colorability status
- If uncolorable: minimum KS subset size found, size distribution across trials, pretty-printed vectors in Eisenstein notation (a + b*omega displayed as "a+bw")

## Key Results

**Phase 1 — Roots of Unity Survey:**
Tests n_root in {3, 4, 6} (cube, 4th, 6th roots of unity as coordinate alphabet). Reports whether any configuration is KS-uncolorable. 6th roots of unity (generating the Eisenstein integers) are expected to produce uncolorable sets.

**Phase 2 — Eisenstein Integer Search:**
- Eisenstein +/-1, norm cutoffs {3, 4, 6}: finds KS sets, minimizes to 33 vectors
- Eisenstein +/-2, norm cutoffs {4, 6, 8}: finds KS sets, minimizes to 33 vectors
- All configurations consistent with minimum complex KS set size = 33
- The Eisenstein 33-ray set is the complex analogue of the Peres 33-ray real set; its rigidity (vs. Peres flexibility) is a key result of the paper

## Eisenstein Arithmetic

- omega = e^{2*pi*i/3} = -1/2 + i*sqrt(3)/2
- omega^2 = -1 - omega = -1/2 - i*sqrt(3)/2
- Six units of Z[omega]: {1, -1, omega, -omega, omega^2, -omega^2}
- Norm: N(a + b*omega) = a^2 - ab + b^2 (always a non-negative integer)
- Hermitian inner product: <v1, v2> = sum conj(v1_k) * v2_k

## Key Functions (importable)

- `generate_eisenstein_rays(max_coeff, dim, norm_cutoff)` — ray generation from Z[omega]
- `generate_root_of_unity_rays(n_root, dim)` — ray generation from n-th roots
- `is_colorable(vectors)` — Hermitian coloring check (backtracking + propagation)
- `analyze_ray_set(vectors)` — returns n, pairs, triads dict
- `multi_trial_minimize(vectors, num_trials)` — randomized greedy minimization; returns (best, best_size, size_distribution)
- `canonicalize_complex_ray(v)` — normalizes by first nonzero component
- `hermitian_dot(v1, v2)` — Hermitian inner product
- `OMEGA` — the constant e^{2*pi*i/3}

## Dependencies

- Standard library only (`cmath`, `itertools`, `math`, `random`, `time`)
- No external dependencies for core library functions
- [[algebraic-islands-main]] — the Eisenstein island (min 33) is one of the six classified islands
- [[ks-islands]] — imports this module for complex analysis components
