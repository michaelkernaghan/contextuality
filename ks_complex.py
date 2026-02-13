"""
KS Set Search — Complex / Eisenstein Extension
================================================
Extends the real-valued KS search to complex vector spaces using
Hermitian inner products. Generates rays from Eisenstein integers
Z[omega] where omega = e^(2*pi*i/3) is a primitive cube root of unity.

The cancellation engine here is (1 + omega + omega^2 = 0) rather than
the real-valued (2 - 1 - 1 = 0) used by Peres with sqrt(2).

Strategy:
1. Generate all rays from Eisenstein integers with bounded coefficients
2. Filter by squared norm |v|^2 <= cutoff
3. Canonicalize (remove duplicates up to complex scaling)
4. Build orthogonality graph using Hermitian inner product
5. Enumerate triads (3-cliques of mutual orthogonality)
6. Test colorability, then minimize

Uses the same solver logic as ks_search.py:
- Green forces all orthogonal rays red
- Two reds in a triad force third green
- Contradiction if 3 reds or 2+ greens in a triad
- Contradiction if two orthogonal rays both green
"""

import cmath
import itertools
import math
import random
import time


# ============================================================
# Eisenstein arithmetic
# ============================================================

# omega = e^(2*pi*i/3) = -1/2 + i*sqrt(3)/2
OMEGA = cmath.exp(2j * cmath.pi / 3)
OMEGA2 = OMEGA * OMEGA  # omega^2 = -1 - omega = -1/2 - i*sqrt(3)/2

# The six units of Z[omega]: {1, -1, omega, -omega, omega^2, -omega^2}
UNITS = [1, -1, OMEGA, -OMEGA, OMEGA2, -OMEGA2]


def eisenstein(a, b):
    """Return the Eisenstein integer a + b*omega."""
    return a + b * OMEGA


def eisenstein_norm(z):
    """
    Norm of an Eisenstein integer a + b*omega.
    N(a + b*omega) = a^2 - ab + b^2 (always a non-negative integer).
    For our purposes we use |z|^2 = z * conj(z).
    """
    return (z * z.conjugate()).real


def vec_squared_norm(v):
    """Squared norm |v|^2 = sum |v_k|^2."""
    return sum(eisenstein_norm(x) for x in v)


# ============================================================
# Hermitian inner product and orthogonality
# ============================================================

def hermitian_dot(v1, v2):
    """Hermitian inner product: <v1, v2> = sum conj(v1_k) * v2_k."""
    return sum(x.conjugate() * y for x, y in zip(v1, v2))


def build_orthogonality_matrix(vectors):
    """Build orthogonality matrix using Hermitian inner product."""
    n = len(vectors)
    P = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            dot = hermitian_dot(vectors[i], vectors[j])
            if abs(dot) < 1e-9:
                P[i][j] = 1
                P[j][i] = 1
    return P


# ============================================================
# Solver (same logic as ks_search.py, fixed version)
# ============================================================

def find_triads(P, n):
    triads = []
    for i in range(n):
        for j in range(i + 1, n):
            if P[i][j] != 1:
                continue
            for k in range(j + 1, n):
                if P[i][k] == 1 and P[j][k] == 1:
                    triads.append((i, j, k))
    return triads


def propagate(C, P, triads, n):
    changed = True
    while changed:
        changed = False
        # Green forces orthogonal rays red; detect two-green contradictions
        for i in range(n):
            if C[i] == 1:
                for j in range(i + 1, n):
                    if P[i][j] == 1:
                        if C[j] == 1:
                            return False  # two orthogonal greens
                        if C[j] == -1:
                            C[j] = 0
                            changed = True
        # Triad constraints
        for triad in triads:
            vals = [C[triad[0]], C[triad[1]], C[triad[2]]]
            if vals.count(0) >= 3:
                return False
            if vals.count(1) >= 2:
                return False
            if vals.count(0) == 2 and vals.count(-1) == 1:
                for idx in triad:
                    if C[idx] == -1:
                        C[idx] = 1
                        changed = True
                        break
    return True


def solve(C, P, triads, n, triad_map=None):
    """
    Recursive backtracking with most-constrained-first heuristic.
    triad_map[i] = list of triads containing ray i (for heuristic).
    """
    if not propagate(C, P, triads, n):
        return False

    # Find uncolored ray with most constraints (triads + orthogonal pairs)
    pick = -1
    best_score = -1
    for i in range(n):
        if C[i] == -1:
            if triad_map is not None:
                score = len(triad_map.get(i, []))
            else:
                score = sum(1 for j in range(n) if P[i][j] == 1)
            if score > best_score:
                best_score = score
                pick = i

    if pick == -1:
        for triad in triads:
            if sum(1 for idx in triad if C[idx] == 1) != 1:
                return False
        return True

    saved = C[:]
    C[pick] = 1
    if solve(C, P, triads, n, triad_map):
        return True
    for i in range(n):
        C[i] = saved[i]
    C[pick] = 0
    if solve(C, P, triads, n, triad_map):
        return True
    for i in range(n):
        C[i] = saved[i]
    return False


def is_colorable(vectors):
    n = len(vectors)
    if n == 0:
        return True
    P = build_orthogonality_matrix(vectors)
    triads = find_triads(P, n)
    if len(triads) == 0:
        return True
    # Build triad map for most-constrained-first heuristic
    triad_map = {}
    for t in triads:
        for idx in t:
            triad_map.setdefault(idx, []).append(t)
    C = [-1] * n
    return solve(C, P, triads, n, triad_map)


# ============================================================
# Ray generation from Eisenstein integers
# ============================================================

def canonicalize_complex_ray(v):
    """
    Canonicalize a complex ray: divide by first nonzero component
    so it becomes 1. This identifies v ~ lambda*v for any nonzero lambda.
    Returns a tuple of complex numbers rounded for hashing, or None if zero.
    """
    # Skip zero vector
    if all(abs(x) < 1e-10 for x in v):
        return None

    # Find first nonzero component and divide by it
    for x in v:
        if abs(x) > 1e-10:
            v = tuple(c / x for c in v)
            break

    # Round real and imaginary parts for hashing
    def rnd(z):
        return complex(round(z.real, 8), round(z.imag, 8))

    return tuple(rnd(x) for x in v)


def generate_eisenstein_rays(max_coeff, dim=3, norm_cutoff=None):
    """
    Generate all distinct rays in C^dim with Eisenstein integer components.
    Each component is a + b*omega with |a|, |b| <= max_coeff.
    Optionally filter by |v|^2 <= norm_cutoff.
    """
    # Build the component alphabet: all a + b*omega
    coeffs = range(-max_coeff, max_coeff + 1)
    alphabet = []
    for a in coeffs:
        for b in coeffs:
            alphabet.append(eisenstein(a, b))

    rays_set = set()
    rays_list = []

    for combo in itertools.product(alphabet, repeat=dim):
        # Norm filter
        if norm_cutoff is not None:
            sn = sum(eisenstein_norm(x) for x in combo)
            if sn > norm_cutoff + 1e-9:
                continue

        canon = canonicalize_complex_ray(list(combo))
        if canon is not None and canon not in rays_set:
            rays_set.add(canon)
            rays_list.append(tuple(complex(x) for x in combo))

    return rays_list


def generate_root_of_unity_rays(n_root, dim=3):
    """
    Generate all distinct rays using 0 and n-th roots of unity.
    E.g., n_root=6 gives {0, zeta^0, ..., zeta^5} with zeta = e^(i*pi/3).
    """
    zeta = cmath.exp(2j * cmath.pi / n_root)
    alphabet = [0] + [zeta**k for k in range(n_root)]

    rays_set = set()
    rays_list = []

    for combo in itertools.product(alphabet, repeat=dim):
        canon = canonicalize_complex_ray(list(combo))
        if canon is not None and canon not in rays_set:
            rays_set.add(canon)
            rays_list.append(combo)

    return rays_list


# ============================================================
# Analysis and minimization
# ============================================================

def analyze_ray_set(vectors):
    n = len(vectors)
    P = build_orthogonality_matrix(vectors)
    triads = find_triads(P, n)
    pairs = sum(sum(row) for row in P) // 2
    return {
        'n': n,
        'pairs': pairs,
        'triads': len(triads),
        'triad_list': triads,
        'P': P,
    }


def minimize_randomized(vectors):
    """Randomized greedy minimization."""
    current = list(vectors)
    removed = True
    while removed:
        removed = False
        indices = list(range(len(current)))
        random.shuffle(indices)
        for i in indices:
            candidate = current[:i] + current[i + 1:]
            if not is_colorable(candidate):
                current = candidate
                removed = True
                break
    return current


def multi_trial_minimize(vectors, num_trials=100, verbose=True):
    """Run many randomized minimization trials."""
    best = None
    best_size = len(vectors)
    sizes_found = {}

    if verbose:
        print(f"  Running {num_trials} randomized minimization trials...")
        print(f"  Starting pool: {len(vectors)} vectors")

    for trial in range(num_trials):
        minimal = minimize_randomized(vectors)
        size = len(minimal)
        sizes_found[size] = sizes_found.get(size, 0) + 1

        if size < best_size:
            best = minimal
            best_size = size
            if verbose:
                print(f"    Trial {trial + 1}: NEW RECORD! {size} vectors")
        elif verbose and trial < 5:
            print(f"    Trial {trial + 1}: {size} vectors")

    if verbose:
        print(f"\n  Size distribution across {num_trials} trials:")
        for size in sorted(sizes_found.keys()):
            count = sizes_found[size]
            print(f"    {size} vectors: {count} times "
                  f"({100 * count / num_trials:.0f}%)")

    return best, best_size, sizes_found


def format_eisenstein(z):
    """Format a complex number as an Eisenstein integer a + b*omega."""
    # Try to decompose z = a + b*omega
    # omega = -1/2 + i*sqrt(3)/2
    # So: z = a + b*(-1/2 + i*sqrt(3)/2) = (a - b/2) + i*(b*sqrt(3)/2)
    # From imag part: b = 2*imag(z) / sqrt(3)
    # From real part: a = real(z) + b/2
    s3_2 = math.sqrt(3) / 2
    b_raw = z.imag / s3_2
    b = round(b_raw)
    a = round(z.real + b / 2)

    # Verify
    reconstructed = eisenstein(a, b)
    if abs(z - reconstructed) > 1e-6:
        # Not a clean Eisenstein integer, show as complex
        return f"({z.real:.3f}+{z.imag:.3f}i)"

    if b == 0:
        return str(a)
    elif a == 0:
        if b == 1:
            return "w"
        elif b == -1:
            return "-w"
        else:
            return f"{b}w"
    else:
        if b == 1:
            return f"{a}+w"
        elif b == -1:
            return f"{a}-w"
        elif b > 0:
            return f"{a}+{b}w"
        else:
            return f"{a}{b}w"


def print_complex_ray(idx, v):
    """Pretty-print a complex ray using Eisenstein notation."""
    parts = [format_eisenstein(x) for x in v]
    print(f"    {idx:3d}: ({', '.join(parts)})")


# ============================================================
# Search pipelines
# ============================================================

def search_eisenstein(max_coeff, norm_cutoff, num_trials=200):
    """Full search pipeline for Eisenstein integer rays."""
    label = (f"Eisenstein +/-{max_coeff}, "
             f"|v|^2 <= {norm_cutoff}")
    print(f"\n{'=' * 60}")
    print(f"Search: {label}")
    print(f"{'=' * 60}")

    t0 = time.time()
    rays = generate_eisenstein_rays(max_coeff, dim=3,
                                   norm_cutoff=norm_cutoff)
    t1 = time.time()
    print(f"  Generated {len(rays)} distinct rays ({t1 - t0:.1f}s)")

    if len(rays) > 2000:
        print(f"  Too many rays for direct solver. "
              f"Try lower norm_cutoff.")
        return None

    info = analyze_ray_set(rays)
    print(f"  Orthogonal pairs: {info['pairs']}")
    print(f"  Orthogonal triads: {info['triads']}")

    if info['triads'] == 0:
        print(f"  No triads — cannot produce KS set.")
        return None

    t2 = time.time()
    colorable = is_colorable(rays)
    t3 = time.time()

    if colorable:
        print(f"  Full set is COLORABLE — no KS set here.")
        print(f"  (tested in {t3 - t2:.2f}s)")
        return None
    else:
        print(f"  Full set is UNCOLORABLE! (tested in {t3 - t2:.2f}s)")

    t4 = time.time()
    best, best_size, sizes = multi_trial_minimize(
        rays, num_trials=num_trials)
    t5 = time.time()

    info2 = analyze_ray_set(best)
    print(f"\n  BEST RESULT: {info2['n']}-vector KS set")
    print(f"    Pairs: {info2['pairs']}, Triads: {info2['triads']}")
    print(f"    Search took {t5 - t4:.1f}s")
    print(f"    Vectors (Eisenstein notation, w = omega):")
    for i, v in enumerate(best):
        print_complex_ray(i + 1, v)

    return best


def search_roots_of_unity(n_root, num_trials=200):
    """Full search pipeline for n-th roots of unity."""
    label = f"{n_root}-th roots of unity"
    print(f"\n{'=' * 60}")
    print(f"Search: {label}")
    print(f"  zeta = e^(2*pi*i/{n_root})")
    print(f"{'=' * 60}")

    t0 = time.time()
    rays = generate_root_of_unity_rays(n_root, dim=3)
    t1 = time.time()
    print(f"  Generated {len(rays)} distinct rays ({t1 - t0:.1f}s)")

    info = analyze_ray_set(rays)
    print(f"  Orthogonal pairs: {info['pairs']}")
    print(f"  Orthogonal triads: {info['triads']}")

    if info['triads'] == 0:
        print(f"  No triads — cannot produce KS set.")
        return None

    t2 = time.time()
    colorable = is_colorable(rays)
    t3 = time.time()

    if colorable:
        print(f"  Full set is COLORABLE — no KS set here.")
        print(f"  (tested in {t3 - t2:.2f}s)")
        return None
    else:
        print(f"  Full set is UNCOLORABLE! (tested in {t3 - t2:.2f}s)")

    t4 = time.time()
    best, best_size, sizes = multi_trial_minimize(
        rays, num_trials=num_trials)
    t5 = time.time()

    info2 = analyze_ray_set(best)
    print(f"\n  BEST RESULT: {info2['n']}-vector KS set")
    print(f"    Pairs: {info2['pairs']}, Triads: {info2['triads']}")
    print(f"    Search took {t5 - t4:.1f}s")
    print(f"    Vectors:")
    for i, v in enumerate(best):
        print_complex_ray(i + 1, v)

    return best


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print("KS Set Search — Complex / Eisenstein Extension")
    print("Using Hermitian inner product for orthogonality")
    print("Solver: triads + propagation + backtracking (fixed)")
    print()

    # Phase 1: Roots of unity (quick survey)
    print("=" * 60)
    print("PHASE 1: Roots of Unity Survey")
    print("=" * 60)
    for n in [3, 4, 6]:
        search_roots_of_unity(n, num_trials=100)

    # Phase 2: Eisenstein integers with increasing norm cutoffs
    print("\n\n" + "=" * 60)
    print("PHASE 2: Eisenstein Integer Search")
    print("=" * 60)

    # Eisenstein +/-1, various norm cutoffs
    for nc in [3, 4, 6]:
        search_eisenstein(1, nc, num_trials=100)

    # Eisenstein +/-2, various norm cutoffs
    for nc in [4, 6, 8]:
        search_eisenstein(2, nc, num_trials=100)
