"""Exact checks of the statements made in the Prolegomena of version 12 (paper/v12_s0_prolegomena.tex).

Integer arithmetic only.  Run:  python ks_v12_prolegomena_checks.py
Exits non-zero if any check fails.
"""
from itertools import product
from math import gcd


def canon(v: tuple[int, ...]) -> tuple[int, ...]:
    """One representative per ray: divide by the gcd, make the first nonzero entry positive."""
    g = gcd(*v)
    v = tuple(c // g for c in v)
    first = next(c for c in v if c != 0)
    return v if first > 0 else tuple(-c for c in v)


def dot(v: tuple[int, ...], w: tuple[int, ...]) -> int:
    return sum(a * b for a, b in zip(v, w))


def cross(v: tuple[int, ...], w: tuple[int, ...]) -> tuple[int, ...]:
    return (v[1] * w[2] - v[2] * w[1], v[2] * w[0] - v[0] * w[2], v[0] * w[1] - v[1] * w[0])


def grid(values: list[int]) -> set[tuple[int, ...]]:
    return {canon(v) for v in product(values, repeat=3) if any(v)}


def main() -> int:
    ok = True

    def check(name: str, cond: bool) -> None:
        nonlocal ok
        print(("PASS  " if cond else "FAIL  ") + name)
        ok = ok and cond

    g1 = grid([0, 1, -1])
    g2 = grid([0, 1, -1, 2, -2])
    check("grid of 0,+-1 has 13 rays", len(g1) == 13)
    check("grid of 0,+-1,+-2 has 49 rays", len(g2) == 49)

    # Section 1.3: the completed-grid example.
    v, w, t = (1, 1, 2), (2, 0, -1), (1, -5, 2)
    check("(1,1,2) and (2,0,-1) are coordinate triples",
          all(c in (0, 1, -1, 2, -2) for c in v + w) and any(v) and any(w))
    check("(1,1,2) and (2,0,-1) are orthogonal", dot(v, w) == 0)
    check("third ray of their triad is (1,-5,2)", canon(cross(v, w)) == canon(t))
    check("(1,-5,2) is orthogonal to both", dot(t, v) == 0 and dot(t, w) == 0)
    check("no coordinate triple names the ray (1,-5,2)", canon(t) not in g2)

    # Completed grid of 0,+-1,+-2: closure under third rays.  The paper states 109 rays.
    closed = set(g2)
    while True:
        rays = sorted(closed)
        new = {canon(cross(a, b)) for i, a in enumerate(rays) for b in rays[i + 1:] if dot(a, b) == 0}
        if new <= closed:
            break
        closed |= new
    check("completed grid of 0,+-1,+-2 has 109 rays (paper, Computed fact on the integer grid)",
          len(closed) == 109)

    # Prolegomena, The grid: every ray leaves the cube where the lines cross.
    def at_crossing(ray: tuple[int, ...], values: list[int]) -> bool:
        """Does the ray meet the cube of half-width max|values| at a crossing of the face lines,
        that is, at a point with all coordinates among the values?  Scale so the largest |coordinate| equals the half-width."""
        top = max(abs(c) for c in values)
        m = max(abs(c) for c in ray)
        return all((c * top) % m == 0 and (c * top) // m in values for c in ray)

    check("all 49 rays of 0,+-1,+-2 leave the cube where the lines cross",
          all(at_crossing(r, [0, 1, -1, 2, -2]) for r in g2))

    # Prolegomena, three coordinate values: the crossings of the face lines are 109 of the 145 rays.
    vals3 = [0, 1, -1, 2, -2, 3, -3]
    g3 = grid(vals3)
    check("grid of 0,+-1,+-2,+-3 has 145 rays", len(g3) == 145)
    carried = sum(at_crossing(r, vals3) for r in g3)
    check("the crossings of the face lines are 109 of those 145 rays", carried == 109)
    check("(1,2,0) is in that grid and leaves the cube away from the crossings",
          canon((1, 2, 0)) in g3 and not at_crossing((1, 2, 0), vals3))

    # Prolegomena: a grid lacking minus signs is a subset of the symmetric one.
    check("grid of 0,1,2 is a subset of the grid of 0,+-1,+-2", grid([0, 1, 2]) <= g2)

    # Prolegomena, The question: the two inner products, as polynomials in x, evaluated at integer x.
    for x in range(-6, 7):
        if dot((x, 1, 1), (x, -1, -1)) != x * x - 2 or dot((1, -1, 1), (x, 1, -1)) != x - 2:
            check(f"inner products at x={x}", False)
            break
    else:
        check("(x,1,1).(x,-1,-1) = x^2-2 and (1,-1,1).(x,1,-1) = x-2 for x = -6..6", True)

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
