# Open Questions — Contextuality Project

Structured tracker for unresolved sub-problems of the algebraic-islands research
programme. Adapted from the agentic-erdos methodology
(github.com/przchojecki/agentic-erdos): per-problem notes with explicit
blocking lemmas and reduction targets, instead of loose prose.

## Purpose

- Separate **computational evidence** (done, strong) from **theorem-strength claims** (mostly open).
- Make each bottleneck explicit so progress is legible across sessions.
- Prevent the overclaim pattern peer reviewers keep catching ("exactly six",
  "measure-zero", "precisely the rings...") by forcing Literature / Approach /
  Blocker / Finish structure.

## File Layout

```
open_questions/
  README.md           <-- this file (index + policy)
  _TEMPLATE.md        <-- blank template, copy for new entries
  OQ-01-*.md          <-- one file per sub-problem
  OQ-02-*.md
  ...
```

One note per open question. No JSON/script triad unless a dedicated probe
script already exists (in which case link it; do not duplicate).

## Required Sections (from agentic-erdos proving-strategy.md)

Each OQ file must contain:

1. **Problem Statement** — normalized, with precise quantifiers.
2. **Literature Status** — known in literature / proved in-project /
   conjectural; name each clearly.
3. **Our Approaches** — attempts made, with outcomes (script refs, dates).
4. **Blocking Lemma(s)** — the concrete missing estimate or structural
   result. Be specific: "need quantitative bound X <= Y(N)", not "need more
   theory".
5. **What Would Finish the Proof** — the one intermediate theorem that, if
   proved, closes the question.

## Anti-Drift Rules (adopted verbatim)

- Do **not** treat empirical evidence as proof progress.
- Do **not** default back to computational scans when stuck.
- Prefer theorem-strength reductions over heuristic narratives.
- Distinguish: "known in literature", "proved in-project", "conjectural route".
- Promote claims only at the strength justified by evidence.

## Queue

| # | Title | Status | Priority |
|---|-------|--------|----------|
| OQ-01 | Norm-3 obstruction: no KS from norm >= 3 alphabets | open | high |
| OQ-02 | CK-31 optimality: algebraic proof of min integer KS = 31 | open | high |
| OQ-03 | Completeness of the six islands | open | medium |
| OQ-04 | Graph universality of CK-31 across constructions | partial | medium |
| OQ-05 | T=1 residual: role of all-nonzero triads for d ≡ 1 mod 4 | controlled | low |

Add new entries by copying `_TEMPLATE.md` and appending to the table.

## Policy Notes

- A "partial" OQ has a proved reduction but an unresolved residual; record
  the residual as a nested blocker.
- If a new computation is genuinely needed, it goes in `contextuality/ks_*.py`,
  not here. The OQ note links to it.
- When an OQ is resolved, move its entry to a "Closed" section below and keep
  the file (do not delete); record the closing argument.

## Closed

(none yet)
