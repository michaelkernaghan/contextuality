"""v10: Cabello-Severini-Winter quantities, each with a stated standard of proof.

For the orthogonality graph G of a named ray set (unweighted sum of all rays):

  alpha     independence number.  EXACT: MaxSAT (RC2) optimum.
  attained  largest eigenvalue of the sum of the rank-one projectors of the
            set's OWN rays in C^3: the value quantum theory reaches with these
            rays.  Numeric (double precision) from exact coordinates.
  theta     Lovasz number: the maximum over ALL orthonormal representations, in
            any dimension.  Numeric: primal and dual SDP values are both printed;
            their gap is the evidence.  attained <= theta always.
  alpha*    fractional packing number with clique (edge and triad) constraints.
            EXACT when status is "certified": a rational primal and a rational
            dual solution of equal value, both checked in Fraction arithmetic.

v9 printed theta as "the quantum bound" of each island and compared it with
alpha.  The comparison that concerns the island's rays is attained vs alpha.

Usage:  python ks_csw_exact.py [key ...]     (keys: set keys and <alphabet>-raw pools)
Writes: results/csw_v10.jsonl
"""
import cmath
import json
import math
import sys
import time
from fractions import Fraction
from pathlib import Path

import cvxpy as cp
import numpy as np
from pysat.examples.rc2 import RC2
from pysat.formula import WCNF
from scipy.optimize import linprog

import ks_bpqs_exact as B
import ks_recertify_v10 as R

HERE = Path(__file__).resolve().parent
ROOT = {"integer": math.sqrt(5), "golden": math.sqrt(5), "peres": math.sqrt(2),
        "sqrtm2": 1j * math.sqrt(2), "eisenstein": cmath.exp(2j * math.pi / 3),
        "heegner7": 1j * math.sqrt(7), "cubic": 2 ** (1 / 3),
        "supergolden": 1.4655712318767680, "supergolden2": 1.4655712318767680}
POOLS = ["integer-raw", "peres-raw", "sqrtm2-raw", "eisenstein-raw", "heegner7-raw",
         "supergolden2-raw"]


def load(key):
    if key in B.SETS:
        rays, orth, bases = B.load_set(key)
        akey = R.POOLS[B.SETS[key]][0]
        pairs = sorted(tuple(sorted(p)) for p in orth)
        return rays, pairs, bases, akey
    akey, comp, _ = R.POOLS[key]
    F, alpha, _ = R.ALPHABETS[akey]
    rays = R.build(alpha, F, complete=comp, cap=3000)
    pairs, triads, _ = R.structure(rays)
    return rays, pairs, [tuple(t) for t in triads], akey


def independence_number(n, pairs):
    w = WCNF()
    for i, j in pairs:
        w.append([-(i + 1), -(j + 1)])
    for i in range(n):
        w.append([i + 1], weight=1)
    with RC2(w) as rc2:
        model = rc2.compute()
    return sum(1 for i in range(n) if model[i] > 0)


def attained(rays, akey):
    t = ROOT[akey]
    S = np.zeros((3, 3), dtype=complex)
    for v in rays:
        z = np.array([sum(float(c) * t ** k for k, c in enumerate(x.c)) for x in v], dtype=complex)
        S += np.outer(z, z.conj()) / np.vdot(z, z).real
    return [float(x) for x in np.linalg.eigvalsh(S)]


def theta(n, pairs):
    X = cp.Variable((n, n), symmetric=True)
    cons = [X >> 0, cp.trace(X) == 1] + [X[i, j] == 0 for i, j in pairs]
    primal = cp.Problem(cp.Maximize(cp.sum(X)), cons).solve(solver=cp.CLARABEL)
    # dual: min t  s.t.  t I + sum_{edges} y_ij (E_ij + E_ji) - J  is PSD
    t = cp.Variable()
    y = cp.Variable(len(pairs))
    rows = [i for i, j in pairs] + [j for i, j in pairs]
    cols = [j for i, j in pairs] + [i for i, j in pairs]
    import scipy.sparse as sp
    M = sp.coo_matrix((np.ones(2 * len(pairs)), (np.array(rows) * n + np.array(cols),
                                                 list(range(len(pairs))) * 2)),
                      shape=(n * n, len(pairs))).tocsc()
    Y = cp.reshape(M @ y, (n, n), order="C")
    dual = cp.Problem(cp.Minimize(t), [t * np.eye(n) + Y - np.ones((n, n)) >> 0]).solve(
        solver=cp.CLARABEL)
    return float(primal), float(dual)


def fractional_packing(n, pairs, triads):
    in_triad = {frozenset(p) for t in triads for p in ((t[0], t[1]), (t[0], t[2]), (t[1], t[2]))}
    cliques = [tuple(t) for t in triads] + [p for p in pairs if frozenset(p) not in in_triad]
    A = np.zeros((len(cliques), n))
    for r, c in enumerate(cliques):
        A[r, list(c)] = 1
    pr = linprog(-np.ones(n), A_ub=A, b_ub=np.ones(len(cliques)), bounds=(0, None), method="highs")
    du = linprog(np.ones(len(cliques)), A_ub=-A.T, b_ub=-np.ones(n), bounds=(0, None), method="highs")
    for den in (12, 60, 840, 10 ** 6):
        w = [Fraction(float(x)).limit_denominator(den) for x in pr.x]
        y = [Fraction(float(x)).limit_denominator(den) for x in du.x]
        ok_p = all(x >= 0 for x in w) and all(sum(w[v] for v in c) <= 1 for c in cliques)
        cover = [Fraction(0)] * n
        for yc, c in zip(y, cliques):
            for v in c:
                cover[v] += yc
        ok_d = all(x >= 0 for x in y) and all(c >= 1 for c in cover)
        if ok_p and ok_d and sum(w) == sum(y):
            return str(sum(w)), float(sum(w)), "certified"
    return None, float(-pr.fun), "numeric only (primal %.9f, dual %.9f)" % (-pr.fun, du.fun)


def main():
    keys = sys.argv[1:] or (list(B.SETS) + POOLS)
    out = HERE / "results" / "csw_v10.jsonl"
    failed = []
    for key in keys:
        t0 = time.time()
        try:
            rays, pairs, triads, akey = load(key)
            n = len(rays)
            a = independence_number(n, pairs)
            eig = attained(rays, akey)
            th_p, th_d = theta(n, pairs)
            fp_exact, fp, fp_status = fractional_packing(n, pairs, triads)
        except Exception as exc:
            failed.append(key)
            print("%-18s ERROR %r" % (key, exc), flush=True)
            continue
        rec = {"object": key, "rays": n, "pairs": len(pairs), "triads": len(triads),
               "alpha": a, "attained": round(eig[-1], 9), "projector_sum_eigenvalues": eig,
               "theta_primal": round(th_p, 6), "theta_dual": round(th_d, 6),
               "alpha_star": fp_exact or round(fp, 9), "alpha_star_status": fp_status,
               "attained_exceeds_alpha": eig[-1] > a + 1e-9,
               "seconds": round(time.time() - t0, 1), "date": time.strftime("%Y-%m-%d %H:%M")}
        print("%-18s n=%3d alpha=%3d attained=%.6f theta=[%.5f, %.5f] alpha*=%s (%s)"
              % (key, n, a, eig[-1], th_p, th_d, rec["alpha_star"], fp_status), flush=True)
        with out.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec) + "\n")
    print("failed: %s" % (failed or "none"))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
