# Algebraic Landscape of Kochen-Specker Sets in Dimension Three

Computational companion to four papers on the number-theoretic structure of Kochen-Specker (KS) contextuality in three-dimensional Hilbert space. All scripts reproduce the tables and results cited in the papers.

## Papers

| Paper | Source | PDF |
|-------|--------|-----|
| The Algebraic Landscape of Kochen-Specker Sets in Dimension Three | [`paper/algebraic_islands.tex`](paper/algebraic_islands.tex) | [`paper/algebraic_islands.pdf`](paper/algebraic_islands.pdf) |
| Cyclotomic Letter | [`paper/cyclotomic_letter.tex`](paper/cyclotomic_letter.tex) | [`paper/cyclotomic_letter.pdf`](paper/cyclotomic_letter.pdf) |
| Heegner-7 Letter | [`paper/heegner7_letter.tex`](paper/heegner7_letter.tex) | [`paper/heegner7_letter.pdf`](paper/heegner7_letter.pdf) |
| Sub-31 Letter | [`paper/sub31_letter.tex`](paper/sub31_letter.tex) | [`paper/sub31_letter.pdf`](paper/sub31_letter.pdf) |
| Universality Letter | [`paper/universality_letter.tex`](paper/universality_letter.tex) | [`paper/universality_letter.pdf`](paper/universality_letter.pdf) |

## Main Results

- **Four algebraic islands** support KS sets: integers (min 31 vectors), Q(√2) (min 33), Eisenstein integers (min 33), and the golden ratio field Q(φ) (min 52).
- **Golden ratio island** — newly discovered, invisible to raw alphabet searches, revealed only by cross-product completion.
- **6|n conjecture** — nth roots of unity produce KS-uncolorable sets iff 6 divides n (verified for n ≤ 30).
- **Realizability gap** — 49% of random abstract hypergraphs are KS-uncolorable, but 0% were found realizable in R³.
- The Conway-Kochen 31-vector set is **destroyed by 1% coordinate perturbation**.

## Computational Scripts

### Core survey and verification

| Script | Purpose |
|--------|---------|
| `ks_islands.py` | Algebraic island survey — generates Tables 1–5 and 7 |
| `ks_complex.py` | Roots of unity survey — generates Table 6 |
| `ks_geometry.py` | Realizability gap experiments — generates Table 8 |
| `ks_sat.py` | SAT-based KS coloring via PySAT/Glucose4 |
| `ks_search.py` | Randomized greedy KS minimization |
| `ks_ring_of_integers.py` | Ring-of-integers generator tests for d ≡ 1 mod 4 |
| `ks_test.py` | Unit tests |
| `find_peres33.py` | Peres 33-vector KS set finder |
| `verify_peres33.py` | Verification of Peres 33-vector set |
| `ks_spectral_filter.py` | Spectral prefilter for fast KS candidate screening |

### Extended analysis

| Script | Purpose |
|--------|---------|
| `ks_new_islands.py` | Search for new algebraic islands |
| `ks_new_island_analysis.py` | Analysis of newly discovered islands |
| `ks_csw.py` | Cabello-Severini-Winter graph-theoretic contextuality |
| `ks_csw_extended.py` | Extended CSW analysis |
| `ks_graph_analysis.py` | Graph-theoretic properties of KS sets |
| `ks_critical_bases.py` | Critical basis identification |
| `ks_bpqs_sat.py` | SAT-based BPQS analysis |
| `ks_trig.py` | Trigonometric coordinate analysis |
| `ks_group_isomorphism.py` | Group isomorphism tests for KS symmetries |
| `ks_literature_connections.py` | Cross-references with published KS results |

### Optimization and proof

| Script | Purpose |
|--------|---------|
| `ks_explore_new.py` | Exploratory search for novel KS constructions |
| `ks_explore_new2.py` | Extended exploratory search |
| `ks_ocus_all_pools.py` | Optimal constrained unsatisfiable subsets |
| `ks_maxsat_optimal.py` | MaxSAT-based optimal KS minimization |
| `ks_peres_merge.py` | Peres set merging strategies |
| `ks_mus_landscape.py` | Minimal unsatisfiable subset landscape |
| `ks_rigidity.py` | Rigidity analysis of KS sets |
| `ks_rigidity_finite.py` | Finite-field rigidity analysis |
| `ks_ck33_identify.py` | Conway-Kochen 33-vector set identification |

### Number-theoretic extensions

| Script | Purpose |
|--------|---------|
| `ks_quaternion.py` | Quaternion algebra KS constructions |
| `ks_octonion.py` | Octonion algebra KS constructions |
| `ks_6n_proof.py` | 6|n divisibility conjecture — proof framework |
| `ks_6n_proof_theorem.py` | 6|n conjecture — theorem statements |

## Requirements

- Python 3.11+
- [PySAT](https://pysathq.github.io/) 1.8+ (Glucose4 solver)
- NumPy, SciPy

```bash
pip install python-sat numpy scipy
```

## Reproducibility

All randomized experiments use `random.seed(42)`. Run individual scripts to regenerate tables:

```bash
python ks_islands.py      # Tables 1-5, 7
python ks_complex.py      # Table 6
python ks_geometry.py     # Table 8
```

## Archive

The complete development history including intermediate scripts is preserved on the [`archive-full`](../../tree/archive-full) branch.

## References

- M. Kernaghan, "Bell-Kochen-Specker theorem for 20 vectors," *J. Phys. A* **27**, L829–L830 (1994).
- M. Kernaghan and A. Peres, "Kochen-Specker theorem for eight-dimensional space," *Phys. Lett. A* **198**, 1–5 (1995).

## License

This code is provided for academic reproducibility. See the papers for citation details.
