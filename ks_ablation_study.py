"""
ks_ablation_study.py -- Ablation study: remove auxiliary rays in batches, track theta/alpha
============================================================================================

Peer review item #7: Show that auxiliary ray removal degrades CSW advantage smoothly/abruptly.
Also addresses #9 (robustness).
"""

import sys
import numpy as np
import cmath
import random
import cvxpy as cp
from scipy.optimize import linprog

# Unbuffered output
sys.stdout.reconfigure(line_buffering=True)

from ks_complex import canonicalize_complex_ray, hermitian_dot
from ks_new_islands import generate_rays_from_alphabet
from ks_new_island_analysis import build_pairs_triads
from ks_sat import is_uncolorable as sat_uncolorable

random.seed(42)
np.random.seed(42)

OMEGA = cmath.exp(2j * cmath.pi / 3)


def adjacency_matrix(n, pairs):
    A = np.zeros((n, n))
    for i, j in pairs:
        A[i, j] = 1.0
        A[j, i] = 1.0
    return A


def independence_number_ilp(n, pairs, timeout=30):
    """Compute alpha(G) via ILP."""
    from scipy.optimize import milp, LinearConstraint, Bounds
    c = -np.ones(n)  # maximize sum of x_i
    # Constraint: x_i + x_j <= 1 for each edge
    A_ub = np.zeros((len(pairs), n))
    for idx, (i, j) in enumerate(pairs):
        A_ub[idx, i] = 1
        A_ub[idx, j] = 1
    b_ub = np.ones(len(pairs))
    constraints = LinearConstraint(A_ub, ub=b_ub)
    bounds = Bounds(lb=0, ub=1)
    integrality = np.ones(n)
    result = milp(c, constraints=constraints, bounds=bounds, integrality=integrality)
    if result.success:
        return int(round(-result.fun))
    return None


def lovasz_theta_sdp(n, pairs):
    """Compute Lovasz theta via SDP (SCS solver)."""
    X = cp.Variable((n, n), symmetric=True)
    constraints = [X >> 0]  # PSD
    constraints += [cp.trace(X) == 1]
    for i, j in pairs:
        constraints += [X[i, j] == 0]
    obj = cp.Maximize(cp.sum(X))
    prob = cp.Problem(obj, constraints)
    try:
        prob.solve(solver=cp.SCS, eps=1e-6, max_iters=20000, verbose=False)
        if prob.status in ['optimal', 'optimal_inaccurate']:
            return prob.value
    except:
        pass
    return None


def fractional_packing(n, pairs, triads):
    """Compute alpha*(G) via LP."""
    c = -np.ones(n)
    A_ub = np.zeros((len(pairs), n))
    for idx, (i, j) in enumerate(pairs):
        A_ub[idx, i] = 1
        A_ub[idx, j] = 1
    b_ub = np.ones(len(pairs))
    bounds = [(0, 1)] * n
    result = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=bounds, method='highs')
    if result.success:
        return -result.fun
    return None


def classify_rays(rays, triads):
    """Classify rays as basis-participating or auxiliary."""
    basis_rays = set()
    for a, b, c in triads:
        basis_rays.add(a)
        basis_rays.add(b)
        basis_rays.add(c)
    auxiliary = [i for i in range(len(rays)) if i not in basis_rays]
    participating = sorted(basis_rays)
    return participating, auxiliary


def remove_rays(rays, pairs, triads, indices_to_remove):
    """Remove specified ray indices and rebuild pairs/triads."""
    keep = sorted(set(range(len(rays))) - set(indices_to_remove))
    new_rays = [rays[i] for i in keep]
    remap = {old: new for new, old in enumerate(keep)}
    keep_set = set(keep)
    new_pairs = [(remap[i], remap[j]) for i, j in pairs if i in keep_set and j in keep_set]
    new_triads = [(remap[a], remap[b], remap[c]) for a, b, c in triads
                  if a in keep_set and b in keep_set and c in keep_set]
    return new_rays, new_pairs, new_triads


# =====================================================================
# Build the Heegner-7 full pool
# =====================================================================
print("=" * 70)
print("ABLATION STUDY: Heegner-7 auxiliary ray removal")
print("=" * 70)

alpha_h7 = (1 + 1j * np.sqrt(7)) / 2
alpha_h7_bar = alpha_h7.conjugate()
alph = [0, 1, -1, alpha_h7, -alpha_h7, alpha_h7_bar, -alpha_h7_bar]

# Use raw alphabet rays only (no hermitian_completion) to match the paper's 145-ray pool
rays_full = generate_rays_from_alphabet(alph)
pairs_full, triads_full = build_pairs_triads(rays_full)

participating, auxiliary = classify_rays(rays_full, triads_full)
print(f"Full pool: {len(rays_full)} rays, {len(triads_full)} bases")
print(f"  Basis-participating: {len(participating)}, Auxiliary: {len(auxiliary)}")

# Shuffle auxiliary rays for random removal order
random.shuffle(auxiliary)

# Compute CSW for full pool
print(f"\nComputing CSW invariants for full pool...")
alpha_val = independence_number_ilp(len(rays_full), pairs_full)
theta_val = lovasz_theta_sdp(len(rays_full), pairs_full)
alpha_star = fractional_packing(len(rays_full), pairs_full, triads_full)
print(f"  alpha={alpha_val}, theta={theta_val:.3f}, alpha*={alpha_star:.3f}")
print(f"  theta/alpha = {theta_val/alpha_val:.4f}")

# Ablation: remove auxiliary rays in batches of ~10
print(f"\n{'Removed':>8s} {'Remaining':>10s} {'Aux left':>9s} {'Bases':>6s} {'alpha':>6s} {'theta':>8s} {'th/al':>7s} {'KS?':>4s}")
print("-" * 70)

batch_size = 16
results = []
removed_so_far = []

# Record full pool
results.append({
    'removed': 0, 'remaining': len(rays_full), 'aux_left': len(auxiliary),
    'bases': len(triads_full), 'alpha': alpha_val, 'theta': theta_val,
    'ratio': theta_val / alpha_val, 'ks': True
})
print(f"{0:>8d} {len(rays_full):>10d} {len(auxiliary):>9d} {len(triads_full):>6d} {alpha_val:>6d} {theta_val:>8.3f} {theta_val/alpha_val:>7.4f} {'Yes':>4s}")

for batch_start in range(0, len(auxiliary), batch_size):
    batch_end = min(batch_start + batch_size, len(auxiliary))
    removed_so_far.extend(auxiliary[batch_start:batch_end])

    new_rays, new_pairs, new_triads = remove_rays(rays_full, pairs_full, triads_full, removed_so_far)
    n_remaining = len(new_rays)
    aux_left = len(auxiliary) - len(removed_so_far)

    a = independence_number_ilp(n_remaining, new_pairs)
    t = lovasz_theta_sdp(n_remaining, new_pairs)

    if a and t:
        ratio = t / a
    else:
        ratio = None

    # Check KS-uncolorability
    ks = False
    if new_triads:
        ks = sat_uncolorable(n_remaining, new_pairs, new_triads)

    ks_str = "Yes" if ks else "No"
    ratio_str = f"{ratio:.4f}" if ratio else "N/A"
    t_str = f"{t:.3f}" if t else "N/A"
    a_str = f"{a}" if a else "N/A"

    results.append({
        'removed': len(removed_so_far), 'remaining': n_remaining, 'aux_left': aux_left,
        'bases': len(new_triads), 'alpha': a, 'theta': t,
        'ratio': ratio, 'ks': ks
    })
    print(f"{len(removed_so_far):>8d} {n_remaining:>10d} {aux_left:>9d} {len(new_triads):>6d} {a_str:>6s} {t_str:>8s} {ratio_str:>7s} {ks_str:>4s}")

# =====================================================================
# Summary
# =====================================================================
print("\n" + "=" * 70)
print("ABLATION SUMMARY")
print("=" * 70)

ks_lost_at = None
for r in results:
    if not r['ks'] and ks_lost_at is None:
        ks_lost_at = r['removed']

print(f"Auxiliary rays removed: 0 to {len(auxiliary)} in batches of {batch_size}")
print(f"Bases remain constant at {results[0]['bases']} (auxiliary rays don't participate in bases)")
if ks_lost_at:
    print(f"KS-uncolorability lost after removing {ks_lost_at} auxiliary rays")
else:
    print(f"KS-uncolorability preserved throughout (as expected -- auxiliary rays don't affect it)")

# Show theta/alpha trajectory
print(f"\ntheta/alpha trajectory:")
for r in results:
    ratio_str = f"{r['ratio']:.4f}" if r['ratio'] else "N/A"
    bar = "#" * int((r['ratio'] - 1.0) * 200) if r['ratio'] and r['ratio'] > 1 else ""
    print(f"  aux={r['aux_left']:>3d}: theta/alpha={ratio_str} {bar}")
