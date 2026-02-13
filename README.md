# The Algebraic Landscape of Kochen-Specker Sets in Dimension Three

Computational investigation of the number fields and coordinate alphabets supporting Kochen-Specker (KS) sets in three-dimensional Hilbert space.

## Paper

**"The Algebraic Landscape of Kochen-Specker Sets in Dimension Three"** by Michael Kernaghan

- LaTeX source: [`paper/algebraic_islands.tex`](paper/algebraic_islands.tex)
- Compiled PDF: [`paper/algebraic_islands.pdf`](paper/algebraic_islands.pdf)

## Main Results

- **Four algebraic islands** support KS sets among all fields tested: integers (min 31), Q(sqrt(2)) (min 33), Eisenstein integers (min 33), and the golden ratio field Q(phi) (min 52).
- The **golden ratio island** is newly discovered, invisible to raw alphabet searches and revealed only by cross-product completion.
- **6|n conjecture**: nth roots of unity produce KS-uncolorable sets iff 6 divides n (verified for n <= 30).
- **Realizability gap**: 49% of random abstract hypergraphs are KS-uncolorable, but 0% were found realizable in R^3.
- The Conway-Kochen 31-vector set is **destroyed by 1% coordinate perturbation**.

## Code

| Script | Purpose |
|--------|---------|
| `ks_islands.py` | Algebraic island survey, generates Tables 1-5 and 7 |
| `ks_complex.py` | Roots of unity survey, generates Table 6 |
| `ks_geometry.py` | Realizability gap experiments, generates Table 8 |
| `ks_sat.py` | SAT-based KS coloring via PySAT/Glucose4 |
| `ks_search.py` | Randomized greedy KS minimization |
| `ks_ring_of_integers.py` | Ring-of-integers generator tests for d = 1 mod 4 |
| `ks_test.py` | Unit tests |
| `find_peres33.py` | Peres 33-vector KS set finder |
| `verify_peres33.py` | Verification of Peres 33-vector set |

## Requirements

- Python 3.11+
- [PySAT](https://pysathq.github.io/) 1.8+ (Glucose4 solver)
- NumPy
- SciPy

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

## References

- M. Kernaghan, "Bell-Kochen-Specker theorem for 20 vectors," *J. Phys. A* **27**, L829-L830 (1994).
- M. Kernaghan and A. Peres, "Kochen-Specker theorem for eight-dimensional space," *Phys. Lett. A* **198**, 1-5 (1995).
