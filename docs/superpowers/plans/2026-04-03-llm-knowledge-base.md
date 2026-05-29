# LLM Knowledge Base Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Karpathy-style LLM-maintained knowledge base for contextuality research with auto-ingest, Q&A, and linting via three Claude Code skills.

**Architecture:** Three skills (`/kb-ingest`, `/kb-query`, `/kb-lint`) operate on a `wiki/` Obsidian vault inside `~/contextuality/`. A `raw/` drop zone stages source material. The LLM maintains all wiki content, INDEX.md, and backlinks. User browses in Obsidian.

**Tech Stack:** Claude Code skills (markdown), Obsidian (viewer), existing `~/contextuality/` git repo.

**Spec:** `docs/superpowers/specs/2026-04-03-llm-knowledge-base-design.md`

---

### Task 1: Create Directory Structure and Templates

**Files:**
- Create: `~/contextuality/raw/.gitkeep`
- Create: `~/contextuality/wiki/INDEX.md`
- Create: `~/contextuality/wiki/concepts/.gitkeep`
- Create: `~/contextuality/wiki/papers/.gitkeep`
- Create: `~/contextuality/wiki/people/.gitkeep`
- Create: `~/contextuality/wiki/computations/.gitkeep`
- Create: `~/contextuality/wiki/open-questions/.gitkeep`
- Create: `~/contextuality/wiki/outputs/.gitkeep`
- Create: `~/contextuality/wiki/_templates/paper.md`
- Create: `~/contextuality/wiki/_templates/concept.md`
- Create: `~/contextuality/wiki/_templates/computation.md`
- Create: `~/contextuality/wiki/_templates/person.md`
- Create: `~/contextuality/wiki/_templates/open-question.md`
- Create: `~/contextuality/wiki/.obsidian/app.json`
- Create: `~/contextuality/.gitignore` (modify if exists — add `.obsidian/workspace.json`)

- [ ] **Step 1: Create the raw/ and wiki/ directory trees**

```bash
cd ~/contextuality && mkdir -p raw wiki/concepts wiki/papers wiki/people wiki/computations wiki/open-questions wiki/outputs wiki/_templates wiki/.obsidian
```

- [ ] **Step 2: Create .gitkeep files for empty directories**

```bash
cd ~/contextuality && touch raw/.gitkeep wiki/concepts/.gitkeep wiki/papers/.gitkeep wiki/people/.gitkeep wiki/computations/.gitkeep wiki/open-questions/.gitkeep wiki/outputs/.gitkeep
```

- [ ] **Step 3: Create the paper article template**

Write `wiki/_templates/paper.md`:

```markdown
---
source:
date_ingested:
type: paper
---

# Title (Author, Year)

## Summary


## Key Claims
-

## Methods
-

## Relevance to Our Work
- Links to [[]]
-

## Open Questions
-
```

- [ ] **Step 4: Create the concept article template**

Write `wiki/_templates/concept.md`:

```markdown
---
date_ingested:
type: concept
---

# Concept Name

## Definition


## Key Results
-

## Connections
- [[]]

## In Our Work
-

## Open Questions
-
```

- [ ] **Step 5: Create the computation article template**

Write `wiki/_templates/computation.md`:

```markdown
---
source:
date_ingested:
type: computation
---

# Script Name

## Purpose


## Inputs
-

## Outputs
-

## Key Results
-

## Dependencies
- [[]]
```

- [ ] **Step 6: Create the person article template**

Write `wiki/_templates/person.md`:

```markdown
---
date_ingested:
type: person
---

# Name

## Affiliation


## Key Contributions
-

## Relevant Papers
- [[]]

## Connection to Our Work
-
```

- [ ] **Step 7: Create the open-question article template**

Write `wiki/_templates/open-question.md`:

```markdown
---
date_ingested:
type: open-question
status: open
---

# Question

## Statement


## Why It Matters
-

## What We Know
-

## Related
- [[]]
```

- [ ] **Step 8: Create the initial INDEX.md**

Write `wiki/INDEX.md`:

```markdown
# Contextuality Knowledge Base Index

> Auto-maintained by LLM. Do not edit manually.

**Last updated:** 2026-04-03
**Article count:** 0

## Concepts

(none yet)

## Papers

(none yet)

## People

(none yet)

## Computations

(none yet)

## Open Questions

(none yet)

## Outputs

(none yet)
```

- [ ] **Step 9: Create minimal Obsidian config**

Write `wiki/.obsidian/app.json`:

```json
{
  "useMarkdownLinks": false,
  "newLinkFormat": "shortest",
  "showLineNumber": true,
  "strictLineBreaks": true
}
```

This ensures Obsidian uses `[[wiki-links]]` (not markdown links) and shortest-path linking.

- [ ] **Step 10: Update .gitignore**

Append to `~/contextuality/.gitignore` (create if missing):

```
# Obsidian workspace state (user-specific, don't commit)
wiki/.obsidian/workspace.json
wiki/.obsidian/workspace-mobile.json
wiki/.obsidian/plugins/
wiki/.obsidian/themes/
```

- [ ] **Step 11: Commit**

```bash
cd ~/contextuality && git add raw/ wiki/ .gitignore && git commit -m "feat: add wiki/ and raw/ directory structure for LLM knowledge base"
```

---

### Task 2: Create `/kb-ingest` Skill

**Files:**
- Create: `~/.claude/skills/kb-ingest/SKILL.md`

- [ ] **Step 1: Create the skill directory**

```bash
mkdir -p ~/.claude/skills/kb-ingest
```

- [ ] **Step 2: Write the skill file**

Write `~/.claude/skills/kb-ingest/SKILL.md`:

```markdown
---
name: kb-ingest
description: Ingest raw sources into contextuality knowledge base wiki. Use when user says "kb-ingest", "ingest into wiki", or "process raw files". Do NOT use for querying or linting.
---

# KB Ingest

Process raw source files into structured wiki articles for the contextuality knowledge base.

## Prerequisites

- Working directory or target: `~/contextuality/`
- `raw/` directory exists with unprocessed files, OR `--seed` flag for initial population

## Modes

### Normal Mode (default)

Scan `~/contextuality/raw/` for files without a `.processed` sidecar.

### Seed Mode (`/kb-ingest --seed`)

One-time bootstrap. Read sources in-place from:
- `references/corpus/*.pdf` (16 reference papers)
- `paper/*.tex` (5 LaTeX papers)
- Optionally: external paths passed as arguments

After seeding, create `.processed` sidecars in `raw/` pointing to original locations.

## Process

For each unprocessed file:

1. **Read the file** based on type:
   - `.pdf` — Use Read tool (small PDFs ≤10 pages). For large PDFs, use `pdftotext` via Bash.
   - `.md` / `.txt` — Read directly.
   - `.tex` — Read directly. Focus on abstract, theorems, and key results.
   - `.py` — Read and identify: purpose, inputs, outputs, key algorithms.
   - `links.txt` — WebFetch each URL (one at a time per CLAUDE.md rules). Mark processed lines.

2. **Read existing `wiki/INDEX.md`** to understand what articles already exist and identify backlink targets.

3. **Generate a wiki article**:
   - Choose the correct category folder: `papers/` for papers, `concepts/` for theoretical topics, `computations/` for scripts, `people/` for researchers, `open-questions/` for conjectures.
   - Filename: lowercase, hyphen-separated, descriptive. Example: `buchanan-monroe-tqft-2025.md`
   - Use the template from `wiki/_templates/<type>.md` as the base structure.
   - Fill in all sections. Do not leave placeholders.
   - Add `[[backlinks]]` to existing wiki articles wherever concepts overlap. Use the exact filename without extension as the link target (e.g., `[[peres-33-3d]]`).
   - If a concept referenced doesn't have its own article yet, still link it — it becomes a candidate for future creation (red link in Obsidian).

4. **Check for duplicates**: If an article for this source already exists (check INDEX.md), skip and report "Already ingested: <filename>".

5. **Update `wiki/INDEX.md`**:
   - Add a line under the appropriate category: `- [[article-name]] — One-line summary`
   - Update the article count and last-updated date in the header.

6. **Create `.processed` sidecar**: Write a file named `<original-filename>.processed` in the same directory containing the timestamp and path to the generated wiki article.

## Output

Report to terminal:
```
Ingested 3 files:
  raw/contextual_TQFT.pdf → wiki/papers/buchanan-monroe-tqft-2025.md
  raw/notes-on-rigidity.md → wiki/concepts/rigidity-ks-sets.md
  raw/verify_peres33.py → wiki/computations/verify-peres33.md
Skipped 1 (already ingested):
  raw/old-paper.pdf
Unprocessed in raw/: 0
```

## Constraints

- NEVER modify existing wiki articles. Ingest only creates new ones.
- NEVER delete or move raw files.
- NEVER touch `docs/` or `paper/` directories.
- Process files one at a time. Do not batch PDF reads.
- WebFetch URLs one at a time (CLAUDE.md rule).
```

- [ ] **Step 3: Verify the skill is discoverable**

```bash
ls ~/.claude/skills/kb-ingest/SKILL.md
```

Expected: file exists.

- [ ] **Step 4: Commit**

```bash
cd ~/.claude && git add skills/kb-ingest/SKILL.md && git commit -m "feat: add /kb-ingest skill for contextuality knowledge base"
```

Note: This commits to the `claude-config` repo, not contextuality.

---

### Task 3: Create `/kb-query` Skill

**Files:**
- Create: `~/.claude/skills/kb-query/SKILL.md`

- [ ] **Step 1: Create the skill directory**

```bash
mkdir -p ~/.claude/skills/kb-query
```

- [ ] **Step 2: Write the skill file**

Write `~/.claude/skills/kb-query/SKILL.md`:

```markdown
---
name: kb-query
description: Query the contextuality knowledge base wiki. Use when user says "kb-query", "ask the wiki", "research question", or "query knowledge base". Do NOT use for ingesting or linting.
---

# KB Query

Ask questions against the contextuality knowledge base and get researched answers.

## Prerequisites

- Working directory or target: `~/contextuality/`
- `wiki/INDEX.md` exists and has been populated (run `/kb-ingest --seed` first if empty)

## Usage

```
/kb-query "What's the relationship between Peres-33 and cyclotomic constructions?"
/kb-query --save "List all KS sets with fewer than 40 vectors"
/kb-query --deep "What computational methods detect contextuality?"
```

## Modes

- **Default**: Answer in terminal, then ask "File this back into the wiki?"
- **`--save`**: Answer and auto-file to `wiki/outputs/` without asking.
- **`--deep`**: Also reads raw source files (PDFs, .tex, .py) beyond wiki summaries. Use for questions requiring primary source detail.

## Process

1. **Parse the question** from the user's argument string.

2. **Read `wiki/INDEX.md`** in full. Identify 3-8 articles most relevant to the question based on their one-line summaries.

3. **Read the relevant articles**. Extract claims, data, and connections.

4. **Follow backlinks** if the articles reference other wiki pages that would help answer the question. Read those too. Cap at 15 total articles to stay within context.

5. **Deep mode only**: If `--deep` flag is set, also read the original source files listed in article frontmatter (`source:` field). For PDFs, read up to 10 pages. For .tex files, focus on theorems and proofs.

6. **Synthesize an answer**:
   - Lead with a direct answer to the question.
   - Support with evidence from specific articles (cite them as `[[article-name]]`).
   - Note any contradictions or gaps found across articles.
   - If the question cannot be fully answered from the wiki, say what's missing.

7. **File back** (if default mode, ask first; if `--save`, do automatically):
   - Save to `wiki/outputs/YYYY-MM-DD-<slugified-question>.md`
   - Frontmatter: `date`, `type: query-output`, `question`
   - Body: the full synthesized answer with backlinks
   - Update `wiki/INDEX.md` under the Outputs section

## Output Format (Terminal)

```
## Answer

[Direct answer with [[backlinks]] to sources]

## Sources Consulted
- [[article-1]] — relevant point
- [[article-2]] — relevant point

## Gaps
- [anything the wiki doesn't cover that would help]

---
File this to wiki/outputs/? (y/n)
```

## Constraints

- Read INDEX.md first, always. Do not skip to reading random wiki files.
- Cap at 15 articles per query to manage context.
- Do not modify existing articles. Query is read-only (except filing outputs).
- WebFetch only in deep mode, only if a source URL is in the frontmatter.
```

- [ ] **Step 3: Commit**

```bash
cd ~/.claude && git add skills/kb-query/SKILL.md && git commit -m "feat: add /kb-query skill for contextuality knowledge base"
```

---

### Task 4: Create `/kb-lint` Skill

**Files:**
- Create: `~/.claude/skills/kb-lint/SKILL.md`

- [ ] **Step 1: Create the skill directory**

```bash
mkdir -p ~/.claude/skills/kb-lint
```

- [ ] **Step 2: Write the skill file**

Write `~/.claude/skills/kb-lint/SKILL.md`:

```markdown
---
name: kb-lint
description: Health check the contextuality knowledge base wiki. Use when user says "kb-lint", "check wiki health", "lint knowledge base", or "wiki consistency check". Do NOT use for ingesting or querying.
---

# KB Lint

Run health checks on the contextuality knowledge base wiki to find structural issues, inconsistencies, and improvement opportunities.

## Prerequisites

- Working directory or target: `~/contextuality/`
- `wiki/INDEX.md` exists and has been populated

## Process

### Phase 1: Structural Checks (always run)

1. **Orphan scan**: Glob all `.md` files in `wiki/` subdirectories. Compare against entries in `wiki/INDEX.md`. Report any files not listed in the index.

2. **Dead link scan**: Grep all `[[wiki-links]]` across wiki articles. For each unique link target, check if a corresponding `.md` file exists anywhere in `wiki/`. Report dead links with the file they appear in.

3. **Unprocessed raw files**: Scan `raw/` for files without a `.processed` sidecar. Report as "pending ingest".

4. **Stub detection**: Read each wiki article. If the body (excluding frontmatter) is fewer than 50 words, flag as a stub.

5. **INDEX.md integrity**: Verify the article count in the header matches the actual count of entries listed.

### Phase 2: Content Checks (run with `--deep` flag)

1. **Inconsistency scan**: Read all articles in a category (e.g., all `papers/`). Look for conflicting claims about the same entity (e.g., different vector counts for the same KS set, conflicting year attributions).

2. **Stale reference check**: Look for articles referencing conjectures or open questions. Cross-check against `wiki/open-questions/` — if any are marked `status: resolved`, flag articles still referencing them as open.

3. **Missing backlink scan**: For each pair of articles that share a concept keyword, check if they link to each other. Report missing bidirectional links.

### Phase 3: Suggestions (run with `--deep` flag)

1. **Red link candidates**: Collect all `[[links]]` that point to nonexistent articles. Rank by frequency. Suggest top 5 as new article candidates.

2. **Connection opportunities**: Identify articles in different categories that reference overlapping concepts but don't link to each other. Suggest links.

## Output

Report to terminal in sections:

```
## Structural Health

Orphan articles (in wiki/ but not in INDEX.md): 2
  - wiki/papers/old-draft.md
  - wiki/concepts/untitled.md

Dead links: 3
  - [[nonexistent-concept]] in wiki/papers/peres-33.md
  - [[missing-person]] in wiki/people/asher-peres.md
  - [[todo-article]] in wiki/concepts/contextuality.md

Unprocessed in raw/: 1
  - raw/new-paper.pdf

Stubs (<50 words): 1
  - wiki/computations/ks-sat.md

INDEX.md count: listed 42, actual 44 (MISMATCH)

## Summary
4 structural issues found. Run /kb-ingest to process 1 pending file.
```

With `--deep`:
```
## Content Issues
- Conflicting vector count for Conway-Kochen: papers/conway-kochen.md says 31, computations/ks-search.md says 33
- wiki/papers/old-paper.md references "open conjecture on 6|n" but open-questions/6n-conjecture.md is marked resolved

## Suggestions
- Top red link candidates: [[bell-inequality]] (referenced 4x), [[gleason-theorem]] (3x), [[csw-inequality]] (3x)
- Missing link: papers/cabello-2014.md and concepts/graph-contextuality.md both discuss CSW but don't link
```

## Saving

Ask: "Save this report to wiki/outputs/lint-YYYY-MM-DD.md?" If yes, save and update INDEX.md.

## Constraints

- NEVER auto-fix issues. Report only. User decides what to address.
- NEVER modify existing wiki articles or INDEX.md (except adding the lint report to outputs).
- Phase 2 and 3 read many files — warn user this may use significant context.
```

- [ ] **Step 3: Commit**

```bash
cd ~/.claude && git add skills/kb-lint/SKILL.md && git commit -m "feat: add /kb-lint skill for contextuality knowledge base"
```

---

### Task 5: Seed the Wiki with Existing Material

**Files:**
- Modify: `~/contextuality/wiki/INDEX.md`
- Create: multiple files in `wiki/papers/`, `wiki/concepts/`, `wiki/computations/`

This task is the big one — it populates the wiki from existing sources. It runs `/kb-ingest --seed`.

- [ ] **Step 1: Copy scattered external files into raw/**

```bash
cd ~/contextuality
cp ~/Documents/Tech-Docs/contextual_TQFT.pdf raw/
cp ~/claude-inbox/peer-reviews/contextuality-site-review-20260316.txt raw/
cp ~/claude-inbox/peer-reviews/contextuality-revision-oxford-review-20260329-210324.txt raw/
```

- [ ] **Step 2: Run `/kb-ingest --seed`**

Invoke the skill: `/kb-ingest --seed`

This will:
- Read all 16 PDFs in `references/corpus/`
- Read all 5 `.tex` papers in `paper/`
- Read the 3 files just copied to `raw/`
- Generate wiki articles for each
- Build out INDEX.md

Expected: ~24 new articles created (16 corpus + 5 papers + 3 external).

- [ ] **Step 3: Create core concept articles**

After seeding from sources, manually invoke `/kb-ingest` logic to create concept articles for foundational topics that span multiple papers. These are not sourced from a single file — they synthesize across the wiki:

Create articles for (at minimum):
- `wiki/concepts/kochen-specker-theorem.md`
- `wiki/concepts/contextuality.md`
- `wiki/concepts/algebraic-islands.md`
- `wiki/concepts/ks-set.md`
- `wiki/concepts/cyclotomic-fields.md`
- `wiki/concepts/graph-contextuality.md`
- `wiki/concepts/peres-33-3d.md`
- `wiki/concepts/csw-inequality.md`

Each should cross-reference the paper articles already created, using `[[backlinks]]`.

- [ ] **Step 4: Create computation articles for key scripts**

Create articles for the most important Python scripts:
- `wiki/computations/ks-islands.md` (from `ks_islands.py` — main survey script)
- `wiki/computations/ks-sat.md` (from `ks_sat.py` — SAT-based coloring solver)
- `wiki/computations/ks-complex.md` (from `ks_complex.py` — roots of unity analysis)
- `wiki/computations/ks-search.md` (from `ks_search.py` — randomized KS minimization)
- `wiki/computations/ks-geometry.md` (from `ks_geometry.py` — realizability gap)

- [ ] **Step 5: Verify INDEX.md is complete**

Read `wiki/INDEX.md` and confirm:
- All created articles are listed
- Article count in header matches actual count
- Each entry has a one-line summary
- Categories are properly organized

- [ ] **Step 6: Run `/kb-lint` to validate**

Invoke `/kb-lint` to check for structural issues after seeding:
- No orphan articles
- No dead links (or document the expected red links for future articles)
- No stubs

- [ ] **Step 7: Commit**

```bash
cd ~/contextuality && git add wiki/ raw/ && git commit -m "feat: seed contextuality knowledge base with existing papers, concepts, and computations"
```

---

### Task 6: Install Obsidian and Open the Vault

- [ ] **Step 1: Check if Obsidian is installed**

```bash
ls "/c/Users/Michael Kernaghan/AppData/Local/Obsidian/" 2>/dev/null && echo "Installed" || echo "Not installed"
```

- [ ] **Step 2: Install Obsidian if needed**

If not installed, open the download page:

```bash
start chrome "https://obsidian.md/download"
```

Download and install the Windows version.

- [ ] **Step 3: Open the wiki vault in Obsidian**

```bash
start "" "obsidian://open?vault=wiki&path=C:/Users/Michael Kernaghan/contextuality/wiki"
```

If this doesn't work (vault not registered), open Obsidian manually and select "Open folder as vault" → navigate to `C:\Users\Michael Kernaghan\contextuality\wiki\`.

- [ ] **Step 4: Verify graph view**

In Obsidian, press `Ctrl+G` to open the graph view. Confirm:
- Nodes appear for all wiki articles
- `[[backlinks]]` show as edges between nodes
- Clicking a node opens the article

- [ ] **Step 5: Commit Obsidian config (excluding workspace)**

```bash
cd ~/contextuality && git add wiki/.obsidian/app.json && git commit -m "feat: add Obsidian vault config for contextuality wiki"
```

---

### Task 7: Smoke Test the Full Workflow

- [ ] **Step 1: Test ingest — drop a new file and process it**

Copy the Buchanan-Monroe TQFT paper (already in raw/ from Task 5) or find a new PDF. If already processed, create a small test file:

```bash
echo "# Test Note\n\nThe Peres-33 set is the smallest known KS set in 3 dimensions with 33 vectors." > ~/contextuality/raw/test-note.md
```

Run `/kb-ingest`. Verify:
- `wiki/concepts/` or `wiki/papers/` gets a new article
- `INDEX.md` is updated
- `raw/test-note.md.processed` exists

- [ ] **Step 2: Test query**

Run: `/kb-query "What is the smallest known KS set in 3 dimensions?"`

Verify:
- The answer references Peres-33 and cites wiki articles
- The "file back" prompt appears
- If filed, `wiki/outputs/` gets a new article and INDEX.md updates

- [ ] **Step 3: Test lint**

Run: `/kb-lint`

Verify:
- Structural report appears
- No false positives on the articles we just created
- Dead links (red links) are reported correctly

- [ ] **Step 4: Verify in Obsidian**

Refresh Obsidian (`Ctrl+R` or reopen). Check:
- New articles from ingest appear in the file tree
- Graph view shows new connections
- Backlinks panel shows incoming links

- [ ] **Step 5: Clean up test file if desired**

The test note can stay or be removed — it's harmless.

- [ ] **Step 6: Final commit**

```bash
cd ~/contextuality && git add wiki/ raw/ && git commit -m "test: verify kb-ingest, kb-query, and kb-lint workflow"
```
