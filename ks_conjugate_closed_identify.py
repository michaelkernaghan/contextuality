"""Identify the minimum sets found by ks_conjugate_closed_theorem.py with the named KS sets.

For every uncolourable case with a stored witness, rebuild the pool at that point, take the
subgraph on the witness words, check again that it is uncolourable, and test it for
isomorphism (VF2) against the graphs of the named sets of the paper.

Usage:  python ks_conjugate_closed_identify.py
Writes results/conjugate_closed_witness_graphs.json.
"""
import json
from pathlib import Path

import networkx as nx

import ks_conjugate_closed_theorem as C
import ks_extras_v10 as E

HERE = Path(__file__).resolve().parent
NAMED = ("ck31", "peres33", "sqrtm2-33", "eisenstein33", "ck33")


def main():
    named = {k: E.graph(k) for k in NAMED}
    recs = json.loads((HERE / "results" / "conjugate_closed_theorem.json").read_text(
        encoding="utf-8"))["uncolourable"]
    todo, graphs, lines, special, skipped = C.cases()
    by_label = {(kind, pt.label()): pt for kind, name, pt in todo}
    out = []
    for r in recs:
        if "witness" not in r or "mirror_of" in r:
            continue
        pt = by_label[(r["kind"], r["x"])]
        reps, pairs, triads = C.pool(pt)
        idx = {C.word_str(w): i for i, w in enumerate(reps)}
        keep = sorted(idx[w] for w in r["witness"])
        assert len(keep) == len(r["witness"]) == r["upper_bound"]
        assert not C.R.colourable(keep, pairs, triads), "witness is colourable"
        pos = {v: k for k, v in enumerate(keep)}
        g = nx.Graph()
        g.add_nodes_from(range(len(keep)))
        g.add_edges_from((pos[i], pos[j]) for i, j in pairs if i in pos and j in pos)
        iso = [k for k, h in named.items()
               if h.number_of_nodes() == g.number_of_nodes()
               and h.number_of_edges() == g.number_of_edges() and nx.is_isomorphic(g, h)]
        deg = sorted(d for _, d in g.degree())
        rec = {"kind": r["kind"], "name": r["name"], "x": r["x"], "status": r["status"],
               "size": len(keep), "pairs": g.number_of_edges(),
               "bases": r["bases_in_witness"],
               "degrees": {str(d): deg.count(d) for d in sorted(set(deg))},
               "isomorphic_to": iso}
        out.append(rec)
        print("%-6s %-46s %-16s %2d rays %3d pairs %2d bases  %s" % (
            r["kind"], r["name"][:46], r["status"], len(keep), g.number_of_edges(),
            r["bases_in_witness"], iso or "-"), flush=True)
    (HERE / "results" / "conjugate_closed_witness_graphs.json").write_text(
        json.dumps(out, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
