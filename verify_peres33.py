"""Verify all 16 orthogonal triads of the Peres 33-vector KS set in 3D."""

import math

S2 = math.sqrt(2)

# All 33 vectors indexed 1-33
vectors = {
    # Type I: Coordinate axes (norm^2 = 1)
    1:  (1, 0, 0),
    2:  (0, 1, 0),
    3:  (0, 0, 1),
    # Type II: Face diagonals (norm^2 = 2)
    4:  (1, 1, 0),
    5:  (1, -1, 0),
    6:  (1, 0, 1),
    7:  (1, 0, -1),
    8:  (0, 1, 1),
    9:  (0, 1, -1),
    # Type III: Mixed sqrt(2)-1-0 (norm^2 = 3)
    10: (S2, 1, 0),
    11: (S2, -1, 0),
    12: (1, S2, 0),
    13: (1, -S2, 0),
    14: (S2, 0, 1),
    15: (S2, 0, -1),
    16: (1, 0, S2),
    17: (1, 0, -S2),
    18: (0, S2, 1),
    19: (0, S2, -1),
    20: (0, 1, S2),
    21: (0, 1, -S2),
    # Type IV: sqrt(2)-1-1 (norm^2 = 4)
    22: (1, 1, S2),
    23: (1, -1, S2),
    24: (1, 1, -S2),
    25: (1, -1, -S2),
    26: (1, S2, 1),
    27: (1, S2, -1),
    28: (1, -S2, 1),
    29: (1, -S2, -1),
    30: (S2, 1, 1),
    31: (S2, 1, -1),
    32: (S2, -1, 1),
    33: (S2, -1, -1),
}

triads = [
    ("T1",  1, 2, 3),
    ("T2",  1, 8, 9),
    ("T3",  2, 6, 7),
    ("T4",  3, 4, 5),
    ("T5",  1, 18, 21),
    ("T6",  1, 19, 20),
    ("T7",  2, 14, 17),
    ("T8",  2, 15, 16),
    ("T9",  3, 10, 13),
    ("T10", 3, 11, 12),
    ("T11", 4, 23, 25),
    ("T12", 5, 22, 24),
    ("T13", 6, 27, 29),
    ("T14", 7, 26, 28),
    ("T15", 8, 31, 32),
    ("T16", 9, 30, 33),
]


def dot(u, v):
    return sum(a * b for a, b in zip(u, v))


def norm_sq(v):
    return dot(v, v)


def fmt_vec(v):
    def c(x):
        if abs(x) < 1e-12:
            return "0"
        if abs(abs(x) - 1) < 1e-12:
            return "1" if x > 0 else "-1"
        if abs(abs(x) - S2) < 1e-12:
            return "s2" if x > 0 else "-s2"
        return f"{x:.4f}"
    return f"({c(v[0])}, {c(v[1])}, {c(v[2])})"


# Verify vector count
print(f"Total vectors: {len(vectors)}")
assert len(vectors) == 33, f"Expected 33 vectors, got {len(vectors)}"

# Verify norms
print("\n--- Norm² check ---")
for i, v in sorted(vectors.items()):
    ns = norm_sq(v)
    print(f"  v{i:2d} = {fmt_vec(v):>22s}  norm^2 = {ns:.6f}")

# Verify all 16 triads
print("\n--- Triad orthogonality check ---")
all_ok = True
for label, i, j, k in triads:
    vi, vj, vk = vectors[i], vectors[j], vectors[k]
    d_ij = dot(vi, vj)
    d_ik = dot(vi, vk)
    d_jk = dot(vj, vk)
    ok = all(abs(d) < 1e-12 for d in [d_ij, d_ik, d_jk])
    status = "OK" if ok else "FAIL"
    if not ok:
        all_ok = False
    print(f"  {label:>3s}: {{v{i}, v{j}, v{k}}} = "
          f"{{{fmt_vec(vi)}, {fmt_vec(vj)}, {fmt_vec(vk)}}}")
    print(f"        dots: ({d_ij:.6f}, {d_ik:.6f}, {d_jk:.6f})  [{status}]")

# Check that every vector appears in at least one triad
print("\n--- Vector participation ---")
participation = {i: 0 for i in vectors}
for _, i, j, k in triads:
    participation[i] += 1
    participation[j] += 1
    participation[k] += 1

for i in sorted(participation):
    print(f"  v{i:2d}: {participation[i]} triad(s)")

total_slots = sum(participation.values())
print(f"\nTotal triad slots: {total_slots} (expected 48 = 16 × 3)")
assert total_slots == 48

unused = [i for i, c in participation.items() if c == 0]
if unused:
    print(f"WARNING: vectors not in any triad: {unused}")
else:
    print("All 33 vectors participate in at least one triad.")

# Final verdict
print("\n" + "=" * 50)
if all_ok:
    print("ALL 16 TRIADS VERIFIED ORTHOGONAL")
else:
    print("SOME TRIADS FAILED - CHECK ABOVE")
print("=" * 50)


# ============================================================
# Part 1b: Find ALL orthogonal triads (not just the 16 listed)
# ============================================================
print("\n\n" + "=" * 50)
print("EXHAUSTIVE TRIAD SEARCH")
print("=" * 50)

all_triads_found = []
vec_ids = sorted(vectors.keys())
for idx_a in range(len(vec_ids)):
    for idx_b in range(idx_a + 1, len(vec_ids)):
        a, b = vec_ids[idx_a], vec_ids[idx_b]
        if abs(dot(vectors[a], vectors[b])) > 1e-10:
            continue
        for idx_c in range(idx_b + 1, len(vec_ids)):
            c = vec_ids[idx_c]
            if (abs(dot(vectors[a], vectors[c])) < 1e-10 and
                    abs(dot(vectors[b], vectors[c])) < 1e-10):
                all_triads_found.append((a, b, c))

print(f"\nFound {len(all_triads_found)} orthogonal triads among 33 vectors:")
for i, (a, b, c) in enumerate(all_triads_found):
    # Check if this matches one of our listed 16
    listed = set((i, j, k) for _, i, j, k in triads)
    tag = " <-- LISTED" if (a, b, c) in listed else " *** NEW ***"
    print(f"  {i+1:2d}. {{v{a}, v{b}, v{c}}} = "
          f"{{{fmt_vec(vectors[a])}, {fmt_vec(vectors[b])}, {fmt_vec(vectors[c])}}}{tag}")

if len(all_triads_found) == 16:
    print("\nConfirmed: exactly 16 triads among the 33 vectors.")
    print("The KS contradiction arises from 72 orthogonal PAIRS, not just triads.")
elif len(all_triads_found) > 16:
    print(f"\nFound {len(all_triads_found) - 16} additional triads beyond the 16 listed!")

# Use ALL found triads for the KS check
all_triad_tuples = all_triads_found

# ============================================================
# Part 1c: Find ALL orthogonal pairs
# ============================================================
print("\n--- All orthogonal pairs ---")
ortho_pairs = []
for idx_a in range(len(vec_ids)):
    for idx_b in range(idx_a + 1, len(vec_ids)):
        a, b = vec_ids[idx_a], vec_ids[idx_b]
        if abs(dot(vectors[a], vectors[b])) < 1e-10:
            ortho_pairs.append((a, b))

print(f"Total orthogonal pairs among 33 vectors: {len(ortho_pairs)}")

# Build adjacency map: for each vector, which vectors are orthogonal to it?
ortho_neighbors = {v: [] for v in vectors}
for a, b in ortho_pairs:
    ortho_neighbors[a].append(b)
    ortho_neighbors[b].append(a)

for v in sorted(vectors):
    nbrs = sorted(ortho_neighbors[v])
    print(f"  v{v:2d} orthogonal to {len(nbrs)} vectors: {nbrs}")

# ============================================================
# Part 2: Verify the KS coloring contradiction
# ============================================================
# The KS theorem states: there is NO assignment of colors
# (green=1, red=0) to the 33 rays such that:
#   1) Every triad has exactly 1 green and 2 red
#   2) No two orthogonal rays are both green
#      (because any orthogonal pair extends to a basis)
#
# We prove this by exhaustive backtracking search.
# ============================================================

print("\n")
print("=" * 50)
print("KS COLORING CONTRADICTION VERIFICATION")
print("=" * 50)
print("\nSearching for a valid {green, red} coloring where:")
print("  (1) each triad has exactly 1 green and 2 red rays")
print("  (2) no two orthogonal rays are both green\n")

# Build adjacency: which triads does each vector appear in?
triad_tuples = all_triad_tuples  # Use ALL triads found exhaustively
vec_to_triads = {v: [] for v in vectors}
for t_idx, (a, b, c) in enumerate(triad_tuples):
    vec_to_triads[a].append(t_idx)
    vec_to_triads[b].append(t_idx)
    vec_to_triads[c].append(t_idx)


def solve_ks():
    """Backtracking search for a valid KS coloring.

    color[v] = 1 (green) or 0 (red), None if unassigned.
    Constraints:
      1) Each triad has exactly one green.
      2) No two orthogonal vectors are both green.

    Returns (found, color_dict, search_stats).
    """
    color = {v: None for v in vectors}
    stats = {"branches": 0, "deadends": 0}

    def propagate():
        """Force-assign vectors where constraints demand it.

        Returns False if a contradiction is found.
        """
        changed = True
        while changed:
            changed = False

            # Pair constraint: if v is green, all orthogonal neighbors must be red
            for v in vectors:
                if color[v] == 1:
                    for u in ortho_neighbors[v]:
                        if color[u] == 1:
                            return False  # two orthogonal greens
                        if color[u] is None:
                            color[u] = 0
                            changed = True

            # Triad constraint
            for a, b, c in triad_tuples:
                triple = [a, b, c]
                greens = sum(1 for v in triple if color[v] == 1)
                reds = sum(1 for v in triple if color[v] == 0)
                unset = [v for v in triple if color[v] is None]

                if greens > 1:
                    return False
                if reds == 3:
                    return False
                if greens == 1:
                    for v in unset:
                        color[v] = 0
                        changed = True
                elif reds == 2 and len(unset) == 1:
                    color[unset[0]] = 1
                    changed = True
        return True

    def backtrack():
        stats["branches"] += 1
        saved = dict(color)

        if not propagate():
            color.update(saved)
            stats["deadends"] += 1
            return False

        unassigned = [v for v in sorted(vectors) if color[v] is None]
        if not unassigned:
            return True  # valid coloring found

        v = unassigned[0]
        for c in (1, 0):
            snapshot = dict(color)
            color[v] = c
            if backtrack():
                return True
            color.update(snapshot)

        stats["deadends"] += 1
        return False

    found = backtrack()
    return found, color, stats


found, coloring, stats = solve_ks()

print(f"  Branches explored: {stats['branches']}")
print(f"  Dead ends hit:     {stats['deadends']}")

if found:
    print("\n  UNEXPECTED: Found a valid coloring!")
    greens = [v for v in sorted(coloring) if coloring[v] == 1]
    print(f"  Green rays: {greens}")
    # Verify the coloring
    print("  Verifying...")
    for a, b in ortho_pairs:
        if coloring[a] == 1 and coloring[b] == 1:
            print(f"    BUG: v{a} and v{b} both green and orthogonal!")
    for a, b, c in triad_tuples:
        g = sum(coloring[v] for v in (a, b, c))
        if g != 1:
            print(f"    BUG: triad {{v{a},v{b},v{c}}} has {g} greens!")
else:
    print("\n  No valid coloring exists.")
    print("  --> KS CONTRADICTION CONFIRMED")

# ============================================================
# Part 3: Constructive proof of KS contradiction
# ============================================================
# Full case-split proof: start with symmetry choices, propagate,
# then branch on remaining free vectors until every branch
# reaches a contradiction.
# ============================================================

print("\n")
print("=" * 50)
print("CONSTRUCTIVE PROOF OF KS CONTRADICTION")
print("=" * 50)
print()


def proof_assign(color, v, c, reason, indent):
    """Assign a color and print the step."""
    label = "GREEN" if c == 1 else "RED"
    color[v] = c
    pad = "  " * indent
    print(f"{pad}v{v:2d} {fmt_vec(vectors[v]):>22s} = {label:5s}  ({reason})")


def proof_propagate(color, indent):
    """Propagate forced assignments. Returns False on contradiction."""
    changed = True
    while changed:
        changed = False

        # Pair constraint: green -> all orthogonal neighbors red
        for v in vectors:
            if color[v] == 1:
                for u in ortho_neighbors[v]:
                    if color[u] == 1:
                        return False  # two orthogonal greens
                    if color[u] is None:
                        proof_assign(color, u, 0,
                                     f"orthogonal to v{v} (green)", indent)
                        changed = True

        # Triad constraint
        for t_idx, (a, b, c) in enumerate(triad_tuples):
            triple = [a, b, c]
            greens = sum(1 for v in triple if color[v] == 1)
            reds = sum(1 for v in triple if color[v] == 0)
            unset = [v for v in triple if color[v] is None]
            tname = f"T{t_idx+1}"

            if greens > 1:
                return False
            if reds == 3:
                return False
            if greens == 1:
                for v in unset:
                    proof_assign(color, v, 0,
                                 f"{tname}: green already chosen", indent)
                    changed = True
            elif reds == 2 and len(unset) == 1:
                proof_assign(color, unset[0], 1,
                             f"{tname}: only option left", indent)
                changed = True
    return True


def find_contradiction(color):
    """Return a string describing the contradiction, or None."""
    for t_idx, (a, b, c) in enumerate(triad_tuples):
        colors = [color[v] for v in (a, b, c)]
        if None in colors:
            continue
        greens = sum(colors)
        if greens != 1:
            tname = f"T{t_idx+1}"
            labels = ["G" if x == 1 else "R" for x in colors]
            if greens == 0:
                return (f"{tname} {{v{a},v{b},v{c}}} = all RED "
                        f"(need exactly 1 green)")
            else:
                return (f"{tname} {{v{a},v{b},v{c}}} = {greens} greens "
                        f"(need exactly 1)")
    for a, b in ortho_pairs:
        if color[a] == 1 and color[b] == 1:
            return f"v{a} and v{b} both GREEN but orthogonal"
    return None


def proof_branch(color, indent, branch_label):
    """Recursively prove contradiction on all branches.

    Returns True if contradiction reached on all paths (proof complete).
    """
    pad = "  " * indent

    # Propagate
    ok = proof_propagate(color, indent)

    # Check for contradiction after propagation
    contra = find_contradiction(color)
    if contra or not ok:
        if contra:
            print(f"{pad}** CONTRADICTION: {contra}")
        else:
            print(f"{pad}** CONTRADICTION (propagation conflict)")
        return True

    # Find unassigned vectors
    unassigned = [v for v in sorted(vectors) if color[v] is None]
    if not unassigned:
        # All assigned, no contradiction - should not happen for KS set
        print(f"{pad}** ALL ASSIGNED - no contradiction (NOT a KS set!)")
        return False

    # Pick the vector to branch on: prefer one with most constraints
    # (most orthogonal neighbors already assigned) for shorter proof
    def branch_priority(v):
        assigned_nbrs = sum(1 for u in ortho_neighbors[v]
                            if color[u] is not None)
        triad_pressure = sum(1 for t_idx, (a, b, c) in enumerate(triad_tuples)
                             if v in (a, b, c) and
                             sum(1 for u in (a, b, c)
                                 if color[u] is not None) >= 1)
        return -(assigned_nbrs + triad_pressure)

    branch_v = min(unassigned, key=branch_priority)

    print(f"{pad}")
    print(f"{pad}Case split on v{branch_v} {fmt_vec(vectors[branch_v])}:")

    all_contra = True
    for c_val in (1, 0):
        c_label = "GREEN" if c_val == 1 else "RED"
        print(f"{pad}  --- Case: v{branch_v} = {c_label} ---")
        snapshot = dict(color)
        proof_assign(color, branch_v, c_val,
                     f"case assumption", indent + 1)
        if not proof_branch(color, indent + 1, f"v{branch_v}={c_label}"):
            all_contra = False
        color.update(snapshot)

    if all_contra:
        print(f"{pad}  Both cases lead to contradiction.")
    return all_contra


# === Begin proof ===

color = {v: None for v in vectors}

print("STEP 1: By cubic symmetry, assume v3 = (0,0,1) is GREEN.")
print("  (The proof for other axis choices follows by permutation.)")
print()
proof_assign(color, 3, 1, "assumption (WLOG by symmetry)", 0)
print()

print("Propagate:")
proof_propagate(color, 0)
print()

print("STEP 2: T3 = {v2(R), v6, v7} forces one of v6, v7 green.")
print("  By z -> -z symmetry, assume v6 = (1,0,1) is GREEN.")
print("  (The v7 case is equivalent by reflection.)")
print()
proof_assign(color, 6, 1, "assumption (WLOG by z-reflection)", 0)
print()

print("Propagate:")
proof_propagate(color, 0)
print()

print("STEP 3: T2 = {v1(R), v8, v9} forces one of v8, v9 green.")
print("  By y -> -y symmetry, assume v8 = (0,1,1) is GREEN.")
print("  (The v9 case is equivalent by reflection.)")
print()
proof_assign(color, 8, 1, "assumption (WLOG by y-reflection)", 0)
print()

print("Propagate:")
proof_propagate(color, 0)
print()

# Status check
assigned = sum(1 for v in vectors if color[v] is not None)
unassigned = [v for v in sorted(vectors) if color[v] is None]
print(f"After symmetry choices and propagation: "
      f"{assigned}/33 assigned, {len(unassigned)} free.")
print(f"Free vectors: {unassigned}")
print()

print("STEP 4: Case splits on remaining free vectors.")
print("  Each branch must reach a contradiction.\n")

result = proof_branch(color, 0, "root")

print()
print("=" * 50)
if result:
    print("ALL BRANCHES REACH CONTRADICTION.")
    print("No valid KS coloring exists for ANY assignment")
    print("consistent with v3=G, v6=G, v8=G.")
    print()
    print("By cubic symmetry (Step 1) and reflection symmetry")
    print("(Steps 2-3), this covers ALL possible colorings.")
    print()
    print("==> KOCHEN-SPECKER THEOREM PROVED.")
else:
    print("PROOF INCOMPLETE - some branch did not contradict.")
print("=" * 50)
