# Version 12: prolegomena and vocabulary

Date: 2026-11-25. Status: awaiting Michael's approval.

## Intent

Version 12 of "The Algebraic Landscape of Kochen-Specker Sets in Dimension Three" opens with
a prolegomena that clarifies and motivates the work before any theorem is stated. It is an
abridged form of the companion note `idea/cube_idea.tex`. It also fixes the vocabulary, and
the rest of the paper is rewritten in that vocabulary.

## Goals

1. A reader who knows the Kochen-Specker theorem but not this paper can, after the
   prolegomena, say what a grid is, what question the paper asks, and why it was asked.
2. One vocabulary from the first page to the last.
3. No theorem, proof, table or number changes. Version 12 is a restatement of v11.1.

## Not goals

- No new results. The undetermined minima (x = 1+i, x = e^{i pi/3}/sqrt 2) stay open.
- Script names, Lean file names and Lean identifiers keep their present names.
- The companion note is not changed and not withdrawn. It stays the fuller account.

## What would make it a failure

- A prolegomena that repeats the introduction, so the reader meets the cube twice.
- A sentence that reads as a claim that 31 is proved minimal.
- A statement that the inner circle is the outer one under x -> 1/x (true only on the axes).
- A statement that a grid lacking minus signs is outside the theorems.
- Mixed vocabulary: "pool" or "word" surviving outside the one mapping sentence and the
  appendix of withdrawn claims.

## Approaches considered

1. **Separate opening section before the Introduction. CHOSEN (Michael, 11-25).** The
   vocabulary is set up in one place that a reader can turn back to, and the motivation is
   not interleaved with citations.
2. Fold into the Introduction. Rejected: motivation and vocabulary get scattered among the
   literature and the list of results.
3. Short pointer, with the note as an appendix. Rejected: the terms would be defined after
   the theorems that use them.

## Vocabulary (Michael's rulings)

| Version 11 | Version 12 |
|---|---|
| pool, raw pool | grid |
| completed pool | completed grid |
| word | coordinate triple (ruled 11-25 after review round 8; "grid point" was the first choice and was dropped because a point where lines cross and a triple of coordinate values are the same thing only for two coordinate values) |
| letter, symbol | coordinate value (never shortened to "value") |
| value 1 / value 0 under a coloring | colored / uncolored |

"Completed grid" carries one sentence where it is defined: the rays added by completion are
in general not grid points; a completed grid is a grid together with further points of the
cube that lie off its lines.

Claude's calls, for Michael to correct:

- **"alphabet"** becomes "the coordinate values of the grid" where it means the list, and
  the families are named by their grids: "grids with two coordinate values" (was two-symbol
  alphabets), "real grids with three coordinate values", "conjugate-closed grids".
- **"the 45 words"** becomes "the 45 grid points".
- **The formal definition of a coloring** keeps the map f: S -> {0,1}, with one added
  sentence: a ray with f = 1 is called colored. Proofs that compute with 0 and 1 keep doing
  so.
- **One mapping sentence** in the prolegomena gives the v11 terms (alphabet, letter, word,
  pool) for readers of earlier versions and of the scripts.
- **Appendix of withdrawn claims** keeps the old terms where it quotes or describes earlier
  versions, since those are the words the withdrawn claims were made in.
- **Title** unchanged.

## Structure of the prolegomena

New file `paper/v12_s0_prolegomena.tex`, about two and a half pages. Section title to be
agreed. Order:

1. A ray is a point on a cube. (Note, Section 1; short.)
2. The rule, and where it comes from: spin one, in three or four sentences; what a
   Kochen-Specker set excludes, stated exactly. (Note, Section 2.)
3. The grid. Peres's two drawings differ in the position of one pair of lines. Definitions
   of grid, grid point, coordinate value; completed grid; the mapping sentence.
   (Note, Section 3.)
4. Orthogonality depends on where the lines sit. The two inner products x^2 - 2 and x - 2.
   The warning that the picture shows position and not orthogonality. (Note, Section 4.)
5. The question: for which positions can the grid not be colored, and how few rays are
   needed? (Note, Section 6, the question only; the answer is the Introduction's job.)
6. The ladder: one, two, three coordinate values. The hope. What was found: elimination,
   not a proof that 31 is least, and why "lies on a grid" excludes nothing until the number
   of lines is bounded. (Note, Section 7, first three parts, shortened.)

Left out, staying in the note: the forcing table for Peres's 33 (note, Section 5) and the
passage on the open point 1+i.

Figures: the generic face or cube with named grid points, and the triptych, both moved from
the v11 introduction; the ladder figure from the note. The map of the x-plane is not placed
here. Instead the cubes A, B, C are pinned on the existing circle figure in the
conjugate-closed section.

## Changes to the rest of the paper

- **Introduction** becomes Section 2: literature, results, standard of proof, relation to
  earlier versions. Its "alphabet" paragraph and both cube figures move to the prolegomena.
- **Definitions and methods**: ray, triad and coloring stay as formal definitions; the grid
  definitions are restated formally there (S(A), completed grid), pointing back to the
  prolegomena for the picture.
- **Vocabulary pass** over the abstract, the seven sections, the two appendices and
  `v10_numbers.tex`: about 335 occurrences of the old terms in 11 files. Done one file at a
  time, by hand, not by search-and-replace, because "word", "letter" and "symbol" also occur
  in their ordinary senses.
- New sources are `algebraic_islands_v12.tex` and `v12_*.tex`, copied from v11. The v11
  sources are left untouched until v12 is released, then archived as v10 was.

## How the work proceeds

- The prolegomena is written with Michael, one numbered part at a time: Claude drafts a
  part, Michael reads it, it is revised, then the next part. "Deepen and simplify" is his
  test for each part.
- The vocabulary pass follows, one file at a time, each compiled and shown as a diff.
- Checks before release: the PDF compiles with no undefined references; a search of the
  v12 sources finds the old terms only in the mapping sentence and the withdrawn-claims
  appendix, with a control search that must match; every number in the v12 PDF text
  that appears in v11.1 is unchanged (text diff of the two PDFs outside the prolegomena).
- A review round on the finished text, as for v11, is Michael's decision at that point.
- Commits, the tag and the arXiv replacement are Michael's steps.

## Left to the builder

Wording of each sentence, within the rulings above; figure sizes; whether the generic
figure is redrawn from the note's Figure 3 or kept from v11.
