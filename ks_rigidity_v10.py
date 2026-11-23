"""v10: infinitesimal rigidity in C^3 of the named KS sets (numerical ranks).

Unknowns: n unit vectors in C^3 (6n real numbers).  Equations: |v_i|^2 = 1 and
Re, Im <v_i|v_j> = 0 for every orthogonal pair.  Symmetries: U(3) acting on all
vectors and a phase on each vector, sharing the overall phase: n + 8 real
dimensions.  The set is infinitesimally rigid when the null space of the
Jacobian has dimension exactly n + 8; the excess is the number of infinitesimal
flexes.  Ranks are numerical (SVD, double precision); the smallest retained and
largest discarded singular values are printed so the gap can be judged.

Infinitesimal rigidity implies local rigidity.  It is neither necessary nor
sufficient for uniqueness of the realisation up to unitary equivalence.

The repo's older ks_rigidity.py treats the real sets in R^3 and so does not
produce the C^3 table printed in v9; this script does.

Usage:  python ks_rigidity_v10.py
Writes: results/rigidity_v10.jsonl
"""
import cmath
import json
import math
import time
from pathlib import Path

import numpy as np

import ks_bpqs_exact as B
import ks_csw_exact as C
import ks_modulus2_circle as M
import ks_recertify_v10 as R

HERE = Path(__file__).resolve().parent


def numeric(rays, akey):
    t = C.ROOT[akey]
    return [np.array([sum(float(c) * t ** k for k, c in enumerate(x.c)) for x in v], dtype=complex)
            for v in rays]


def flexes(vecs, pairs):
    n = len(vecs)
    vecs = [v / np.linalg.norm(v) for v in vecs]
    J = np.zeros((n + 2 * len(pairs), 6 * n))
    for i, v in enumerate(vecs):
        J[i, 6 * i:6 * i + 3] = 2 * v.real
        J[i, 6 * i + 3:6 * i + 6] = 2 * v.imag
    for r, (i, j) in enumerate(pairs):
        a, b = vecs[i], vecs[j]
        for row, part in ((n + 2 * r, np.real), (n + 2 * r + 1, np.imag)):
            J[row, 6 * i:6 * i + 3] = part(b)
            J[row, 6 * i + 3:6 * i + 6] = part(-1j * b)
            J[row, 6 * j:6 * j + 3] = part(a.conj())
            J[row, 6 * j + 3:6 * j + 6] = part(1j * a.conj())
    s = np.linalg.svd(J, compute_uv=False)
    rank = int((s > 1e-9 * s[0]).sum())
    null = 6 * n - rank
    kept = float(s[rank - 1])
    dropped = float(s[rank]) if rank < len(s) else 0.0
    return null, null - (n + 8), kept, dropped


def circle_set(theta):
    words = M.generic_rays()
    adj = M.build(words)
    import random
    rng = random.Random(7)
    cur, order = list(range(len(words))), list(range(len(words)))
    rng.shuffle(order)
    for r in order:
        trial = [c for c in cur if c != r]
        if M.uncolorable(trial, adj):
            cur = trial
    x = math.sqrt(2) * cmath.exp(1j * theta)
    val = {"0": 0, "1": 1, "-1": -1, "x": x, "-x": -x, "x*": x.conjugate(), "-x*": -x.conjugate()}
    vecs = [np.array([val[c] for c in words[i]], dtype=complex) for i in cur]
    pairs = [(a, b) for a in range(len(vecs)) for b in range(a + 1, len(vecs))
             if abs(np.vdot(vecs[a], vecs[b])) < 1e-9]
    return vecs, pairs


def main():
    out = HERE / "results" / "rigidity_v10.jsonl"
    jobs = []
    for key in B.SETS:
        try:
            rays, orth, bases = B.load_set(key)
        except Exception:
            continue
        akey = R.POOLS[B.SETS[key]][0]
        jobs.append((key, numeric(rays, akey), sorted(tuple(sorted(p)) for p in orth)))
    for name, th in (("circle-45 at theta=1.0", 1.0), ("circle-45 at theta=0.3", 0.3),
                     ("circle-45 at x=(1+sqrt-7)/2", math.atan(math.sqrt(7)))):
        v, p = circle_set(th)
        jobs.append((name, v, p))
    for key, vecs, pairs in jobs:
        null, extra, kept, dropped = flexes(vecs, pairs)
        rec = {"set": key, "rays": len(vecs), "pairs": len(pairs), "null": null,
               "symmetry": len(vecs) + 8, "flexes": extra, "smallest_kept_sv": kept,
               "largest_dropped_sv": dropped, "date": time.strftime("%Y-%m-%d %H:%M")}
        print("%-30s n=%2d pairs=%3d null=%2d n+8=%2d flexes=%d  (sv gap %.2e / %.2e)"
              % (key, len(vecs), len(pairs), null, len(vecs) + 8, extra, kept, dropped), flush=True)
        with out.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")


if __name__ == "__main__":
    main()
