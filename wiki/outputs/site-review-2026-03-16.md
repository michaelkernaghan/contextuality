---
source: raw/contextuality-site-review-20260316.txt
date_ingested: 2026-04-03
type: query-output
reviewer: GPT-5.4 (via Codex)
document: 14,502 words from 13 pages
tokens_used: 75,734
---

# Site Peer Review (March 16, 2026)

## Summary

GPT-5.4 reviewed the contextuality KS-set atlas website (13 pages, ~14,500 words). Overall verdict: the site is technically ambitious with impressive internal quantitative consistency across six algebraic islands (CK-31, Peres-33, Eisenstein-33, Z[sqrt(-2)]-33, Heegner-7/43, Golden-52). The core vector/pair/rigidity data hang together well. However, several specific errors and structural problems require attention before the site reads as a credible research atlas rather than a hybrid of polished pages and working notes.

The reviewer flagged seven specific findings ranging from mathematical errors to presentation problems, then provided an eight-category assessment.

## Critical Issues

- **Heegner-7 CSW table is mathematically impossible as written**: lists alpha(G)=50 for a 43-vector set, if G is the KS orthogonality graph. Either the graph is not the KS graph, or the numbers/notation are wrong. This undermines the strongest "highest contextual advantage" claim. (heegner7-43-3d.md:71)
- **"Fundamental unit" error**: In Q(sqrt(-7)), calling (1+sqrt(-7))/2 a "fundamental unit" is wrong. It is an algebraic integer of norm 2, not a fundamental unit. (heegner7-43-3d.md:105)
- **Ontological instability in "six islands" claim**: The same page says Gaussian integers Z[i] produce the Peres graph. If islands classify rings, Gaussian looks like a seventh ring; if islands classify graph-families, the wording should say that. The ontology shifts mid-argument. (index.md:32, algebraic-islands.md:5, algebraic-islands.md:16)
- **Peres page OCR-like prose**: The opening is hard to trust and hard to read; the "24 distinct vectors" line is especially garbled. (peres-33-3d.md:13)
- **Chronology metadata problems on Recent Papers page**: Title says 2022-2025 but page includes a 2026 section and is stamped March 2026; one entry says "Date: 2024 (published PRL 2025)". (recent-papers.md:1, :19, :56, :313)
- **GPT-review note weakens scholarly credibility**: The public-facing note about chatbot review rounds does not belong in the same evidentiary frame as theorem/proof claims. (papers.md:89)

## Status Labeling Problem

Complete theorems, computational evidence, heuristic BPQS upper bounds, and conjectures are placed in the same rhetorical register. This is risky for readers evaluating new 2026 claims. (algebraic-islands.md:95, :133; heegner7-43-3d.md:85; golden-52-3d.md:84)

## Assessment by Category

| Category | Assessment |
|---|---|
| Scientific accuracy | Mostly strong on internal counts; main problems are Heegner CSW table, "fundamental unit" error, ring-vs-island taxonomy |
| Completeness | Good for six-island narrative; weaker around CK-33, Gaussian, Penrose, Cabello 2025 equivalence |
| Accessibility | Graduate student in quantum foundations can follow; newcomer will struggle with OCUS, MUS, VF2, BPQS, CSW, merge-saturation, Jacobian rigidity (used before explained) |
| Site structure | Top-level organization sensible; main weakness is no visual separation between established literature, 2026 results, heuristic findings, and conjectures |
| Writing quality | Overview pages clear and energetic; Peres page and compressed research claims read like internal notes |
| New results presentation | Broadly convincing (especially Eisenstein vs Peres vs Z[sqrt(-2)] on rigidity/flex); weakest point is Cabello 2025 relationship (needs explicit statement of equivalence) |
| Bibliography | Good core coverage; style inconsistent (some full citations, some placeholders/shorthand) |

## Recommendations

- Add status badges everywhere: Proved / Computational evidence / Heuristic bound / Conjecture / Unpublished
- Fix the Heegner-7 CSW section first, with an explicit definition of the graph whose alpha and vartheta are being quoted
- Rewrite the Peres opener into clean original prose; keep the historical scan as a figure, not as primary exposition
- Decide whether "islands" classify rings, graph types, or realizability classes, and enforce that language consistently
- Add one glossary/methods page for BPQS, CSW, OCUS, MUS, VF2, rigidity, and merge operations
- Add dedicated comparison pages or appendices for CK-33, Gaussian/Peres realizations, and the Cabello 2025 identification
- Normalize bibliography entries to one citation style and remove the GPT-review note from the public research narrative
- Add a downloadable data appendix for vector certificates

## Related

- [[algebraic-islands-main]]
