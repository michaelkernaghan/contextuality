"""Checked mathematics for the companion note idea/cube_idea.tex.

Everything the note states as a fact about rays is produced or asserted here, in
exact integer arithmetic (an inner product of two words over {0, +-1, +-x} is a
polynomial c0 + c1 x + c2 x^2 with integer coefficients; it is tested for zero at
x = sqrt 2, 2 and sqrt 3 without floating point).

  check_identities   the inner products quoted in Section 4
  check_ladder       13 rays over {0,+-1}, colourable; 49 over {0,+-1,+-x}; 145 with a third letter
  check_peres        the 33 rays of Peres: 72 pairs, 16 triads, cannot be marked,
                     and can be marked after deleting any one ray
  build / check_tree the table of forced choices of Section 5, replayed by an
                     independent checker; a tampered table must be rejected

Writes idea/idea_data.json and idea/forcing_table.tex.
Run:  python ks_idea_forcing.py        (exit status 0 means every check passed)
"""
import copy
import itertools
import json
import sys
from pathlib import Path

import make_alphabet_cube_figures as mc

X = mc.X
OUT = Path(__file__).resolve().parent / "idea"

# ---- exact arithmetic --------------------------------------------------------


def W(*letters):
    """Word from entries 0, 1, -1, 'x', '-x' (not made canonical)."""
    table = {0: (0, 0), 1: (1, 1), -1: (-1, 1), "x": (1, X), "-x": (-1, X)}
    return tuple(table[c] for c in letters)


def dot_poly(v, w):
    """Inner product of two real words as integer coefficients (c0, c1, c2) of 1, x, x^2."""
    c = [0, 0, 0]
    for (sa, ka), (sb, kb) in zip(v, w):
        if sa and sb:
            c[(ka == X) + (kb == X)] += sa * sb
    return tuple(c)


def vanishes(poly, where):
    c0, c1, c2 = poly
    if where == "sqrt2":
        return c0 + 2 * c2 == 0 and c1 == 0
    if where == "2":
        return c0 + 2 * c1 + 4 * c2 == 0
    if where == "sqrt3":
        return c0 + 3 * c2 == 0 and c1 == 0
    raise ValueError(where)


def structure(rays, where):
    n = len(rays)
    orth = [[vanishes(dot_poly(rays[i], rays[j]), where) for j in range(n)] for i in range(n)]
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n) if orth[i][j]]
    triads = [(i, j, k) for (i, j) in pairs for k in range(j + 1, n) if orth[i][k] and orth[j][k]]
    return pairs, triads


# ---- marking -----------------------------------------------------------------
# A marking gives each ray 1 (marked) or 0 (unmarked): two orthogonal rays are
# never both marked, and every triad has exactly one marked ray.


class System:
    def __init__(self, n, pairs, triads):
        self.n, self.pairs, self.triads = n, pairs, triads
        self.adj = [set() for _ in range(n)]
        for i, j in pairs:
            self.adj[i].add(j)
            self.adj[j].add(i)

    def mark(self, val, r):
        """Mark r; every ray orthogonal to r becomes unmarked. Returns the newly unmarked."""
        assert r not in val and all(val.get(m) != 1 for m in self.adj[r])
        val[r] = 1
        new = sorted(m for m in self.adj[r] if m not in val)
        for m in new:
            val[m] = 0
        return new

    def propagate(self, val, steps=None):
        """Apply 'two unmarked rays of a triad force the third' until nothing changes.
        Returns a triad whose three rays are all unmarked, or None."""
        while True:
            for t in self.triads:
                zeros = [r for r in t if val.get(r) == 0]
                if len(zeros) == 3:
                    return t
                if len(zeros) == 2:
                    (r,) = [r for r in t if val.get(r) != 0]
                    if r not in val:
                        new = self.mark(val, r)
                        if steps is not None:
                            steps.append({"ray": r, "how": "triad", "triad": list(t), "unmarks": new})
                        break
            else:
                return None

    def open_triads(self, val):
        return [t for t in self.triads if all(val.get(r) != 1 for r in t)]

    def solve(self, val=None):
        """A marking extending val, or None."""
        val = dict(val or {})
        if self.propagate(val):
            return None
        todo = self.open_triads(val)
        if not todo:
            return {r: val.get(r, 0) for r in range(self.n)}
        for r in todo[0]:
            if r not in val:
                v2 = dict(val)
                self.mark(v2, r)
                res = self.solve(v2)
                if res:
                    return res
        return None


def colourable(rays, where):
    pairs, triads = structure(rays, where)
    res = System(len(rays), pairs, triads).solve()
    if res is not None:                                   # check the marking found, directly
        assert all(not (res[i] and res[j]) for i, j in pairs)
        assert all(sum(res[r] for r in t) == 1 for t in triads)
    return res is not None


# ---- symmetries --------------------------------------------------------------


def signed_perms(rays):
    """The signed permutations of the coordinates that map the ray list to itself,
    as {name: index permutation}."""
    index = {w: i for i, w in enumerate(rays)}
    out = {}
    for perm in itertools.permutations(range(3)):
        for signs in itertools.product((1, -1), repeat=3):
            img = []
            for w in rays:
                v = mc.canon(tuple((signs[k] * w[perm[k]][0], w[perm[k]][1]) for k in range(3)))
                if v not in index:
                    break
                img.append(index[v])
            else:
                name = "(a,b,c) -> (" + ",".join(
                    ("-" if signs[k] < 0 else "") + "abc"[perm[k]] for k in range(3)) + ")"
                out[name] = img
    return out


# ---- the table of forced choices ----------------------------------------------


def build(system, val, perms, memo):
    """Smallest case tree found that shows val cannot be completed. Returns (node, cost)."""
    key = frozenset(val.items())
    if key in memo:
        return copy.deepcopy(memo[key])
    val = dict(val)
    steps = []
    dead = system.propagate(val, steps)
    if dead:
        res = ({"steps": steps, "dead": list(dead)}, len(steps) + 1)
        memo[key] = res
        return copy.deepcopy(res)
    marked = {r for r, v in val.items() if v == 1}
    unmarked = {r for r, v in val.items() if v == 0}
    stab = {name: g for name, g in perms.items()
            if {g[r] for r in marked} == marked and {g[r] for r in unmarked} == unmarked}
    best = None
    for t in system.open_triads(val):
        children, cost, real = [], 0, []
        for r in t:
            if r in val:
                continue
            image = next(((r0, name) for r0 in real for name, g in sorted(stab.items())
                          if g[r0] == r), None)
            if image:
                children.append({"choice": r, "image_of": image[0], "perm": image[1]})
                cost += 1
                continue
            v2 = dict(val)
            new = system.mark(v2, r)
            sub, c = build(system, v2, perms, memo)
            sub["steps"].insert(0, {"ray": r, "how": "choice", "unmarks": new})
            children.append({"choice": r, **sub})
            real.append(r)
            cost += c + 1
        if best is None or cost < best[1]:
            best = ({"steps": steps, "branch": {"triad": list(t), "children": children}},
                    len(steps) + cost)
    assert best is not None, "state can be completed: the set is colourable"
    memo[key] = best
    return copy.deepcopy(best)


def check_tree(rays, where, tree, perms):
    """Independent replay. Uses only the ray list: orthogonality is recomputed here."""
    n = len(rays)

    def orth(i, j):
        return i != j and vanishes(dot_poly(rays[i], rays[j]), where)

    def is_triad(t):
        return len(set(t)) == 3 and all(orth(a, b) for a, b in itertools.combinations(t, 2))

    index = {w: i for i, w in enumerate(rays)}
    for name, g in perms.items():                          # every symmetry used is a symmetry
        dst = name.split(" -> ")[1].strip("()").split(",")  # re-derive it from its printed formula
        spec = [(-1 if d.startswith("-") else 1, "abc".index(d[-1])) for d in dst]
        derived = [index.get(mc.canon(tuple((s * w[p][0], w[p][1]) for s, p in spec))) for w in rays]
        assert derived == list(g), "printed formula %s is not the permutation used" % name
        assert sorted(g) == list(range(n)), name
        assert all(orth(i, j) == orth(g[i], g[j]) for i in range(n) for j in range(i)), name

    leaves = 0

    def walk(node, val, expect_choice):
        nonlocal leaves
        val = dict(val)
        for k, st in enumerate(node["steps"]):
            r = st["ray"]
            assert r not in val, "ray decided twice"
            if st["how"] == "choice":
                assert k == 0 and r == expect_choice, "unexpected choice"
            else:
                t = st["triad"]
                assert is_triad(t) and r in t, "not a triad"
                assert all(val.get(m) == 0 for m in t if m != r), "triad does not force this ray"
            nb = [m for m in range(n) if orth(r, m)]
            assert all(val.get(m) != 1 for m in nb), "marked ray orthogonal to a marked ray"
            val[r] = 1
            new = sorted(m for m in nb if m not in val)
            assert new == sorted(st["unmarks"]), "wrong list of unmarked rays"
            for m in new:
                val[m] = 0
        if expect_choice is not None:
            assert node["steps"] and node["steps"][0]["how"] == "choice"
        if "dead" in node:
            assert is_triad(node["dead"]) and all(val.get(m) == 0 for m in node["dead"]), \
                "claimed contradiction is not one"
            leaves += 1
            return
        t = node["branch"]["triad"]
        kids = node["branch"]["children"]
        assert is_triad(t) and all(val.get(m) != 1 for m in t), "bad branching triad"
        assert sorted(c["choice"] for c in kids) == sorted(m for m in t if m not in val), \
            "cases do not cover the triad"
        marked = {r for r, v in val.items() if v == 1}
        unmarked = {r for r, v in val.items() if v == 0}
        real = {c["choice"] for c in kids if "image_of" not in c}
        for c in kids:
            if "image_of" in c:
                g = perms[c["perm"]]
                assert c["image_of"] in real and g[c["image_of"]] == c["choice"], "bad image"
                assert {g[r] for r in marked} == marked and {g[r] for r in unmarked} == unmarked, \
                    "symmetry does not preserve the choices already made"
            else:
                walk(c, val, c["choice"])

    walk(tree, {}, None)
    return leaves


# ---- output ------------------------------------------------------------------


def tex_word(w):
    def letter(s, k):
        body = "0" if s == 0 else ("x" if k == X else "1")
        return "\\bar %s" % body if s < 0 else body
    return "(" + ",".join(letter(s, k) for s, k in w) + ")"


def plain_word(w):
    return [("0" if s == 0 else ("-" if s < 0 else "") + ("x" if k == X else "1")) for s, k in w]


def tex_perm(name):
    src, dst = name.split(" -> ")
    dst = dst.strip("()").split(",")
    return "$(a,b,c)\\mapsto(" + ",".join(("\\bar " + d[1:]) if d.startswith("-") else d for d in dst) + ")$"


def render(rays, tree):
    """LaTeX rows for the table, and the plain list of rows for the JSON file."""
    rows, plain = [], []
    counter = [0]

    def words(idx):
        return ", ".join("$%s$" % tex_word(rays[i]) for i in idx) if idx else "none"

    def walk(node, label):
        for st in node["steps"]:
            counter[0] += 1
            r = st["ray"]
            if st["how"] == "choice":
                why = "chosen (case %s)" % label
            else:
                others = [m for m in st["triad"] if m != r]
                why = "its triad partners %s are uncolored" % words(others).replace(", ", " and ")
            rows.append("%d & $%s$ & %s & %s \\\\" % (counter[0], tex_word(rays[r]), why, words(st["unmarks"])))
            plain.append({"row": counter[0], "case": label, "ray": r, "how": st["how"],
                          "unmarks": st["unmarks"]})
        if "dead" in node:
            rows.append("\\multicolumn{4}{@{}p{\\linewidth}@{}}{\\emph{Contradiction%s:} the triad %s has no "
                        "ray left to color.} \\\\ \\addlinespace"
                        % (" in case " + label if label else "", words(node["dead"])))
            return
        t, kids = node["branch"]["triad"], node["branch"]["children"]
        names = {}
        for n, c in enumerate(kids):
            names[c["choice"]] = (label + "." if label else "") + str(n + 1)
        rows.append("\\multicolumn{4}{@{}p{\\linewidth}@{}}{\\emph{Cases%s.} One ray of the triad %s must be "
                    "colored: %s.} \\\\ \\addlinespace"
                    % (" within " + label if label else "", words(t),
                       "; ".join("case %s is $%s$" % (names[c["choice"]], tex_word(rays[c["choice"]]))
                                 for c in kids)))
        for c in kids:
            if "image_of" in c:
                rows.append("\\multicolumn{4}{@{}p{\\linewidth}@{}}{\\emph{Case %s} is case %s with the "
                            "coordinates rearranged by %s, a symmetry of the 33 rays that leaves every "
                            "earlier choice in place.} \\\\ \\addlinespace"
                            % (names[c["choice"]], names[c["image_of"]], tex_perm(c["perm"])))
            else:
                walk(c, names[c["choice"]])

    walk(tree, "")
    return rows, plain


def first_real_path(tree):
    """Steps of the first fully written case, from the top of the table down to its contradiction."""
    node, steps = tree, []
    while True:
        steps += node["steps"]
        if "dead" in node:
            return steps, node["dead"]
        node = next(c for c in node["branch"]["children"] if "image_of" not in c)


# ---- checks ------------------------------------------------------------------


def check_identities():
    a = dot_poly(W("x", 1, 1), W("x", -1, -1))             # x^2 - 2
    b = dot_poly(W(1, -1, 1), W("x", 1, -1))               # x - 2
    c = dot_poly(W(1, 1, "x"), W(1, 1, -1))                # 2 - x
    assert a == (-2, 0, 1) and b == (-2, 1, 0) and c == (2, -1, 0), (a, b, c)
    assert vanishes(a, "sqrt2") and not vanishes(a, "2") and not vanishes(a, "sqrt3")
    assert vanishes(b, "2") and not vanishes(b, "sqrt2") and not vanishes(b, "sqrt3")
    assert vanishes(c, "2") and not vanishes(c, "sqrt2") and not vanishes(c, "sqrt3")


def check_ladder():
    pool = sorted(mc.POOL, key=str)
    bottom = [w for w in pool if all(k != X for s, k in w)]
    assert len(bottom) == 13 and len(pool) == 49
    for where in ("sqrt2", "2", "sqrt3"):                  # no letter x occurs: same answer for every x
        assert colourable(bottom, where)
    assert colourable(pool, "sqrt3") and not colourable(pool, "sqrt2") and not colourable(pool, "2")
    # three letters 1, x, y at generic values: words over seven letters, up to scale
    letters = [(0, 0)] + [(s, k) for k in (1, "x", "y") for s in (1, -1)]
    seen = set()
    for w in itertools.product(letters, repeat=3):
        if not any(s for s, k in w):
            continue
        if len({k for s, k in w if s}) == 1:
            w = tuple((s, 1 if s else 0) for s, k in w)
        lead = next(s for s, k in w if s)
        seen.add(tuple((s * lead, k) for s, k in w))
    assert len(seen) == 145, len(seen)
    return len(bottom), len(pool), len(seen)


def check_peres():
    rays = sorted(mc.PERES33, key=str)
    pairs, triads = structure(rays, "sqrt2")
    assert (len(rays), len(pairs), len(triads)) == (33, 72, 16), (len(rays), len(pairs), len(triads))
    # the note's description: the 49 words less those like (1,1,1) and those like (1,x,x)
    left_out = [w for w in mc.POOL if all(s for s, k in w)
                and sum(1 for s, k in w if k == X) in (0, 2)]
    assert len(left_out) == 16 and set(rays) == set(mc.POOL) - set(left_out)
    # independent cross-check of the exact orthogonality test, in floating point
    r2 = 2 ** 0.5
    num = [[s * (r2 if k == X else 1.0) for s, k in w] for w in rays]
    exact = set(pairs)
    for i in range(33):
        for j in range(i + 1, 33):
            d = sum(a * b for a, b in zip(num[i], num[j]))
            assert (abs(d) < 1e-9) == ((i, j) in exact), (i, j, d)
            assert abs(d) < 1e-9 or abs(d) > 1e-3
    assert not colourable(rays, "sqrt2")
    for i in range(33):
        assert colourable(rays[:i] + rays[i + 1:], "sqrt2"), "ray %d is not needed" % i
    return rays, pairs, triads


def check_rejects_tampered(rays, tree, perms):
    """Negative controls: the checker must refuse a damaged table and a damaged ray list."""
    refused = 0
    bad = copy.deepcopy(tree)
    node = bad
    while "dead" not in node:
        node = next(c for c in node["branch"]["children"] if "image_of" not in c)
    node["steps"][-1]["unmarks"] = node["steps"][-1]["unmarks"][:-1] or [0]
    for candidate_rays, candidate in ((rays, bad), (rays[:-1] + [W(1, 1, 1)], tree)):
        try:
            check_tree(candidate_rays, "sqrt2", candidate, perms)
        except AssertionError:
            refused += 1
    assert refused == 2, "checker accepted a damaged table"


def main():
    check_identities()
    counts = check_ladder()
    rays, pairs, triads = check_peres()
    perms = signed_perms(rays)
    assert len(perms) == 48, len(perms)
    system = System(len(rays), pairs, triads)
    tree, cost = build(system, {}, perms, {})
    leaves = check_tree(rays, "sqrt2", tree, perms)
    check_rejects_tampered(rays, tree, perms)
    rows, plain = render(rays, tree)
    path_steps, dead = first_real_path(tree)

    OUT.mkdir(exist_ok=True)
    (OUT / "forcing_table.tex").write_text(
        "% generated by ks_idea_forcing.py -- do not edit\n" + "\n".join(rows) + "\n", encoding="utf-8")
    (OUT / "idea_data.json").write_text(json.dumps({
        "rays": [plain_word(w) for w in rays], "pairs": pairs, "triads": triads,
        "ladder_counts": counts, "first_case": {"steps": path_steps, "dead": dead},
        "rows": plain, "tree": tree}, indent=1), encoding="utf-8")
    n_marked = sum(1 for r in plain)
    print("identities ok; ladder %d / %d / %d rays" % counts)
    print("33 rays, 72 pairs, 16 triads, cannot be colored; every 32-ray subset can")
    print("table: %d colored-ray rows, %d written cases, replayed and negative controls refused"
          % (n_marked, leaves))
    return 0


if __name__ == "__main__":
    sys.exit(main())
