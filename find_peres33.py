"""Find the correct Peres 33-ray KS set by searching all vectors
with components from {0, +/-1, +/-sqrt(2)} in R^3.

Key: identify PROPORTIONAL vectors as the same ray."""

import math
from itertools import combinations

S2 = math.sqrt(2)
VALS = [0, 1, -1, S2, -S2]
EPS = 1e-10


def dot(u, v):
    return sum(a * b for a, b in zip(u, v))


def norm_sq(v):
    return dot(v, v)


def normalize(v):
    """Normalize to unit vector."""
    n = math.sqrt(norm_sq(v))
    return tuple(c / n for c in v)


def ray_key(v):
    """Canonical key for a ray: normalize, then pick sign so first nonzero > 0."""
    nv = normalize(v)
    for c in nv:
        if abs(c) > EPS:
            if c < 0:
                nv = tuple(-x for x in nv)
            break
    return tuple(round(x, 8) for x in nv)


def fmt(v):
    def c(x):
        if abs(x) < EPS: return "0"
        if abs(x - 1) < EPS: return "1"
        if abs(x + 1) < EPS: return "-1"
        if abs(x - S2) < EPS: return "s2"
        if abs(x + S2) < EPS: return "-s2"
        return f"{x:.3f}"
    return f"({c(v[0])},{c(v[1])},{c(v[2])})"


# Generate all distinct rays (identifying proportional vectors)
ray_dict = {}
for x in VALS:
    for y in VALS:
        for z in VALS:
            if abs(x) + abs(y) + abs(z) < EPS:
                continue
            v = (x, y, z)
            k = ray_key(v)
            if k not in ray_dict:
                ray_dict[k] = v  # store one representative

rays = list(ray_dict.values())
print(f"Total distinct rays: {len(rays)}")

# Classify by direction cosines squared (invariant of the ray)
def cosines_sq(v):
    ns = norm_sq(v)
    return tuple(sorted([round(c * c / ns, 6) for c in v]))

cos_classes = {}
for v in rays:
    cs = cosines_sq(v)
    cos_classes.setdefault(cs, []).append(v)

print("\nRays by direction cosines^2:")
for cs in sorted(cos_classes):
    vecs = cos_classes[cs]
    print(f"  {cs}: {len(vecs)} rays  e.g. {fmt(vecs[0])}")

# Build orthogonality graph
n = len(rays)
adj = [set() for _ in range(n)]
for i in range(n):
    for j in range(i + 1, n):
        if abs(dot(rays[i], rays[j])) < EPS:
            adj[i].add(j)
            adj[j].add(i)

# Find all triads
all_triads = []
for i in range(n):
    for j in adj[i]:
        if j <= i:
            continue
        for k in (adj[i] & adj[j]):
            if k <= j:
                continue
            all_triads.append((i, j, k))

print(f"\nTotal triads among all {n} rays: {len(all_triads)}")

# Triad type breakdown
print("\nTriads by direction-cosine types:")
triad_type_count = {}
for i, j, k in all_triads:
    types = tuple(sorted([cosines_sq(rays[idx]) for idx in (i, j, k)]))
    triad_type_count[types] = triad_type_count.get(types, 0) + 1

for tt in sorted(triad_type_count):
    print(f"  {tt}: {triad_type_count[tt]} triads")


# Now: try to find a 33-ray KS-uncolorable subset.
# The Peres set uses rays with cosines^2 patterns:
#   (0, 0, 1): 3 rays
#   (0, 0.5, 0.5): 6 rays
#   (0.25, 0.25, 0.5): 12 rays
# That's 21. Need 12 more.
# Candidates: (0, 0.333333, 0.666667) = 12 rays, or (0.2, 0.4, 0.4) = 12

# Strategy: test different 33-ray subsets for KS-uncolorability
def find_subset_triads(subset_indices):
    """Find all triads within a subset of rays."""
    s = set(subset_indices)
    triads = []
    for i, j, k in all_triads:
        if i in s and j in s and k in s:
            triads.append((i, j, k))
    return triads


def is_ks_uncolorable(subset_indices):
    """Check if a subset is KS-uncolorable by backtracking search."""
    triads = find_subset_triads(subset_indices)
    if not triads:
        return False, 0

    vecs = sorted(subset_indices)
    vec_to_triads_local = {v: [] for v in vecs}
    for t_idx, (a, b, c) in enumerate(triads):
        vec_to_triads_local[a].append(t_idx)
        vec_to_triads_local[b].append(t_idx)
        vec_to_triads_local[c].append(t_idx)

    color = {v: None for v in vecs}

    def propagate():
        changed = True
        while changed:
            changed = False
            for a, b, c in triads:
                triple = [a, b, c]
                greens = sum(1 for v in triple if color[v] == 1)
                reds = sum(1 for v in triple if color[v] == 0)
                unset = [v for v in triple if color[v] is None]
                if greens > 1:
                    return False
                if greens == 1:
                    for v in unset:
                        color[v] = 0
                        changed = True
                elif reds == 2 and len(unset) == 1:
                    color[unset[0]] = 1
                    changed = True
                elif reds == 3:
                    return False
        return True

    def backtrack():
        saved = dict(color)
        if not propagate():
            color.update(saved)
            return False
        unset = [v for v in vecs if color[v] is None]
        if not unset:
            return True  # valid coloring found
        v = unset[0]
        for c in (1, 0):
            snap = dict(color)
            color[v] = c
            if backtrack():
                return True
            color.update(snap)
        return False

    found = backtrack()
    return not found, len(triads)


# Test my original 33 = types (0,0,1) + (0,0.5,0.5) + (0,0.333333,0.666667) + (0.25,0.25,0.5)
print("\n" + "=" * 60)
print("TESTING CANDIDATE 33-RAY SUBSETS")
print("=" * 60)

# Identify ray indices by type
def rays_of_type(target_cs):
    return [i for i, v in enumerate(rays) if cosines_sq(v) == target_cs]

t_100 = rays_of_type((0, 0, 1.0))        # (1,0,0) type
t_110 = rays_of_type((0, 0.5, 0.5))      # (1,1,0) type
t_s210 = rays_of_type((0, 0.333333, 0.666667))  # (s2,1,0) type
t_11s2 = rays_of_type((0.25, 0.25, 0.5))  # (1,1,s2) type
t_111 = rays_of_type((0.333333, 0.333333, 0.333333))  # (1,1,1) type
t_s2s21 = rays_of_type((0.2, 0.4, 0.4))  # (s2,s2,1) type

print(f"\n(1,0,0) type: {len(t_100)} rays")
print(f"(1,1,0) type: {len(t_110)} rays")
print(f"(s2,1,0) type: {len(t_s210)} rays")
print(f"(1,1,s2) type: {len(t_11s2)} rays")
print(f"(1,1,1) type: {len(t_111)} rays")
print(f"(s2,s2,1) type: {len(t_s2s21)} rays")

# Original attempt: I+II+III+IV = 3+6+12+12 = 33
set_A = t_100 + t_110 + t_s210 + t_11s2
print(f"\nTest A: I+II+III+IV = {len(set_A)} rays")
uncolorable_A, triads_A = is_ks_uncolorable(set_A)
print(f"  Triads: {triads_A}, Uncolorable: {uncolorable_A}")

# Alternative: I+II+IV+V-bis = 3+6+12+4 = 25
set_B = t_100 + t_110 + t_11s2 + t_111
print(f"\nTest B: I+II+IV+V-bis = {len(set_B)} rays")
uncolorable_B, triads_B = is_ks_uncolorable(set_B)
print(f"  Triads: {triads_B}, Uncolorable: {uncolorable_B}")

# Try: I+II+III+IV+V-bis = 3+6+12+12+4 = 37
set_C = t_100 + t_110 + t_s210 + t_11s2 + t_111
print(f"\nTest C: I+II+III+IV+V-bis = {len(set_C)} rays")
uncolorable_C, triads_C = is_ks_uncolorable(set_C)
print(f"  Triads: {triads_C}, Uncolorable: {uncolorable_C}")

# Try: I+II+IV+V = 3+6+12+12 = 33
set_D = t_100 + t_110 + t_11s2 + t_s2s21
print(f"\nTest D: I+II+IV+V = {len(set_D)} rays")
uncolorable_D, triads_D = is_ks_uncolorable(set_D)
print(f"  Triads: {triads_D}, Uncolorable: {uncolorable_D}")

# Try: all 62 rays
print(f"\nTest E: ALL {len(rays)} rays")
uncolorable_E, triads_E = is_ks_uncolorable(list(range(len(rays))))
print(f"  Triads: {triads_E}, Uncolorable: {uncolorable_E}")

# Key test: I+II+IV+V-bis+extras from III to reach 33
# 3+6+12+4 = 25, need 8 more from Type III (12 available)
# Try all combinations of 8 from 12 Type III rays
if not uncolorable_B:
    print(f"\nTest F: I+II+IV+V-bis + subsets of Type III (25+k)...")
    # Just test with all 12 Type III
    set_F = t_100 + t_110 + t_11s2 + t_111 + t_s210
    print(f"  Full set: {len(set_F)} rays")
    uncolorable_F, triads_F = is_ks_uncolorable(set_F)
    print(f"  Triads: {triads_F}, Uncolorable: {uncolorable_F}")

# The real candidate: I+II+V-bis+IV with (1,1,1) type creating crucial cross-links
# Test: I+II+V-bis (3+6+4=13) alone
set_core = t_100 + t_110 + t_111
print(f"\nTest G: I+II+V-bis = {len(set_core)} rays")
uncolorable_G, triads_G = is_ks_uncolorable(set_core)
print(f"  Triads: {triads_G}, Uncolorable: {uncolorable_G}")

# Test with (s2,s2,0) type which creates (4,4,4) triads
t_s2s20 = rays_of_type((0, 0.5, 0.5))  # same as t_110, includes (s2,s2,0) ∝ (1,1,0)
# Actually (s2,s2,0) is the same ray as (1,1,0) since they're proportional.
# The norm^2=4 class (0.0, 0.5, 0.5) would be (0,s2,s2) type...

# Let me check: what are the norm^2=4 rays?
print("\n--- Type IV (norm^2=4) rays: ---")
for i, v in enumerate(rays):
    ns = round(norm_sq(v), 6)
    if ns == 4.0:
        print(f"  {i}: {fmt(v)}  cosines^2 = {cosines_sq(v)}")
