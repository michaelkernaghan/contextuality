---
source: ks_islands.py
date_ingested: 2026-04-03
type: computation
---

# KS Islands — Algebraic Island Survey

## Purpose

Systematically searches for algebraic islands beyond CK-31: coordinate number fields or rings (other than the integers) that might support a KS set with fewer than 31 vectors. The core question is whether CK-31's minimality is a property of the integer coordinate ring specifically, or whether a different algebraic structure could yield a smaller set.

The script imports from `ks_sat.py` (SAT-based coloring) and `ks_complex.py` (Eisenstein/complex tools) and runs six experiments.

## Inputs

- No file inputs; parameters are hardcoded per experiment
- Optional: `python-sat` (Glucose4) for fast SAT checking; falls back to backtracking via `ks_complex.is_colorable`

## Outputs

- Console output only (no files written)
- Per-experiment tables reporting: ray count, orthogonal pair count, triad count, colorability status, and minimized KS subset size
- Reports whether each field is "CLOSED" or leaks new coordinate values under cross-product completion

## Key Results

Six experiments are run:

**Experiment 1 — Attractor Analysis (xy=2 family):**
Tests alphabets {0, ±1, ±t, ±2/t} for t in {sqrt(2), sqrt(3), phi, cbrt(4), sqrt(5), 3/2, pi/2, e/2}. After cross-product completion, checks whether the CK-31 rays are contained in the pool and whether the minimized KS set size matches 31. Confirms that any alphabet containing the xy=2 identity collapses to CK-31 under completion — CK-31 is an attractor.

**Experiment 2 — Novel Quadratic Fields {0, ±1, ±sqrt(d)}, d=2..30:**
Scans which quadratic extensions produce KS sets. The d=2 (Peres) field produces a KS set with minimum size 33. Fields where sqrt(d) is an integer are skipped. The experiment identifies the cancellation identity (e.g., d=1+1 for d=2) that enables each island.

**Experiment 3 — Product Families xy=k (k=2,3,5):**
Tests whether k>2 product identities produce different KS behavior. Reports colorability and minimum sizes for each alphabet family.

**Experiment 4 — Icosahedral Symmetry:**
Generates vertex, edge-midpoint, and face-center rays of the icosahedron (totaling 31 rays). Tests for orthogonal triads. Finds that icosahedral rays have no triads because the icosahedral group lacks 90-degree rotations (rotation orders are 2, 3, 5). Confirms that icosahedral symmetry CANNOT produce KS sets. Cross-product completion is also tested.

**Experiment 5 — Deep Eisenstein Search:**
Pushes the Eisenstein search (Z[omega], omega = e^{2*pi*i/3}) to larger coefficient bounds and norm cutoffs (up to coeff=3, norm<=7). All configurations found produce KS sets with minimum 33, consistent with the known complex minimum. No sub-33 complex KS set is found.

**Experiment 6 — Cross-Product Closure Analysis:**
For fields Q, Q(sqrt(2)), Q(sqrt(3)), Q(sqrt(5)), Q(phi), Q(sqrt(2),sqrt(3)), Q(2,sqrt(2)), Q(2,sqrt(3)): checks whether cross-product completion generates coordinates outside the field ("leaks"). Reports which fields are closed and which leak to a larger ring (e.g., to integers). A genuinely separate algebraic island must be closed under cross products.

## Dependencies

- [[ks-complex]] — Eisenstein ray generation, complex coloring, multi-trial minimization
- [[ks-sat]] — SAT-based KS coloring checker (optional)
- [[algebraic-islands-main]] — conceptual home of the island classification
- [[kochen-specker-theorem]] — background
