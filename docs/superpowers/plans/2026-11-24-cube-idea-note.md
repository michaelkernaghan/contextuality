# Cube Idea Note Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A four-to-six-page standalone PDF, `idea/cube_idea.pdf`, that sets out the idea behind the alphabet construction in six short sections with one figure each.

**Architecture:** One exact-arithmetic script produces and checks every mathematical statement the note makes (the two identities, the 33 rays of Peres, the table of forced choices). A second script draws the six figures as TikZ, reusing the projection of the paper's cube figures. The note is one LaTeX file that inputs the generated table and figures.

**Tech Stack:** Python 3.11 (standard library only for the checks), TikZ, pdflatex (MiKTeX, off PATH: see memory `reference_miktex_pdflatex_windows`).

**Spec:** `docs/superpowers/specs/2026-11-24-cube-idea-note-design.md`

## Global Constraints

- No new result and no claim beyond v11.1. `paper/` is not touched.
- Reader: a physicist or a philosopher of science. "Ray", "orthogonal", "Hilbert space" are used without construction.
- Plain declarative prose. No theorem environments, no literature survey, no abstract (a three-sentence opening instead).
- No figure may suggest that nearness on the cube means anything about orthogonality; Section 4 says so in words.
- Black and white TikZ, same style as `paper/figures/alphabet_cube_*.pdf`.
- The PDF prints `cube_idea.pdf` on the first page and in every footer.
- `.tex` text goes through the Write/Edit tools, never a bash heredoc (backslashes are halved).
- Never `git add` anything under `docs/ks-sets/scans/`. Claude does not commit; commands are handed to Michael.
- Python runs with `PYTHONIOENCODING=utf-8` and `PYTHONUTF8=1`.

## Review Focus

- A reader takes "marked" in Section 2 to be value 1 in one place and value 0 in another: the note fixes one convention in Section 2 and the table uses the same one (checked by reading, Task 3 step 4).
- The forcing table uses "without loss of generality" that the script did not check: every symmetry reduction in the table is a signed permutation the script verified to map the 33 rays to themselves (Task 1 test).
- A figure's filled points differ from the set the script uses: figures read the ray list from the script's JSON, not from a second hand-typed list (Task 2 test).
- The sliding-line figure shows a pair as orthogonal at a value where it is not: the two identities are asserted for x = √2, 2, √3 in exact arithmetic (Task 1 test).
- The PDF overruns six pages or a figure overflows the margin: checked by reading every page of the built PDF (Task 3 step 4).

---

### Task 1: The checked mathematics

**Files:**
- Create: `ks_idea_forcing.py`
- Create (generated): `idea/forcing_table.tex`, `idea/idea_data.json`

**Interfaces:**
- Produces: `idea/idea_data.json` with keys `rays` (33 words, each three strings from `0, 1, -1, x, -x`), `pairs`, `triads` (index lists), `first_steps` (the forced choices drawn in Figure 5: list of `{ray, value, because}`), `cases` (the full table rows). `idea/forcing_table.tex` is a `tabular` built from `cases`.
- Numbers are stored as integer pairs `(a, b)` meaning `a + b√2`.

- [ ] **Step 1: Write the self-checks first, as functions called from `main()` that exit non-zero on failure**

```python
def check_identities():
    # (x,1,1).(x,-1,-1) = x^2 - 2 ; (1,1,x).(1,1,-1) = 2 - x
    assert dot_at((X,1,1), (X,-1,-1), SQRT2) == ZERO
    assert dot_at((X,1,1), (X,-1,-1), TWO) != ZERO
    assert dot_at((1,1,X), (1,1,-1), TWO) == ZERO
    assert dot_at((1,1,X), (1,1,-1), SQRT2) != ZERO
    assert dot_at((X,1,1), (X,-1,-1), SQRT3_SQUARED_CASE) != ZERO  # x^2 = 3

def check_peres():
    rays, pairs, triads = peres33()
    assert (len(rays), len(pairs), len(triads)) == (33, 72, 16)
    assert not colourable(rays, pairs, triads)                  # exhaustive backtracking
    assert all(colourable_without(rays, pairs, triads, i) for i in range(33))

def check_table(cases):
    # replay: every row's forced value follows from earlier rows of its case by
    # one pair or one triad; every case ends in a named contradiction;
    # the cases together cover a whole triad; every symmetry used maps the 33 rays to themselves
    ...
```

The counts 33 / 72 / 16 are v11's (memory: Peres-33 has 72 pairs, 16 triads). If the script disagrees, stop and report; do not adjust the assertion.

- [ ] **Step 2: Run `python ks_idea_forcing.py`; expected: fails (functions undefined)**

- [ ] **Step 3: Implement**

`peres33()`: rays over `{0, ±1, ±√2}` whose nonzero entries are, up to sign and order, `{1}`, `{1,1}`, `{1,√2}` or `{1,1,√2}` (3 + 6 + 12 + 12). `build_cases()`: branch on the axis triad, close each branch by unit propagation over pairs and triads, branch again only when propagation stops; where a branch is the image of an earlier one under a verified signed permutation, record that instead of repeating it. Write the JSON and the table.

- [ ] **Step 4: Run `python ks_idea_forcing.py`; expected: exit 0, prints `33 rays, 72 pairs, 16 triads, uncolourable, N table rows`**

- [ ] **Step 5: Negative control: delete one ray inside a temporary call and confirm `check_table` rejects the unchanged table; remove the temporary call**

### Task 2: The six figures

**Files:**
- Create: `make_idea_figures.py`
- Create (generated): `idea/figures/fig1_ray.tex` … `fig6_triptych.tex` and their PDFs

**Interfaces:**
- Consumes: `idea/idea_data.json` (Task 1); `proj`, `cube`, `standalone`, `face_point` imported from `make_alphabet_cube_figures.py`.
- Produces: six standalone PDFs named as above.

Figures: (1) cube with one line through the centre and its two exit points; (2) the three axes with one filled point and two open; (3) one face with the 5×5 grid, lines labelled 0, ±1, ±x; (4) one face drawn three times with the inner line at √2, √3, 2, the pair `(x,1,1)`, `(x,−1,−1)` joined by a line labelled "orthogonal" only at √2 and the pair `(1,1,x)`, `(1,1,−1)` only at 2; (5) the Peres cube with the `first_steps` rays numbered in the order they are forced; (6) the existing triptych, copied by calling `triptych()` with `OUT` redirected.

- [ ] **Step 1: Write `check_figures()`: the filled points of Figure 5 are exactly `rays` from the JSON; six `.tex` files exist and each compiles**
- [ ] **Step 2: Run; expected: fails**
- [ ] **Step 3: Implement the six figure functions**
- [ ] **Step 4: Run; expected: exit 0, six PDFs. Read each PDF with the Read tool and confirm no label overlaps a point**

### Task 3: The note

**Files:**
- Create: `idea/cube_idea.tex`

**Interfaces:**
- Consumes: `idea/figures/fig*.pdf`, `idea/forcing_table.tex`.

- [ ] **Step 1: Write the note.** Title "The idea behind the alphabet construction"; author line as on the paper; three-sentence opening; six numbered sections titled as in the spec, each about half a page with its figure; the table as an end section "The complete argument for the 33 rays"; one closing paragraph naming what the paper adds (more letters, complex x) with the arXiv number 2603.16988. Footer and first page print `cube_idea.pdf`.
- [ ] **Step 2: Build twice with pdflatex; expected: no errors, no overfull boxes wider than 5pt, four to six pages**
- [ ] **Step 3: Check every sentence that states a fact against `ks_idea_forcing.py` output or v11 text; list any that have neither source and remove or source them**
- [ ] **Step 4: Read every page of the PDF with the Read tool: one convention for "marked", figures in order, nothing over the margin**
- [ ] **Step 5: Open the PDF in Brave for Michael; stage by explicit path (`ks_idea_forcing.py make_idea_figures.py idea docs/superpowers`), confirm with `git status --short`, hand over the commit and push lines (branch `main`)**

### Addition 2026-11-24: Section 7, "The ladder of grids"

- Task 1 gains `check_ladder()`: the pool of `{0, ±1}` has exactly 13 rays and is colourable (exhaustive); the pool of `{0, ±1, ±x}` has 49 rays. The "no set below 31" statements for the second and third rungs are NOT recomputed here; the note cites Theorems `thm:twosymbol` and `thm:threesymbol` of v11.1 for them, and the wording is copied from v11's statements.
- Task 2 gains `fig7_ladder`: three faces, 3×3, 5×5, 7×7, captioned 13 / 49 / 145 rays.
- Task 3 gains Section 7 with its limits stated in the section itself (see spec). The page target becomes five to seven.
- Review Focus gains: a reader takes Section 7 to say 31 is the smallest Kochen-Specker set in three dimensions; the section must say in one plain sentence that it does not.

## Self-review

Spec coverage: reader and tone (Global Constraints, Task 3); six sections and figures (Tasks 2, 3); Section 5 table from a script (Task 1); file name on the page (Global Constraints); completion check (Task 3 steps 2 to 4). No gap found.
