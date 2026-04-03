---
source: ks_geometry.py
date_ingested: 2026-04-03
type: computation
---

# KS Geometry — Realizability Gap Experiments

## Purpose

Inverts the alphabet-based approach by building KS configurations directly from R^3 geometry, guaranteeing realizability by construction. Motivated by the "realizability gap" finding in ks_sat.py: random abstract KS-uncolorable hypergraphs are almost never realizable in R^3, so the geometric constraints are the bottleneck. This script eliminates that bottleneck by growing configurations from actual orthogonal frames.

Four experimental strategies are implemented. The overarching question: can continuous rotations access configurations invisible to any finite coordinate alphabet, and could such configurations be smaller than 31?

## Inputs

- No file inputs; all experiments are parameterized inline
- Optional: `ks_sat.py` for fast SAT-based `is_uncolorable` (falls back to built-in backtracking)
- `numpy`, `scipy` required

## Outputs

- Console output from all experiments
- Per-experiment: tested count, uncolorable count, best minimal ray count found
- Frame tree experiment: ray count distribution across tested configurations
- Angle scan: per-angle-family uncolorability rate and best minimal size
- Perturbed integer: per-epsilon uncolorability rate and best minimal size
- Mixed alphabets: per-mix colorability/uncolorability and minimized size

## Key Results

**Experiment 1 — Mixed Alphabets + Orthogonal Completion:**
Combines two algebraically independent alphabets (e.g., integer {0, ±1, ±2} with sqrt(2) {0, ±1, ±sqrt(2)}), then completes all orthogonal pairs via cross products. The cross products generate rays in NEITHER original alphabet. Tests whether this mixing can produce configurations smaller than 31. Tested mixes: int+sqrt2, int+sqrt3, int+phi, sqrt2+sqrt3, sqrt2+phi, int+sqrt5.

**Experiment 2 — Orthogonal Completion from Random Seeds:**
Starts with 8-25 random unit vectors, iteratively adds cross products of all orthogonal pairs until the pool stabilizes. Tests the resulting pool for KS-uncolorability. Runs 200 trials. Explores whether "generic" configurations can be KS-uncolorable.

**Experiment 3 — Perturbed Integer Alphabet:**
Starts from {0, ±1, ±2} (which produces CK-31) and adds continuous perturbations epsilon in {0.0, 0.01, 0.05, 0.1, 0.2, 0.5}. Tests whether the neighborhood of CK-31 in coordinate space contains smaller KS sets or whether the minimum jumps above 31 under perturbation.

**Experiment 4 — Frame Trees:**
Grows trees of orthogonal frames by rotating around shared axes using random angles (Rodrigues' formula). Depth 2, branching 2. Runs 100 trials, minimizes each uncolorable configuration found.

## Realizability Gap Summary

The script documents the insight (from ks_sat.py Phase 3) that geometric realizability in R^3 is the hard constraint for KS existence. Most combinatorially KS-uncolorable hypergraphs cannot be embedded in R^3. Building from frames sidesteps this: all configurations produced are realizable by construction.

The reference benchmark is: Trandafir & Cabello (2025) conjecture 31 is optimal; theoretical lower bound is 24 (Uijlen-Westerbaan 2016).

## Key Classes and Functions

- `RayPool` — manages a collection of rays with tolerance-based identification (merges rays within tol=1e-8)
- `rodrigues_rotation(axis, angle)` — rotation matrix via Rodrigues' formula
- `build_frame_tree(depth, branching, angle_source, seed_frame)` — grows BFS tree of orthogonal frames
- `build_multi_root_network(n_roots, depth, branching)` — star topology with shared z-axis
- `analyze_configuration(pool, triads, tol)` — finds ALL orthogonal pairs (including accidental ones)
- `build_from_orthogonal_completion(n_seed, max_iterations)` — pool-based completion from random seeds
- `build_from_perturbed_integer(perturbation, alphabet_range)` — integer coords plus noise
- `build_from_two_alphabets(alpha1, alpha2)` — mixed alphabet plus cross-product completion
- `minimize_ks_set(n, rays, pairs, triads, num_trials)` — randomized greedy minimization over ray indices

## Dependencies

- `numpy`, `scipy` — required for rotations and numerical optimization
- `ks_sat.py` — optional faster SAT coloring; built-in backtracking used as fallback
- [[ks-sat]] — provides `is_uncolorable`, `check_realizability`, `build_graph`
- [[algebraic-islands-main]] — CK-31 integer island is the baseline; goal is sub-31
- [[kochen-specker-theorem]] — the realizability gap is a geometric fact about KS sets
