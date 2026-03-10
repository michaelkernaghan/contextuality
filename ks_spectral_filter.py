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

import math
import random
import numpy as np


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


def build_triads_from_pairs(n, pairs):
    """Find all triads (mutually orthogonal triples) from pairs."""
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


def profile_known_sets():
    """Compute spectral profiles for all known KS sets.

    Returns:
        dict mapping name -> spectral_profile dict
    """
    profiles = {}

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

    for name, coords in KS_REGISTRY.items():
        pairs = build_pairs_from_coords(coords)
        profiles[name] = spectral_profile(len(coords), pairs)

    return profiles


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

    calibrated = calibrate_thresholds(analysis)
    print(f"\n  Calibrated THRESHOLDS: {calibrated}")

    # Also compute Lovasz theta if available
    try:
        import cvxpy
        print()
        print("=" * 78)
        print("LOVASZ THETA VALUES")
        print("=" * 78)
        for name in sorted(ks_profiles.keys()):
            if name not in KS_REGISTRY:
                continue
            coords = KS_REGISTRY[name]
            pairs = build_pairs_from_coords(coords)
            theta = lovasz_theta(len(coords), pairs)
            print(f"  {name}: theta = {theta:.4f}")
    except ImportError:
        print("\ncvxpy not installed -- skipping Lovasz theta computation")
        print("Install with: pip install cvxpy")


if __name__ == "__main__":
    main()
