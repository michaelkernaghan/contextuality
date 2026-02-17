"""
ks_trig.py — Trigonometric family of KS ray sets
=================================================

Explores the identity cos²θ + sin²θ = 1 as a cancellation mechanism
for constructing Kochen-Specker sets in R³.

Alphabet: {0, ±1, ±cosθ, ±sinθ}

The Pythagorean identity provides orthogonalities such as:
    (cosθ, sinθ, -1) · (cosθ, sinθ, 1) = cos²θ + sin²θ - 1 = 0

This gives a continuous one-parameter family that should recover known
islands at special angles (e.g. θ=π/4 → Peres-like) and may reveal
new ones.

Key questions:
  1. For which θ is the ray pool KS-uncolorable?
  2. Does cross-product completion stay finite?
  3. Are there new islands beyond the known six?
  4. Is there a continuous interval of uncolorable angles, or only isolated points?

Requires: numpy, python-sat
"""

import numpy as np
import math
import itertools
import random
import time
import sys
import io
from fractions import Fraction

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

random.seed(42)

# ============================================================
# SAT solver
# ============================================================

try:
    from pysat.solvers import Glucose4
    HAS_SAT = True
except ImportError:
    HAS_SAT = False
    print("WARNING: pysat not found. Install with: pip install python-sat")

def sat_uncolorable(n, pairs, triads):
    """Check if a ray configuration is KS-uncolorable via SAT."""
    if not HAS_SAT or not triads:
        return False
    clauses = []
    triad_pair_set = set()
    for a, b, c in triads:
        A, B, C = a + 1, b + 1, c + 1
        clauses.append([A, B, C])
        clauses.append([-A, -B])
        clauses.append([-A, -C])
        clauses.append([-B, -C])
        for x, y in [(a,b), (a,c), (b,c)]:
            triad_pair_set.add((min(x,y), max(x,y)))
    for a, b in pairs:
        key = (min(a,b), max(a,b))
        if key not in triad_pair_set:
            clauses.append([-(a+1), -(b+1)])
    with Glucose4() as solver:
        for c in clauses:
            solver.add_clause(c)
        return not solver.solve()

# ============================================================
# Ray generation and orthogonality
# ============================================================

def canonicalize_ray(v, tol=1e-10):
    """Canonicalize a real ray: first nonzero positive, scale max to 1."""
    if all(abs(x) < tol for x in v):
        return None
    v = list(v)
    for x in v:
        if abs(x) > tol:
            if x < 0:
                v = [-x for x in v]
            break
    m = max(abs(x) for x in v)
    return tuple(round(x / m, 10) for x in v)


def generate_rays(alphabet):
    """Generate all distinct rays from alphabet in R³."""
    rays_set = set()
    rays_list = []
    for combo in itertools.product(alphabet, repeat=3):
        canon = canonicalize_ray(combo)
        if canon is not None and canon not in rays_set:
            rays_set.add(canon)
            rays_list.append(tuple(combo))
    return rays_list, rays_set


def dot(v1, v2):
    return sum(a * b for a, b in zip(v1, v2))


def cross(v1, v2):
    return (
        v1[1]*v2[2] - v1[2]*v2[1],
        v1[2]*v2[0] - v1[0]*v2[2],
        v1[0]*v2[1] - v1[1]*v2[0],
    )


def find_pairs(rays, tol=1e-9):
    """Find all orthogonal pairs."""
    n = len(rays)
    pairs = []
    for i in range(n):
        for j in range(i+1, n):
            if abs(dot(rays[i], rays[j])) < tol:
                pairs.append((i, j))
    return pairs


def find_triads(rays, pairs):
    """Find all orthogonal triads (bases)."""
    pair_set = set(pairs)
    triads = []
    n = len(rays)
    for i in range(n):
        for j in range(i+1, n):
            if (i,j) not in pair_set:
                continue
            for k in range(j+1, n):
                if (i,k) in pair_set and (j,k) in pair_set:
                    triads.append((i,j,k))
    return triads


def cross_product_completion(rays, max_iters=10, tol=1e-9):
    """Complete ray set by adding cross products of orthogonal pairs."""
    rays_set = set()
    for r in rays:
        c = canonicalize_ray(r)
        if c:
            rays_set.add(c)

    expanded = list(rays)
    for iteration in range(max_iters):
        new_rays = []
        n = len(expanded)
        for i in range(n):
            for j in range(i+1, n):
                if abs(dot(expanded[i], expanded[j])) < tol:
                    cp = cross(expanded[i], expanded[j])
                    norm = math.sqrt(sum(x*x for x in cp))
                    if norm < tol:
                        continue
                    canon = canonicalize_ray(cp)
                    if canon and canon not in rays_set:
                        rays_set.add(canon)
                        # Store unnormalized for better numerics
                        new_rays.append(cp)
        if not new_rays:
            break
        expanded.extend(new_rays)
    return expanded


def sat_minimize(rays, pairs, triads, n_trials=200):
    """SAT-based randomized greedy minimization."""
    n = len(rays)
    best_size = n
    best_subset = list(range(n))
    sizes = {}

    for trial in range(n_trials):
        current = list(range(n))
        random.shuffle(current)
        removed = True
        while removed:
            removed = False
            order = list(current)
            random.shuffle(order)
            for r in order:
                candidate = [x for x in current if x != r]
                if len(candidate) < 3:
                    break
                s = set(candidate)
                remap = {old: new for new, old in enumerate(sorted(candidate))}
                sp = [(remap[a], remap[b]) for a, b in pairs if a in s and b in s]
                st = [(remap[a], remap[b], remap[c]) for a, b, c in triads
                      if a in s and b in s and c in s]
                if st and sat_uncolorable(len(candidate), sp, st):
                    current = candidate
                    removed = True
                    break
        size = len(current)
        sizes[size] = sizes.get(size, 0) + 1
        if size < best_size:
            best_size = size
            best_subset = current

    return best_subset, best_size, sizes


# ============================================================
# Main experiments
# ============================================================

def analyze_angle(theta, name, do_completion=True, do_minimize=True,
                  min_trials=200, verbose=True):
    """Full analysis of one angle: raw alphabet, completion, minimization."""
    c, s = math.cos(theta), math.sin(theta)

    # Build alphabet {0, ±1, ±cosθ, ±sinθ}
    # Deduplicate values that are numerically equal
    raw_vals = [0, 1, -1, c, -c, s, -s]
    alphabet = []
    seen = set()
    for v in raw_vals:
        key = round(v, 10)
        if key not in seen:
            seen.add(key)
            alphabet.append(v)

    if verbose:
        print(f"\n{'='*60}")
        print(f"θ = {name} = {theta:.6f} rad = {math.degrees(theta):.2f}°")
        print(f"cos θ = {c:.6f}, sin θ = {s:.6f}")
        print(f"Alphabet ({len(alphabet)} values): " +
              ", ".join(f"{v:.4f}" for v in sorted(alphabet)))
        print(f"{'='*60}")

    # Generate rays
    rays, rays_set = generate_rays(alphabet)
    pairs = find_pairs(rays)
    triads = find_triads(rays, pairs)
    uncolorable = sat_uncolorable(len(rays), pairs, triads) if triads else False

    result = {
        'theta': theta, 'name': name,
        'cos': c, 'sin': s,
        'alphabet_size': len(alphabet),
        'raw_rays': len(rays), 'raw_pairs': len(pairs),
        'raw_triads': len(triads), 'raw_uncolorable': uncolorable,
        'comp_rays': None, 'comp_pairs': None,
        'comp_triads': None, 'comp_uncolorable': None,
        'min_size': None, 'min_sizes': None,
    }

    if verbose:
        status = "KS-UNCOLORABLE" if uncolorable else "colorable"
        print(f"  Raw: {len(rays)} rays, {len(pairs)} pairs, "
              f"{len(triads)} triads → {status}")

    # Cross-product completion
    if do_completion:
        comp_rays = cross_product_completion(rays)
        comp_pairs = find_pairs(comp_rays)
        comp_triads = find_triads(comp_rays, comp_pairs)
        comp_unc = sat_uncolorable(len(comp_rays), comp_pairs, comp_triads) \
            if comp_triads else False

        result['comp_rays'] = len(comp_rays)
        result['comp_pairs'] = len(comp_pairs)
        result['comp_triads'] = len(comp_triads)
        result['comp_uncolorable'] = comp_unc

        if verbose:
            status = "KS-UNCOLORABLE" if comp_unc else "colorable"
            print(f"  Completed: {len(comp_rays)} rays, {len(comp_pairs)} pairs, "
                  f"{len(comp_triads)} triads → {status}")

        # Minimize if uncolorable (raw or completed)
        if do_minimize and (uncolorable or comp_unc):
            if comp_unc:
                target_rays, target_pairs, target_triads = \
                    comp_rays, comp_pairs, comp_triads
                label = "completed"
            else:
                target_rays, target_pairs, target_triads = rays, pairs, triads
                label = "raw"

            if verbose:
                print(f"  Minimizing {label} set ({min_trials} trials)...", end="", flush=True)
            t0 = time.time()
            best_sub, best_size, size_dist = sat_minimize(
                target_rays, target_pairs, target_triads, n_trials=min_trials)
            elapsed = time.time() - t0
            result['min_size'] = best_size
            result['min_sizes'] = size_dist
            if verbose:
                print(f" done ({elapsed:.1f}s)")
                print(f"  Minimum KS subset: {best_size} vectors")
                print(f"  Size distribution: {dict(sorted(size_dist.items()))}")

    return result


def experiment_rational_multiples_of_pi():
    """Sweep θ = kπ/n for small n, covering common algebraic angles."""
    print("\n" + "#"*70)
    print("# EXPERIMENT 1: Rational multiples of π")
    print("# θ = kπ/n for n = 2..24, k = 1..n-1 (unique angles in (0, π/2))")
    print("#"*70)

    angles = {}  # angle -> name
    for n in range(2, 25):
        for k in range(1, n):
            theta = k * math.pi / n
            # Only consider angles in (0, π/2) — others give equivalent alphabets
            if theta > math.pi/2 + 1e-10:
                continue
            # Deduplicate
            key = round(theta, 10)
            if key not in angles:
                frac = Fraction(k, n)
                angles[key] = f"{frac.numerator}π/{frac.denominator}"

    # Sort by angle
    sorted_angles = sorted(angles.items())
    print(f"\nTesting {len(sorted_angles)} unique angles in (0, π/2]\n")

    results = []
    for theta, name in sorted_angles:
        r = analyze_angle(theta, name, do_completion=True,
                         do_minimize=True, min_trials=200, verbose=True)
        results.append(r)

    return results


def experiment_fine_sweep():
    """Fine sweep to find boundaries of uncolorable regions."""
    print("\n" + "#"*70)
    print("# EXPERIMENT 2: Fine sweep around promising angles")
    print("# Looking for boundaries of KS-uncolorable regions")
    print("#"*70)

    # First, identify which rational multiples of π are uncolorable
    # Then sweep finely around the boundaries

    # Coarse sweep: 1-degree increments from 1° to 89°
    coarse_results = []
    print("\nCoarse sweep (1° increments):\n")
    print(f"{'Angle':>8s}  {'Rays':>5s}  {'Pairs':>5s}  {'Triads':>6s}  "
          f"{'Raw':>5s}  {'CRays':>5s}  {'CTri':>5s}  {'Comp':>5s}")
    print("-" * 65)

    for deg in range(1, 90):
        theta = math.radians(deg)
        r = analyze_angle(theta, f"{deg}°", do_completion=True,
                         do_minimize=False, verbose=False)
        coarse_results.append(r)

        raw_ks = "YES" if r['raw_uncolorable'] else "no"
        comp_ks = "YES" if r['comp_uncolorable'] else "no"
        comp_rays = r['comp_rays'] if r['comp_rays'] else "-"
        comp_tri = r['comp_triads'] if r['comp_triads'] else "-"
        print(f"{deg:>6d}°  {r['raw_rays']:>5d}  {r['raw_pairs']:>5d}  "
              f"{r['raw_triads']:>6d}  {raw_ks:>5s}  {str(comp_rays):>5s}  "
              f"{str(comp_tri):>5s}  {comp_ks:>5s}")

    # Find boundaries: angles where uncolorability switches
    unc_angles = [r for r in coarse_results if r['raw_uncolorable'] or r['comp_uncolorable']]
    print(f"\nUncolorable angles found: {len(unc_angles)}")
    for r in unc_angles:
        src = "raw" if r['raw_uncolorable'] else "completed"
        print(f"  {r['name']:>6s}: {src}")

    return coarse_results


def experiment_special_values():
    """Test algebraically special angles beyond rational π multiples."""
    print("\n" + "#"*70)
    print("# EXPERIMENT 3: Algebraically special angles")
    print("# Angles where cos/sin take algebraic values")
    print("#"*70)

    specials = [
        # Angles where cos or sin is a known algebraic number
        ("arctan(√2)", math.atan(math.sqrt(2)),
         "cos=1/√3, sin=√(2/3)"),
        ("arctan(1/√2)", math.atan(1/math.sqrt(2)),
         "cos=√(2/3), sin=1/√3"),
        ("arctan(φ)", math.atan((1+math.sqrt(5))/2),
         "cos=2/(1+√5+...), sin related to φ"),
        ("arctan(1/φ)", math.atan(2/(1+math.sqrt(5))),
         "complementary golden angle"),
        ("arccos(1/3)", math.acos(1/3),
         "tetrahedral angle, cos=1/3"),
        ("arccos(1/√3)", math.acos(1/math.sqrt(3)),
         "space diagonal, cos=1/√3"),
        ("arctan(2)", math.atan(2),
         "cos=1/√5, sin=2/√5"),
        ("arctan(1/2)", math.atan(0.5),
         "cos=2/√5, sin=1/√5"),
        ("arccos(√2/2)", math.pi/4,
         "π/4, cos=sin=√2/2 (Peres connection)"),
        ("arccos(φ/2)", math.acos((1+math.sqrt(5))/4),
         "cos=φ/2, golden half"),
        ("arctan(√3-1)", math.atan(math.sqrt(3)-1),
         "mixed surd"),
        ("arccos(√(2/3))", math.acos(math.sqrt(2.0/3.0)),
         "cos²=2/3, magic angle complement"),
    ]

    results = []
    for name, theta, desc in specials:
        print(f"\n--- {name}: {desc} ---")
        r = analyze_angle(theta, name, do_completion=True,
                         do_minimize=True, min_trials=200, verbose=True)
        results.append(r)
    return results


def experiment_known_island_recovery():
    """Verify that the trigonometric family recovers known islands at special angles."""
    print("\n" + "#"*70)
    print("# EXPERIMENT 4: Known island recovery")
    print("# Check that special angles reproduce known island structures")
    print("#"*70)

    cases = [
        # Peres: cos²θ + sin²θ = 1 with cosθ = sinθ = 1/√2
        ("π/4 (Peres?)", math.pi/4,
         "cosθ=sinθ=√2/2, expect norm-2 cancellation → min 33"),

        # Integer-like: cosθ = 2/√5, sinθ = 1/√5 → cos²=4/5, sin²=1/5
        # Not quite 1+1=2 but let's see
        ("arctan(1/2)", math.atan(0.5),
         "cosθ=2/√5, sinθ=1/√5"),

        # arctan(1) = π/4 already covered
        # Try angles where alphabet has 2:1 ratio
        ("arccos(2/√5)", math.acos(2/math.sqrt(5)),
         "cosθ=2/√5 ≈ 0.894"),

        # Eisenstein-like: try θ = π/3 (cos=1/2, sin=√3/2)
        ("π/3 (Eisenstein?)", math.pi/3,
         "cosθ=1/2, sinθ=√3/2"),

        # π/6: cos=√3/2, sin=1/2
        ("π/6", math.pi/6,
         "cosθ=√3/2, sinθ=1/2"),
    ]

    results = []
    for name, theta, desc in cases:
        print(f"\n--- {name}: {desc} ---")
        r = analyze_angle(theta, name, do_completion=True,
                         do_minimize=True, min_trials=500, verbose=True)
        results.append(r)
    return results


# ============================================================
# Summary
# ============================================================

def print_summary(all_results):
    """Print summary table of all tested angles."""
    print("\n" + "="*80)
    print("SUMMARY TABLE")
    print("="*80)
    print(f"{'Angle':<20s} {'cos θ':>8s} {'sin θ':>8s} "
          f"{'Rays':>5s} {'Tri':>4s} {'Raw':>4s} "
          f"{'CRay':>5s} {'CTri':>5s} {'Comp':>4s} {'Min':>4s}")
    print("-"*80)

    for r in sorted(all_results, key=lambda x: x['theta']):
        raw = "YES" if r['raw_uncolorable'] else "-"
        comp = "YES" if r['comp_uncolorable'] else "-"
        cr = str(r['comp_rays']) if r['comp_rays'] is not None else "-"
        ct = str(r['comp_triads']) if r['comp_triads'] is not None else "-"
        mn = str(r['min_size']) if r['min_size'] is not None else "-"
        print(f"{r['name']:<20s} {r['cos']:>8.4f} {r['sin']:>8.4f} "
              f"{r['raw_rays']:>5d} {r['raw_triads']:>4d} {raw:>4s} "
              f"{cr:>5s} {ct:>5s} {comp:>4s} {mn:>4s}")

    # Highlight uncolorable
    unc = [r for r in all_results if r['raw_uncolorable'] or r['comp_uncolorable']]
    print(f"\nTotal angles tested: {len(all_results)}")
    print(f"KS-uncolorable (raw or completed): {len(unc)}")
    if unc:
        print("\nUncolorable angles:")
        for r in sorted(unc, key=lambda x: x['theta']):
            src = "raw" if r['raw_uncolorable'] else "completed only"
            mn = f", min={r['min_size']}" if r['min_size'] else ""
            print(f"  θ = {r['name']:<20s} ({src}{mn})")


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    t_start = time.time()

    all_results = []

    # Experiment 1: rational multiples of π
    r1 = experiment_rational_multiples_of_pi()
    all_results.extend(r1)

    # Experiment 2: coarse sweep to find boundaries
    r2 = experiment_fine_sweep()
    all_results.extend(r2)

    # Experiment 3: algebraically special angles
    r3 = experiment_special_values()
    all_results.extend(r3)

    # Experiment 4: known island recovery
    r4 = experiment_known_island_recovery()
    all_results.extend(r4)

    # Deduplicate by angle before summary
    seen_angles = {}
    unique_results = []
    for r in all_results:
        key = round(r['theta'], 8)
        if key not in seen_angles:
            seen_angles[key] = r
            unique_results.append(r)
        else:
            # Keep the one with more data (e.g. minimization done)
            if r['min_size'] is not None and seen_angles[key]['min_size'] is None:
                seen_angles[key] = r
                unique_results = [x for x in unique_results if round(x['theta'], 8) != key]
                unique_results.append(r)

    print_summary(unique_results)

    elapsed = time.time() - t_start
    print(f"\nTotal runtime: {elapsed:.1f}s")
