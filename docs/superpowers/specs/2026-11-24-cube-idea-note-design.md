# Design: companion note "The idea behind the alphabet construction"

Date: 2026-11-24. Status: awaiting Michael's approval. Size: small (one short document, six figures).

## Intent

The three-dimensional Kochen-Specker paper (v11.1, arXiv 2603.16988) grows from one idea:
name each ray by the point where it leaves the surface of a cube, notice that the points of
the known sets lie on a grid, and ask which grids carry a set that cannot be colored. The
paper states this in ten lines for a specialist. Michael wants the idea set out as plainly as
Einstein sets out his in *Relativity: The Special and the General Theory*.

## Reader

A physicist opening the arXiv paper, or a philosopher of science. "Ray", "orthogonal" and
"Hilbert space" may be used without construction. Every statement must be unambiguous to
both readers.

## Goals

- Seven short numbered sections, about half a page each, one simple figure per section.
- Plain declarative prose. No theorem environments, no literature survey.
- Readable alone, without the 27-page paper. Five to seven pages.
- Every mathematical statement is true as written and checked by a script in exact arithmetic.

## Non-goals

- No new result. No claim beyond v11.1.
- No change to the v11 paper or its arXiv record.
- Complex alphabets are named in one closing paragraph, not drawn.

## Anti-goals

- A picture that suggests nearness on the cube means anything about orthogonality.
- A "proof sketch" in Section 5 that a reader cannot follow to the end or that is not exact.
- Academic register: hedged sentences, citation clusters, passive constructions.

## Approaches

- **A. Standalone companion note (chosen by Michael 2026-11-24).** Free in tone, readable
  alone, leaves v11.1 untouched. Readers of the paper see it only if pointed to it.
- **B. New opening section of the paper (v12).** Every reader meets it first, but it must
  match the paper's register and needs another arXiv replacement.
- C. Longer captions on the existing two figures. Dropped: captions cannot carry six steps.

The note is written so that it can become Section 1 of a later v12 with little change.

## The six sections

1. **A ray is a point on a cube.** A line through the centre leaves the surface at two
   opposite points; either names it. Figure: a cube, one line.
2. **The rule.** Of three mutually orthogonal rays exactly one is marked; two orthogonal rays
   are never both marked. One sentence on the spin-1 measurement this stands for. Figure:
   the three axes, one filled point.
3. **The points form a grid.** In the drawings of Peres and of Conway and Kochen the points
   sit on lines at 0, ±1, ±x. Figure: one face.
4. **Orthogonality depends on where the lines sit.** `(x,1,1)·(x,−1,−1) = x² − 2` and
   `(1,1,x)·(1,1,−1) = 2 − x`. Figure: the grid line sliding; the pairs become orthogonal at
   √2 and at 2 only.
5. **Enough orthogonal pairs leave no way to mark.** The first forced choices are drawn; the
   complete argument for the 33 rays of Peres is given as one table at the end.
6. **The question and its answer.** For which x does this happen? Figure: the existing
   triptych (√2, 2, √3). One closing paragraph on what the paper adds (more letters, complex x).

7. **The ladder of grids** (added by Michael 2026-11-24). Grids are ordered by their number
   of letters. Bottom rung, letters 0 and ±1: 13 rays, colorable. Second rung, one further
   letter x: 49 rays, uncolorable only at the values of Section 6, never with fewer than 31
   rays. Third rung, two further real letters: no set below 31 either. Stated limits, in the
   same section: this excludes a smaller set from these grids only; every finite set of rays
   lies on some grid with enough letters, so the general minimum (between 24 and 31) stays
   open; the complex rung with x and its conjugate has two points whose minimum is not
   settled. Figure: three faces side by side, 3×3, 5×5, 7×7, each with its count.

## Claude's calls (not decided by Michael; correct any of them)

- Location: `idea/cube_idea.tex`, figures in `idea/figures/`, generator `make_idea_figures.py`
  at the repository root beside `make_alphabet_cube_figures.py`, reusing its projection.
- Section 5 uses the Peres 33-ray set, because its points are the ones in the Section 3
  figure. The table of forced choices is produced and checked by a script
  (`ks_idea_forcing.py`), not written by hand.
- Figures are black and white TikZ, same style as the paper's two cube figures.
- The PDF prints its own file name on the first page and in the footer (standing rule 11-21).
- Author line as on the paper. No abstract; a three-sentence opening instead.
- Not committed by Claude; commit and push commands are handed to Michael.

## Left to the builder

Wording, figure geometry, the order of rows in the forcing table.

## Check that the work is done

`pdflatex idea/cube_idea.tex` builds without error; `python ks_idea_forcing.py` exits 0 and
its table matches the one in the note; the two identities in Section 4 are asserted in the
same script.
