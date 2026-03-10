# Spectral Pre-Filter Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a spectral pre-filter module that profiles known KS sets, identifies discriminating invariants, and provides a fast rejection function for candidate orthogonality graphs before SAT solving.

**Architecture:** A standalone module `ks_spectral_filter.py` with two filter layers (fast eigenvalue checks, optional Lovasz theta SDP) that integrates into existing search pipelines via a single `passes_spectral_filter()` call. Thresholds are determined empirically by profiling known KS sets against colorable controls.

**Tech Stack:** Python, numpy, scipy, pysat (existing); cvxpy (new, optional for Layer 2)

**Spec:** `docs/superpowers/specs/2026-03-09-spectral-prefilter-design.md`

---

## Chunk 1: Core Spectral Profiling

### Task 1: Spectral profile function with test

**Files:**
- Create: `ks_spectral_filter.py`
- Create: `test_spectral_filter.py`

- [ ] **Step 1: Write the failing test for spectral_profile**

```python
"""test_spectral_filter.py -- Tests for spectral pre-filter module."""
import math
import numpy as np
import pytest


def test_spectral_profile_returns_all_invariants():
    from ks_spectral_filter import spectral_profile, CK31_COORDS, build_pairs_from_coords
    pairs = build_pairs_from_coords(CK31_COORDS)
    profile = spectral_profile(len(CK31_COORDS), pairs)

    expected_keys = {
        'n', 'edges', 'lambda_max', 'lambda_min',
        'hoffman_bound', 'spectral_gap', 'algebraic_connectivity',
        'energy', 'edge_density', 'eigenvalues'
    }
    assert set(profile.keys()) == expected_keys


def test_spectral_profile_ck31_basic_properties():
    from ks_spectral_filter import spectral_profile, CK31_COORDS, build_pairs_from_coords
    pairs = build_pairs_from_coords(CK31_COORDS)
    profile = spectral_profile(len(CK31_COORDS), pairs)

    assert profile['n'] == 31
    assert profile['edges'] == len(pairs)
    assert profile['lambda_max'] > 0
    assert profile['lambda_min'] < 0
    assert profile['hoffman_bound'] > 0
    assert profile['spectral_gap'] > 0
    assert profile['algebraic_connectivity'] > 0
    assert profile['energy'] > 0
    assert 0 < profile['edge_density'] < 1


def test_spectral_profile_trivial_graph():
    """A graph with no edges should have degenerate spectral properties."""
    from ks_spectral_filter import spectral_profile
    profile = spectral_profile(5, [])

    assert profile['edges'] == 0
    assert profile['energy'] == pytest.approx(0, abs=1e-10)
    assert profile['edge_density'] == 0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd ~/contextuality && python -m pytest test_spectral_filter.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'ks_spectral_filter'`

- [ ] **Step 3: Write spectral_profile implementation**

```python
"""
ks_spectral_filter.py -- Spectral pre-filter for KS set search
===============================================================

Cascading spectral filter that rejects candidate orthogonality graphs
that cannot be KS-uncolorable, before invoking the expensive SAT solver.

Layer 1: Fast eigenvalue-based filters (~microseconds per graph)
Layer 2: Lovasz theta SDP (~100ms, optional, requires cvxpy)

Usage:
    from ks_spectral_filter import passes_spectral_filter
    if not passes_spectral_filter(n, pairs):
        continue  # skip SAT

Profiling:
    python ks_spectral_filter.py   # runs profile_known_sets()
"""

import numpy as np


def adjacency_matrix(n, pairs):
    """Build adjacency matrix from vertex count and edge list."""
    A = np.zeros((n, n))
    for i, j in pairs:
        A[i, j] = 1.0
        A[j, i] = 1.0
    return A


def laplacian_matrix(n, pairs):
    """Build Laplacian L = D - A."""
    A = adjacency_matrix(n, pairs)
    D = np.diag(A.sum(axis=1))
    return D - A


def spectral_profile(n, pairs):
    """Compute all Layer 1 spectral invariants for an orthogonality graph.

    Args:
        n: number of vertices (rays)
        pairs: list of (i, j) orthogonal pairs

    Returns:
        dict with keys: n, edges, lambda_max, lambda_min, hoffman_bound,
        spectral_gap, algebraic_connectivity, energy, edge_density, eigenvalues
    """
    edges = len(pairs)

    if edges == 0:
        return {
            'n': n,
            'edges': 0,
            'lambda_max': 0.0,
            'lambda_min': 0.0,
            'hoffman_bound': float('inf'),
            'spectral_gap': 0.0,
            'algebraic_connectivity': 0.0,
            'energy': 0.0,
            'edge_density': 0.0,
            'eigenvalues': tuple([0.0] * n),
        }

    A = adjacency_matrix(n, pairs)
    eigs = sorted(np.linalg.eigvalsh(A), reverse=True)

    lambda_max = eigs[0]
    lambda_min = eigs[-1]

    # Hoffman bound on independence number
    if lambda_max - lambda_min > 1e-12:
        hoffman = n * (-lambda_min) / (lambda_max - lambda_min)
    else:
        hoffman = float('inf')

    # Spectral gap
    spectral_gap = eigs[0] - eigs[1] if len(eigs) > 1 else 0.0

    # Algebraic connectivity (second-smallest eigenvalue of Laplacian)
    L = laplacian_matrix(n, pairs)
    lap_eigs = sorted(np.linalg.eigvalsh(L))
    algebraic_connectivity = lap_eigs[1] if len(lap_eigs) > 1 else 0.0

    # Energy
    energy = sum(abs(e) for e in eigs)

    # Edge density
    max_edges = n * (n - 1) / 2
    edge_density = edges / max_edges if max_edges > 0 else 0.0

    return {
        'n': n,
        'edges': edges,
        'lambda_max': lambda_max,
        'lambda_min': lambda_min,
        'hoffman_bound': hoffman,
        'spectral_gap': spectral_gap,
        'algebraic_connectivity': algebraic_connectivity,
        'energy': energy,
        'edge_density': edge_density,
        'eigenvalues': tuple(np.round(eigs, 10)),
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd ~/contextuality && python -m pytest test_spectral_filter.py -v`
Expected: 3 tests PASS

- [ ] **Step 5: Commit**

```bash
cd ~/contextuality
git add ks_spectral_filter.py test_spectral_filter.py
git commit -m "feat: add spectral_profile function with tests"
```

---

### Task 2: Profile known KS sets

**Files:**
- Modify: `ks_spectral_filter.py`
- Modify: `test_spectral_filter.py`

- [ ] **Step 1: Write test for build_pairs_from_coords helper**

Add to `test_spectral_filter.py`:

```python
def test_build_pairs_from_coords_ck31():
    from ks_spectral_filter import build_pairs_from_coords, CK31_COORDS
    pairs = build_pairs_from_coords(CK31_COORDS)
    # CK-31 has 71 orthogonal pairs (known from ks_30_budget.py analysis)
    assert len(pairs) == 71
    # All pairs should be valid indices
    for i, j in pairs:
        assert 0 <= i < 31
        assert 0 <= j < 31
        assert i < j
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd ~/contextuality && python -m pytest test_spectral_filter.py::test_build_pairs_from_coords_ck31 -v`
Expected: FAIL with `ImportError`

- [ ] **Step 3: Implement build_pairs_from_coords and KNOWN_KS_SETS data**

Add to `ks_spectral_filter.py`:

```python
import math


def build_pairs_from_coords(coords, tol=1e-9):
    """Build orthogonal pairs from coordinate vectors."""
    n = len(coords)
    pairs = []
    for i in range(n):
        for j in range(i + 1, n):
            dot = sum(a * b for a, b in zip(coords[i], coords[j]))
            if abs(dot) < tol:
                pairs.append((i, j))
    return pairs


def build_triads_from_pairs(n, pairs):
    """Find all triads (mutually orthogonal triples) from pairs."""
    pair_set = set(pairs) | {(j, i) for i, j in pairs}
    triads = []
    adj = [set() for _ in range(n)]
    for i, j in pairs:
        adj[i].add(j)
        adj[j].add(i)
    for i in range(n):
        for j in sorted(adj[i]):
            if j <= i:
                continue
            for k in sorted(adj[j]):
                if k <= j:
                    continue
                if k in adj[i]:
                    triads.append((i, j, k))
    return triads


# ============================================================
# Known KS sets for profiling
# ============================================================

CK31_COORDS = [
    (0, 0, 1), (0, 1, 0), (0, 1, 1), (0, 1, -1), (0, 1, 2), (0, 2, -1),
    (1, 0, 0), (1, 0, 1), (1, 0, -1), (1, 0, 2), (1, 0, -2),
    (1, 1, 0), (1, 1, 1), (1, 1, -1), (1, 1, 2), (1, -1, 0),
    (1, -1, 1), (1, -1, -1), (1, -1, -2), (1, 2, 0), (1, 2, -1),
    (1, -2, 0), (1, -2, 1), (2, 0, 1), (2, 0, -1), (2, 1, 0),
    (2, 1, 1), (2, 1, -1), (2, -1, 0), (2, -1, 1), (2, -1, -1)
]

_S2 = math.sqrt(2)
PERES33_COORDS = [
    (1, 0, 0), (0, 1, 0), (0, 0, 1),
    (1, 1, 0), (1, -1, 0), (1, 0, 1), (1, 0, -1), (0, 1, 1), (0, 1, -1),
    (1, 1, 1), (1, 1, -1), (1, -1, 1), (-1, 1, 1),
    (0, 1, _S2), (0, 1, -_S2), (1, 0, _S2), (1, 0, -_S2),
    (_S2, 1, 0), (_S2, -1, 0), (0, _S2, 1), (0, _S2, -1),
    (1, _S2, 0), (1, -_S2, 0), (_S2, 0, 1), (_S2, 0, -1),
    (1, _S2, 1), (1, _S2, -1), (1, -_S2, 1), (-1, _S2, 1),
    (_S2, 1, 1), (_S2, 1, -1), (_S2, -1, 1), (-_S2, 1, 1),
]

# Registry mapping name -> coordinates (extensible)
KS_REGISTRY = {
    'CK-31': CK31_COORDS,
    'Peres-33': PERES33_COORDS,
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd ~/contextuality && python -m pytest test_spectral_filter.py::test_build_pairs_from_coords_ck31 -v`
Expected: PASS

- [ ] **Step 5: Write test for profile_known_sets**

Add to `test_spectral_filter.py`:

```python
def test_profile_known_sets_returns_profiles():
    from ks_spectral_filter import profile_known_sets
    profiles = profile_known_sets()
    assert 'CK-31' in profiles
    assert 'Peres-33' in profiles
    for name, prof in profiles.items():
        assert prof['n'] > 0
        assert prof['edges'] > 0
        assert prof['lambda_max'] > 0
```

- [ ] **Step 6: Run test to verify it fails**

Run: `cd ~/contextuality && python -m pytest test_spectral_filter.py::test_profile_known_sets_returns_profiles -v`
Expected: FAIL

- [ ] **Step 7: Implement profile_known_sets**

Add to `ks_spectral_filter.py`:

```python
def profile_known_sets():
    """Compute spectral profiles for all known KS sets.

    Returns:
        dict mapping name -> spectral_profile dict
    """
    profiles = {}

    known_sets = {
        'CK-31': CK31_COORDS,
        'Peres-33': PERES33_COORDS,
    }

    # Also try to load complex pools from existing modules
    try:
        from ks_graph_analysis import build_pairs_triads
        from ks_new_islands import generate_rays_from_alphabet, sat_minimize
        from ks_complex import generate_eisenstein_rays

        # Eisenstein
        eis_rays = generate_eisenstein_rays(max_coeff=1, dim=3, norm_cutoff=3)
        eis_pairs, eis_triads = build_pairs_triads(eis_rays)
        eis_sub, eis_size, _ = sat_minimize(eis_rays, eis_pairs, eis_triads, n_trials=100)
        eis_s = set(eis_sub)
        eis_remap = {old: new for new, old in enumerate(sorted(eis_sub))}
        eis_min_pairs = [(eis_remap[a], eis_remap[b])
                         for a, b in eis_pairs if a in eis_s and b in eis_s]
        profiles['Eisenstein-33'] = spectral_profile(eis_size, eis_min_pairs)
    except ImportError:
        pass

    for name, coords in known_sets.items():
        pairs = build_pairs_from_coords(coords)
        profiles[name] = spectral_profile(len(coords), pairs)

    return profiles
```

- [ ] **Step 8: Run test to verify it passes**

Run: `cd ~/contextuality && python -m pytest test_spectral_filter.py::test_profile_known_sets_returns_profiles -v`
Expected: PASS

- [ ] **Step 9: Commit**

```bash
cd ~/contextuality
git add ks_spectral_filter.py test_spectral_filter.py
git commit -m "feat: add KS set profiling with CK-31, Peres-33, Eisenstein"
```

---

### Task 3: Generate colorable controls and discrimination analysis

**Files:**
- Modify: `ks_spectral_filter.py`
- Modify: `test_spectral_filter.py`

- [ ] **Step 1: Write test for generate_colorable_controls**

Add to `test_spectral_filter.py`:

```python
def test_generate_colorable_controls():
    from ks_spectral_filter import generate_colorable_controls, build_pairs_from_coords, CK31_COORDS
    pairs = build_pairs_from_coords(CK31_COORDS)
    controls = generate_colorable_controls(31, pairs, n_samples=50)
    assert len(controls) >= 10  # at least some controls generated
    for ctrl in controls:
        assert 'n' in ctrl
        assert ctrl['n'] < 31  # controls are subsets (smaller)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd ~/contextuality && python -m pytest test_spectral_filter.py::test_generate_colorable_controls -v`
Expected: FAIL

- [ ] **Step 3: Implement generate_colorable_controls**

Add to `ks_spectral_filter.py`:

```python
import random


def generate_colorable_controls(n, pairs, n_samples=200):
    """Generate spectral profiles of colorable subgraphs.

    For a known KS set, removing any single ray makes it colorable
    (since known KS sets are critical). We generate controls by
    removing 1, 2, and 3 rays.

    Args:
        n: number of vertices in the KS set
        pairs: edge list of the KS set
        n_samples: number of controls to generate

    Returns:
        list of spectral_profile dicts for colorable subgraphs
    """
    controls = []
    vertices = list(range(n))

    for _ in range(n_samples):
        # Remove 1, 2, or 3 rays randomly
        n_remove = random.choice([1, 2, 3])
        remove = set(random.sample(vertices, n_remove))
        keep = sorted(set(vertices) - remove)
        remap = {old: new for new, old in enumerate(keep)}

        sub_pairs = [(remap[a], remap[b]) for a, b in pairs
                     if a in remap and b in remap]
        sub_n = len(keep)

        if sub_pairs:
            controls.append(spectral_profile(sub_n, sub_pairs))

    return controls
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd ~/contextuality && python -m pytest test_spectral_filter.py::test_generate_colorable_controls -v`
Expected: PASS

- [ ] **Step 5: Write test for discrimination_analysis**

Add to `test_spectral_filter.py`:

```python
def test_discrimination_analysis():
    from ks_spectral_filter import discrimination_analysis, profile_known_sets
    ks_profiles = profile_known_sets()
    analysis = discrimination_analysis(ks_profiles)
    assert isinstance(analysis, dict)
    # Should contain entries for each invariant
    assert 'hoffman_bound' in analysis
    assert 'spectral_gap' in analysis
    # Each entry should have ks_min, control_p95, useful flag
    for key, info in analysis.items():
        assert 'ks_min' in info or 'ks_max' in info
        assert 'useful' in info
```

- [ ] **Step 6: Run test to verify it fails**

Run: `cd ~/contextuality && python -m pytest test_spectral_filter.py::test_discrimination_analysis -v`
Expected: FAIL

- [ ] **Step 7: Implement discrimination_analysis**

Add to `ks_spectral_filter.py`:

```python
def discrimination_analysis(ks_profiles, n_control_samples=500):
    """Analyze which spectral invariants discriminate KS from colorable.

    For each invariant, compares the range across known KS sets against
    the distribution across colorable controls.

    Args:
        ks_profiles: dict of name -> spectral_profile for known KS sets
        n_control_samples: controls per KS set

    Returns:
        dict mapping invariant_name -> {ks_min, ks_max, control_p5,
        control_p95, control_mean, useful, direction}
    """
    # Invariants to analyze (excludes 'eigenvalues' which is a tuple)
    invariant_keys = [
        'hoffman_bound', 'spectral_gap', 'algebraic_connectivity',
        'energy', 'edge_density'
    ]

    # Collect KS values
    ks_values = {k: [] for k in invariant_keys}
    for name, prof in ks_profiles.items():
        for k in invariant_keys:
            ks_values[k].append(prof[k])

    # Generate controls from each KS set using the registry
    all_controls = []
    for name, prof in ks_profiles.items():
        if name not in KS_REGISTRY:
            continue
        coords = KS_REGISTRY[name]
        pairs = build_pairs_from_coords(coords)
        controls = generate_colorable_controls(len(coords), pairs, n_control_samples)
        all_controls.extend(controls)

    control_values = {k: [] for k in invariant_keys}
    for ctrl in all_controls:
        for k in invariant_keys:
            control_values[k].append(ctrl[k])

    analysis = {}
    for k in invariant_keys:
        ks_vals = ks_values[k]
        ctrl_vals = control_values[k]

        if not ctrl_vals:
            analysis[k] = {'ks_min': min(ks_vals), 'ks_max': max(ks_vals),
                           'useful': False}
            continue

        ks_min_val = min(ks_vals)
        ks_max_val = max(ks_vals)
        ctrl_arr = np.array(ctrl_vals)
        ctrl_p5 = float(np.percentile(ctrl_arr, 5))
        ctrl_p95 = float(np.percentile(ctrl_arr, 95))
        ctrl_mean = float(np.mean(ctrl_arr))

        # For most invariants, KS sets should have HIGHER values
        # (more connected, more constrained)
        # Hoffman bound is an exception: lower = more constrained
        if k == 'hoffman_bound':
            useful = ks_max_val < ctrl_p95
            direction = 'upper'  # reject if above threshold
        else:
            useful = ks_min_val > ctrl_p5
            direction = 'lower'  # reject if below threshold

        analysis[k] = {
            'ks_min': ks_min_val,
            'ks_max': ks_max_val,
            'control_p5': ctrl_p5,
            'control_p95': ctrl_p95,
            'control_mean': ctrl_mean,
            'useful': useful,
            'direction': direction,
        }

    return analysis
```

- [ ] **Step 8: Run tests**

Run: `cd ~/contextuality && python -m pytest test_spectral_filter.py -v`
Expected: All PASS

- [ ] **Step 9: Commit**

```bash
cd ~/contextuality
git add ks_spectral_filter.py test_spectral_filter.py
git commit -m "feat: add colorable controls and discrimination analysis"
```

---

## Chunk 2: Filter Functions and Integration

### Task 4: Filter functions

**Files:**
- Modify: `ks_spectral_filter.py`
- Modify: `test_spectral_filter.py`

- [ ] **Step 1: Write test for passes_fast_filter**

Add to `test_spectral_filter.py`:

```python
def test_passes_fast_filter_ck31_passes():
    """CK-31 (a known KS set) should pass the filter."""
    from ks_spectral_filter import passes_fast_filter, build_pairs_from_coords, CK31_COORDS
    pairs = build_pairs_from_coords(CK31_COORDS)
    assert passes_fast_filter(31, pairs) is True


def test_passes_fast_filter_trivial_fails():
    """A trivial graph with no edges should fail."""
    from ks_spectral_filter import passes_fast_filter
    assert passes_fast_filter(5, []) is False


def test_passes_fast_filter_sparse_fails():
    """A very sparse graph (single edge) should fail."""
    from ks_spectral_filter import passes_fast_filter
    assert passes_fast_filter(30, [(0, 1)]) is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd ~/contextuality && python -m pytest test_spectral_filter.py::test_passes_fast_filter_ck31_passes -v`
Expected: FAIL

- [ ] **Step 3: Implement passes_fast_filter**

Add to `ks_spectral_filter.py`:

```python
# ============================================================
# Filter thresholds (determined by profiling, updated by
# running profile_known_sets and discrimination_analysis)
# ============================================================

# Placeholder thresholds -- these will be refined after the first
# profiling run. Set conservatively so no known KS set is rejected.
THRESHOLDS = {
    'min_edge_density': 0.01,        # very conservative initial
    'min_algebraic_connectivity': 0.1,
    'min_energy': 5.0,
    'min_spectral_gap': 0.1,
    'max_hoffman_bound': 100.0,      # very permissive initial
}


def passes_fast_filter(n, pairs):
    """Layer 1: Fast eigenvalue-based filter.

    Returns True if the graph passes all spectral thresholds
    (i.e., could potentially be KS-uncolorable).
    Returns False if the graph definitely cannot be KS-uncolorable.

    Runs in ~microseconds (eigenvalue computation of small matrices).
    """
    if not pairs:
        return False

    profile = spectral_profile(n, pairs)

    if profile['edge_density'] < THRESHOLDS['min_edge_density']:
        return False
    if profile['algebraic_connectivity'] < THRESHOLDS['min_algebraic_connectivity']:
        return False
    if profile['energy'] < THRESHOLDS['min_energy']:
        return False
    if profile['spectral_gap'] < THRESHOLDS['min_spectral_gap']:
        return False
    if profile['hoffman_bound'] > THRESHOLDS['max_hoffman_bound']:
        return False

    return True


def passes_spectral_filter(n, pairs):
    """Combined Layer 1 + Layer 2 filter.

    Returns True if the graph passes all spectral checks.
    Layer 2 (Lovasz theta) is only run if cvxpy is available.
    """
    if not passes_fast_filter(n, pairs):
        return False

    # Layer 2: Lovasz theta (optional)
    try:
        if not passes_theta_filter(n, pairs):
            return False
    except Exception:
        pass  # skip Layer 2 if cvxpy unavailable or SDP fails

    return True
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd ~/contextuality && python -m pytest test_spectral_filter.py -k "fast_filter" -v`
Expected: 3 PASS

- [ ] **Step 5: Commit**

```bash
cd ~/contextuality
git add ks_spectral_filter.py test_spectral_filter.py
git commit -m "feat: add passes_fast_filter with conservative thresholds"
```

---

### Task 5: Lovasz theta filter (Layer 2)

**Files:**
- Modify: `ks_spectral_filter.py`
- Modify: `test_spectral_filter.py`

- [ ] **Step 1: Write test for lovasz_theta**

Add to `test_spectral_filter.py`:

```python
def test_lovasz_theta_complete_graph():
    """For complete graph K_n, theta = 1."""
    pytest.importorskip("cvxpy")
    from ks_spectral_filter import lovasz_theta
    # K_4: all pairs connected
    pairs = [(i, j) for i in range(4) for j in range(i+1, 4)]
    theta = lovasz_theta(4, pairs)
    assert theta == pytest.approx(1.0, abs=0.1)


def test_lovasz_theta_empty_graph():
    """For empty graph (no edges), theta = n."""
    pytest.importorskip("cvxpy")
    from ks_spectral_filter import lovasz_theta
    theta = lovasz_theta(5, [])
    assert theta == pytest.approx(5.0, abs=0.1)


def test_lovasz_theta_ck31():
    """CK-31 should have a finite theta value."""
    pytest.importorskip("cvxpy")
    from ks_spectral_filter import lovasz_theta, build_pairs_from_coords, CK31_COORDS
    pairs = build_pairs_from_coords(CK31_COORDS)
    theta = lovasz_theta(31, pairs)
    assert 1.0 < theta < 31.0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd ~/contextuality && python -m pytest test_spectral_filter.py::test_lovasz_theta_complete_graph -v`
Expected: FAIL (function doesn't exist yet)

- [ ] **Step 3: Implement lovasz_theta and passes_theta_filter**

Add to `ks_spectral_filter.py`:

```python
def lovasz_theta(n, pairs):
    """Compute Lovasz theta function via SDP.

    theta(G) = max { sum_ij M_ij : M psd, trace(M) = 1, M_ij = 0 for edges }

    Requires cvxpy. Returns float.
    """
    import cvxpy as cp

    M = cp.Variable((n, n), symmetric=True)
    constraints = [M >> 0, cp.trace(M) == 1]

    # Zero out entries for edges
    for i, j in pairs:
        constraints.append(M[i, j] == 0)

    # All entries non-negative (for independence number formulation)
    constraints.append(M >= 0)

    objective = cp.Maximize(cp.sum(M))
    prob = cp.Problem(objective, constraints)
    prob.solve(solver=cp.SCS, verbose=False, max_iters=5000)

    if prob.status in ('optimal', 'optimal_inaccurate'):
        return prob.value
    return float('inf')


# Threshold for Lovasz theta (updated by profiling)
THETA_THRESHOLD = None  # set after profiling


def passes_theta_filter(n, pairs):
    """Layer 2: Lovasz theta SDP filter.

    Returns True if theta(G) is consistent with KS-uncolorability.
    Returns True (pass) if cvxpy is unavailable or threshold not set.
    """
    if THETA_THRESHOLD is None:
        return True  # no threshold set yet, pass by default

    theta = lovasz_theta(n, pairs)
    # KS sets need tightly constrained independence structure
    # If theta is too large, the graph is too "loose"
    return theta <= THETA_THRESHOLD
```

- [ ] **Step 4: Run tests**

Run: `cd ~/contextuality && python -m pytest test_spectral_filter.py -k "lovasz" -v`
Expected: PASS (or skip if cvxpy not installed)

- [ ] **Step 5: Commit**

```bash
cd ~/contextuality
git add ks_spectral_filter.py test_spectral_filter.py
git commit -m "feat: add Lovasz theta SDP filter (Layer 2, optional)"
```

---

### Task 6: Main profiling script and threshold calibration

**Files:**
- Modify: `ks_spectral_filter.py`

- [ ] **Step 1: Implement main() profiling runner**

Add to `ks_spectral_filter.py`:

```python
def print_profiling_report(ks_profiles, analysis):
    """Print a formatted report of profiling results."""
    print("=" * 78)
    print("SPECTRAL PROFILES: Known KS Sets")
    print("=" * 78)
    header = f"{'Set':<18s} {'n':>3s} {'edges':>5s} {'Hoffman':>8s} " \
             f"{'gap':>7s} {'alg_conn':>8s} {'energy':>7s} {'density':>7s}"
    print(header)
    print("-" * 78)
    for name, prof in sorted(ks_profiles.items()):
        print(f"{name:<18s} {prof['n']:3d} {prof['edges']:5d} "
              f"{prof['hoffman_bound']:8.3f} {prof['spectral_gap']:7.3f} "
              f"{prof['algebraic_connectivity']:8.3f} {prof['energy']:7.2f} "
              f"{prof['edge_density']:7.4f}")

    print()
    print("=" * 78)
    print("DISCRIMINATION ANALYSIS")
    print("=" * 78)
    header = f"{'Invariant':<25s} {'KS min':>8s} {'KS max':>8s} " \
             f"{'Ctrl p5':>8s} {'Ctrl p95':>8s} {'Useful?':>8s}"
    print(header)
    print("-" * 78)
    for key, info in sorted(analysis.items()):
        if 'control_p5' not in info:
            continue
        useful = "YES" if info['useful'] else "no"
        print(f"{key:<25s} {info['ks_min']:8.3f} {info['ks_max']:8.3f} "
              f"{info['control_p5']:8.3f} {info['control_p95']:8.3f} "
              f"{useful:>8s}")

    # Recommend thresholds
    print()
    print("=" * 78)
    print("RECOMMENDED THRESHOLDS")
    print("=" * 78)
    for key, info in sorted(analysis.items()):
        if not info.get('useful'):
            continue
        if info.get('direction') == 'lower':
            # KS sets are above this, use 90% of KS min as threshold
            threshold = info['ks_min'] * 0.9
            print(f"  {key}: >= {threshold:.4f}  (KS min = {info['ks_min']:.4f})")
        elif info.get('direction') == 'upper':
            threshold = info['ks_max'] * 1.1
            print(f"  {key}: <= {threshold:.4f}  (KS max = {info['ks_max']:.4f})")


def main():
    """Run full profiling and discrimination analysis."""
    random.seed(42)
    np.random.seed(42)

    print("Profiling known KS sets...")
    ks_profiles = profile_known_sets()

    print(f"Profiled {len(ks_profiles)} KS sets")
    print("Running discrimination analysis...")
    analysis = discrimination_analysis(ks_profiles, n_control_samples=500)

    print_profiling_report(ks_profiles, analysis)

    # Also compute Lovasz theta if available
    try:
        import cvxpy
        print()
        print("=" * 78)
        print("LOVASZ THETA VALUES")
        print("=" * 78)
        for name in sorted(ks_profiles.keys()):
            if name == 'CK-31':
                pairs = build_pairs_from_coords(CK31_COORDS)
                n = 31
            elif name == 'Peres-33':
                pairs = build_pairs_from_coords(PERES33_COORDS)
                n = 33
            else:
                continue
            theta = lovasz_theta(n, pairs)
            print(f"  {name}: theta = {theta:.4f}")
    except ImportError:
        print("\ncvxpy not installed -- skipping Lovasz theta computation")
        print("Install with: pip install cvxpy")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Run the profiling script**

Run: `cd ~/contextuality && python ks_spectral_filter.py`
Expected: Profiling output with spectral invariants for CK-31 and Peres-33, discrimination analysis showing which invariants are useful, and recommended thresholds.

- [ ] **Step 3: Update THRESHOLDS using calibrate_thresholds**

Add a `calibrate_thresholds()` function that deterministically maps discrimination analysis to threshold values, then call it from `main()`:

```python
def calibrate_thresholds(analysis):
    """Deterministically set filter thresholds from discrimination analysis.

    For 'lower' direction invariants (KS sets have higher values):
        threshold = ks_min * 0.9  (10% safety margin)
    For 'upper' direction invariants (KS sets have lower values):
        threshold = ks_max * 1.1  (10% safety margin)

    Only sets thresholds for invariants marked as 'useful'.

    Returns:
        dict of threshold values ready to assign to THRESHOLDS
    """
    global THRESHOLDS
    for key, info in analysis.items():
        if not info.get('useful'):
            continue
        if info['direction'] == 'lower':
            threshold_val = info['ks_min'] * 0.9
            # Map to THRESHOLDS key
            if key == 'algebraic_connectivity':
                THRESHOLDS['min_algebraic_connectivity'] = threshold_val
            elif key == 'energy':
                THRESHOLDS['min_energy'] = threshold_val
            elif key == 'spectral_gap':
                THRESHOLDS['min_spectral_gap'] = threshold_val
            elif key == 'edge_density':
                THRESHOLDS['min_edge_density'] = threshold_val
        elif info['direction'] == 'upper':
            threshold_val = info['ks_max'] * 1.1
            if key == 'hoffman_bound':
                THRESHOLDS['max_hoffman_bound'] = threshold_val
    return dict(THRESHOLDS)
```

Call from `main()` after `discrimination_analysis()`:
```python
    calibrated = calibrate_thresholds(analysis)
    print(f"\n  Calibrated THRESHOLDS: {calibrated}")
```

- [ ] **Step 4: Run all tests**

Run: `cd ~/contextuality && python -m pytest test_spectral_filter.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
cd ~/contextuality
git add ks_spectral_filter.py
git commit -m "feat: add profiling runner and calibrate thresholds"
```

---

### Task 7: Integration into search pipelines

**Files:**
- Modify: `ks_sub31_search.py` (add spectral filter call)
- Modify: `ks_sat.py` (add spectral filter call)

- [ ] **Step 1: Read current search loop in ks_sub31_search.py**

Read `ks_sub31_search.py` to identify the exact location where SAT is called in the search loop, so the spectral filter can be inserted before it.

- [ ] **Step 2: Add spectral filter import and call in ks_sub31_search.py**

At the top of `ks_sub31_search.py`, add:

```python
try:
    from ks_spectral_filter import passes_fast_filter
    HAS_SPECTRAL = True
except ImportError:
    HAS_SPECTRAL = False
```

Before each `is_ks_uncolorable_full()` call in the search loop, add:

```python
if HAS_SPECTRAL and not passes_fast_filter(n_sub, sub_pairs):
    filtered_count += 1
    continue
```

Add a counter `filtered_count = 0` at the start of the search and print it at the end:
```python
print(f"  Spectrally filtered: {filtered_count}")
```

- [ ] **Step 3: Add spectral filter to ks_sat.py**

Same pattern: import with fallback, insert `passes_fast_filter` check before SAT calls in the abstract graph search loop.

- [ ] **Step 4: Run existing tests to verify no regressions**

Run: `cd ~/contextuality && python -m pytest test_spectral_filter.py -v`
Expected: All PASS

- [ ] **Step 5: Commit**

```bash
cd ~/contextuality
git add ks_sub31_search.py ks_sat.py ks_spectral_filter.py test_spectral_filter.py
git commit -m "feat: integrate spectral pre-filter into search pipelines"
```
