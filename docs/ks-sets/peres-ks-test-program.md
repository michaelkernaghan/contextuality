# Peres KS Coloring Test Program (Fortran)

## Source

Reconstructed from: A. Peres, *Quantum Theory: Concepts and Methods* (Kluwer, 1993), Appendix to Chapter 7, pages 209–211.

Original scans: [page 209](scans/peres-appendix-page209.jpg) | [page 210](scans/peres-appendix-page210.jpg) | [page 211](scans/peres-appendix-page211.jpg)

Fortran source: [peres-ks-test.f](peres-ks-test.f)

The original program may have been distributed as `realks.f` but no copy has been located online.

---

## Purpose

This Fortran 77 program tests whether a given set of rays in 3-dimensional real Hilbert space can be consistently colored in a noncontextual manner. It implements a backtracking search to determine if any valid green/red assignment exists for the Kochen-Specker coloring problem.

A **consistent coloring** assigns each ray a color (green = 1 or red = 0) such that in every orthogonal triad, exactly one ray is green and two are red. The **Kochen-Specker theorem** states that for certain sets of rays (e.g., Peres's 33 rays), no such coloring exists.

---

## Color Convention

| Value | Meaning | Description |
|-------|---------|-------------|
| 4 | Uncolored | Ray has not yet been assigned |
| 1 | Green | Ray assigned value "yes" (projector eigenvalue 1) |
| 0 | Red | Ray assigned value "no" (projector eigenvalue 0) |

---

## Algorithm

The program uses **backtracking with forced-move propagation**:

1. **Build triads**: From the input orthogonality pairs, enumerate all orthogonal triads (three mutually orthogonal rays).

2. **Arbitrary choice** (label 14): Find the first uncolored ray. Make it green. Record the decision level.

3. **Propagate** (label 18–19): All rays orthogonal to a green ray must be red.

4. **Check contradictions** (label 20–21): Scan all triads. If any triad has three red rays, this is a contradiction (at least one must be green).

5. **Backtrack on contradiction** (label 22–24): Restore to the last decision point. If the last choice was green (LAST=1), try red instead (LAST=0). If both green and red have been tried, backtrack further.

6. **Forced moves** (label 25–27): If any triad has two red rays and one uncolored ray, the uncolored ray *must* be green. Apply this and return to propagation (step 3).

7. **Termination**: Either a consistent coloring is found (printed to output) or all options are exhausted ("No consistent coloring").

---

## Variables

| Variable | Type | Description |
|----------|------|-------------|
| `N` | Parameter | Total number of rays |
| `P(N,N)` | Integer | Orthogonality matrix: `P(I,J)=1` if rays I and J are orthogonal |
| `X(N), Y(N), Z(N)` | Integer | Ray indices for each triad (X=1st, Y=2nd, Z=3rd) |
| `C(N)` | Integer | Current color of each ray (0, 1, or 4) |
| `L(N)` | Integer | Which ray was colored at each decision level |
| `OC(N,N)` | Integer | Saved state of `C` at each decision level |
| `NTRIAD` | Integer | Number of orthogonal triads found |
| `LVL` | Integer | Current backtracking depth |
| `LAST` | Integer | 1 if last choice was green, 0 if red |
| `NG` | Integer | Index of the ray currently being colored |

---

## Input Format

**File**: `INPUT.KS`

Each line contains a pair of orthogonal ray indices in format `2I3` (two 3-digit integers):

```
  1  2
  1  5
  2  3
  ...
```

The ray numbering (1 to N) must be consistent. Only orthogonal pairs need to be listed — the program builds triads automatically by finding all triples where all three pairs are orthogonal.

---

## Output Format

**File**: `OUTPUT.KS`

Either:
- A line of N integers (format `40I2`) showing the coloring: `1` = green, `0` = red
- Or the message: `No consistent coloring`

---

## Usage

1. Set `PARAMETER (N=33)` to the number of rays (33 for Peres, 31 for Conway-Kochen)
2. Prepare `INPUT.KS` with all orthogonal ray pairs
3. Compile: `gfortran -o kstest peres-ks-test.f`
4. Run: `./kstest`
5. Check `OUTPUT.KS` for result

---

## Expected Results

| Ray Set | N | Triads | Expected Output |
|---------|---|--------|-----------------|
| Peres 33 | 33 | 16 | No consistent coloring |
| Conway-Kochen 31 | 31 | 17 | No consistent coloring |
| Peres 33 minus any 1 ray | 32 | varies | Consistent coloring found |
| Conway-Kochen 31 minus any 1 ray | 30 | varies | Consistent coloring found |

---

## Reconstruction Notes

- Pages 209 and 211 were photographed upside down, introducing some uncertainty in the transcription
- The flow after label 24 (continuation from page 210 to 211) is the least certain part — specifically the `GOTO 20` target
- The `PARAMETER (N=33)` was left blank in the original for users to fill in
- The P array relies on implicit zero-initialization (standard in most Fortran 77 implementations)
- Array sizes assume NTRIAD <= N, which holds for all known 3D KS sets

---

## Exercises (from page 211)

**Exercise 7.20** Show that the 31 rays in Plate II (p. 114) form 17 orthogonal triads.

**Exercise 7.21** Show that removing any one of these 31 rays leaves a set that can be consistently colored.

**Exercise 7.22** Write a similar program for the Kochen-Specker problem in four dimensions.

---

## Cross-Links

- [Peres 33-Vector KS Set (3D)](peres-33-3d.md) — The 33-ray construction this program tests
- [Conway-Kochen 31-Vector Construction (3D)](conway-kochen-31-3d.md) — Another set to test
- [Kochen-Specker Theorem History](../history/kochen-specker.md) — Full historical context
- [Kernaghan 20-Vector KS Set (4D)](kernaghan-20-4d.md) — Exercise 7.22 asks for a 4D version
