# Multi-Reviewer Protocol for Contextuality Papers

## Inspired by Moreno et al. (arXiv:2603.20179) JFC Framework

## Overview
Before submission of any paper, run 4 independent reviewer agents, each with
a distinct mandate and deliberately different information access. An arbiter
synthesizes findings into PASS / ITERATE / ESCALATE.

---

## Reviewer 1: Algebraic Correctness Reviewer

**Role**: Pure mathematician checking proofs and algebraic claims.

**Access**: The paper only. NO access to our scripts, computational output, or memory files.

**Mandate**:
- Verify every algebraic identity (e.g., norm-2 cancellation, vanishing sums, Eisenstein identity)
- Check proof logic in all lemmas/theorems (especially cyclotomic 6|n proof)
- Flag any step that assumes computational evidence where a proof is claimed
- Verify definitions are consistent (B-KS, KS-uncolorable, orthogonality)
- Check that notation is consistent across sections
- Category A: logical gaps in proofs, incorrect algebraic claims
- Category B: unclear proof steps, missing intermediate results
- Category C: notation inconsistencies

**Prompt template**:
```
You are a pure mathematician reviewing a paper on Kochen-Specker sets.
You have NO access to the computational scripts — evaluate the paper
purely on the mathematical content presented. For each claim, assess:
(1) Is the proof complete? (2) Are algebraic identities correct?
(3) Are there hidden assumptions? Classify issues as A (proof gap),
B (unclear/incomplete), or C (notation/style).
```

---

## Reviewer 2: Computational Verification Reviewer

**Role**: Computational scientist checking that claims match evidence.

**Access**: The paper AND all Python scripts. NO access to references or literature.

**Mandate**:
- For every table of results, verify the script exists and could produce those numbers
- Check reproducibility: random seeds, solver versions, parameter choices
- Flag any claim not backed by a specific script (e.g., "exhaustive search" — over what space?)
- Verify SAT solver usage is correct (UNSAT = uncolorable, not the other way)
- Check statistical claims (confidence bounds, sample sizes)
- Verify OCUS/MUS methodology is correctly described
- Category A: result not reproducible, script doesn't match claim
- Category B: missing reproducibility details, unclear parameters
- Category C: script naming, code organization

**Prompt template**:
```
You are a computational scientist reviewing a paper that combines algebra
and SAT solving. You have access to all scripts in the contextuality/
directory. For every numerical claim or table entry, find the script that
produces it. Verify: (1) Does the script implement what the paper describes?
(2) Are parameters (seeds, timeouts, pool sizes) correctly reported?
(3) Could someone reproduce these results? Classify as A/B/C.
```

---

## Reviewer 3: Literature & Novelty Reviewer

**Role**: Domain expert checking positioning against existing work.

**Access**: The paper AND the full reference corpus (references/corpus/). NO scripts.

**Mandate**:
- For every novelty claim, check it against the corpus papers
- Specifically verify: "Heegner-7 and Golden are genuinely new" — are they in any catalogue?
- Check if Trandafir-Cabello 2025 supersedes any of our rigidity claims
- Verify our characterization of Cabello 2025 simplest set is accurate
- Check if Cortez-Morales-Reyes 2022 Z[1/6] result is correctly cited
- Look for papers in the gap-check list that we should cite
- Verify our "six islands" claim isn't contradicted by recent work
- Check author self-citation (Kernaghan1994, KernaghanPeres1995) is appropriate
- Category A: novelty claim contradicted by literature, missed critical reference
- Category B: imprecise characterization of prior work, missing comparison
- Category C: citation formatting, reference completeness

**Prompt template**:
```
You are a contextuality/KS theory expert reviewing a paper for novelty
and literature coverage. You have access to a corpus of reference papers.
For every novelty claim, search the corpus for contradicting evidence.
For every characterization of prior work, verify accuracy. Check the
gap-check list in CORPUS-INDEX.md for potentially missing references.
Classify as A (false novelty/missed critical ref), B (imprecise), C (minor).
```

---

## Reviewer 4: Narrative & Presentation Reviewer

**Role**: Journal referee evaluating readability and argument structure.

**Access**: The paper only. NO scripts, NO references, NO memory files.

**Mandate**:
- Is the central thesis (norm-2 boundary) clearly stated and supported?
- Does the paper flow logically from introduction through results to conclusion?
- Are figures/tables necessary and well-labeled?
- Is the abstract accurate — does it promise what the paper delivers?
- Are limitations honestly stated?
- Is the paper the right length for its venue (arXiv preprint vs PRL letter)?
- Is the LLM verification methodology section appropriate and well-placed?
- Category A: thesis unsupported by presented evidence, misleading abstract
- Category B: structural problems, missing motivation, unclear argument
- Category C: style, grammar, formatting

**Prompt template**:
```
You are an anonymous journal referee for Physical Review A. Evaluate this
paper purely on its narrative structure, clarity, and persuasiveness.
Do NOT verify algebra or check references — focus on whether a reader
would find the argument compelling and well-organized. Classify as A/B/C.
```

---

## Arbiter Protocol

After all 4 reviewers report, the arbiter:

1. **Collects** all findings into a unified table: finding, source reviewer(s), category, agreement
2. **Resolves conflicts**: If reviewers disagree on severity, take the higher rating
3. **Cross-validates**: If the algebra reviewer flags a proof gap AND the computational
   reviewer can't find supporting evidence, escalate to Category A
4. **Decides**:
   - **PASS**: No Category A, fewer than 3 unresolved Category B
   - **ITERATE**: Category A items exist but are fixable in current draft
   - **ESCALATE**: Fundamental issue (false novelty claim, incorrect proof, irreproducible result)

---

## Execution Plan

### Per-Paper Review Order
1. `algebraic_islands.tex` (main paper, 36 pages) — full 4-reviewer protocol
2. `sub31_overview.tex` (overview, 16 pages) — full 4-reviewer protocol
3. Letters (cyclotomic, heegner7, universality, sub31) — 2-reviewer minimum
   (Reviewer 1 + Reviewer 3, since letters are shorter)

### Cost Estimate
- Each reviewer: ~1 Opus invocation with paper + context = ~$2-4
- Full 4-reviewer + arbiter on main paper: ~$15-20
- Full suite across all 6 papers: ~$50-80
- GPT peer review cross-check: ~$1.50 per paper (existing workflow)

### Integration with Existing Workflow
This protocol ADDS to, not replaces, our existing 3-layer verification:
1. **Layer 1**: Symbolic computation (scripts verify algebra)
2. **Layer 2**: SAT solver (independent verification of uncolorability)
3. **Layer 3**: GPT peer review (existing `peer_review_submit.py`)
4. **Layer 4 (NEW)**: Multi-reviewer protocol (this document)

### When to Run
- Before arXiv submission (main paper: done, but run on revisions)
- Before any journal submission
- After significant revisions (e.g., adding new results)
- After incorporating feedback from external reviewers
