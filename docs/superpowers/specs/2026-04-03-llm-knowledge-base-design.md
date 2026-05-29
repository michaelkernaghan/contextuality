# LLM Knowledge Base for Contextuality Research

**Date:** 2026-04-03
**Status:** Design approved
**Inspired by:** Karpathy's LLM knowledge base pattern (Obsidian + LLM-maintained markdown wiki)

## Overview

A self-maintaining markdown knowledge base for the contextuality research project. Raw source materials (papers, articles, notes, scripts) are ingested by the LLM into a structured wiki with backlinks, auto-maintained indexes, and cross-references. The wiki is browsable in Obsidian (graph view, backlinks) and queryable via Claude Code skills.

Three skills drive the system:
- `/kb-ingest` — process raw sources into wiki articles
- `/kb-query` — ask questions across the knowledge base
- `/kb-lint` — health checks and consistency validation

## Directory Structure

```
contextuality/
├── raw/                    # Drop zone for unprocessed sources
│   └── links.txt           # Optional: URLs to fetch and ingest
├── wiki/                   # Obsidian vault — LLM-maintained knowledge base
│   ├── .obsidian/          # Obsidian config
│   ├── INDEX.md            # Auto-maintained master index
│   ├── concepts/           # Core concepts (contextuality, KS theorem, etc.)
│   ├── papers/             # Summaries of papers (ours + external)
│   ├── people/             # Researcher profiles
│   ├── computations/       # Script documentation and result summaries
│   ├── open-questions/     # Research questions and conjectures
│   ├── outputs/            # Q&A results, generated reports filed back in
│   └── _templates/         # Templates for each article type
├── docs/                   # (existing) MkDocs public site — unchanged
├── references/corpus/      # (existing) reference PDFs — unchanged
├── paper/                  # (existing) LaTeX papers — unchanged
└── ...
```

Key constraints:
- `raw/` is append-only. Originals are never deleted or moved. A `.processed` sidecar marks completion.
- `wiki/` uses `[[wiki-links]]` for Obsidian compatibility.
- `docs/` and `paper/` are never touched by these skills.
- `INDEX.md` is the LLM's primary navigation aid — categorized list of every article with one-line summaries.

## Skill 1: `/kb-ingest`

### Trigger
Run manually after dropping files into `raw/`.

### Process
1. Scan `raw/` for files without a `.processed` sidecar.
2. Extract content based on file type:
   - `.pdf` → text extraction (Read tool for small PDFs, `pdftotext` for large)
   - `.md` / `.txt` → read directly
   - `.tex` → read directly
   - `.py` → read and summarize purpose, inputs, outputs
   - URLs in `raw/links.txt` → WebFetch each, mark processed lines
3. Generate a wiki article for each source:
   - File placed in appropriate category folder (`papers/`, `concepts/`, etc.)
   - Filename: slugified title (e.g., `buchanan-monroe-tqft-2025.md`)
   - Frontmatter: `source`, `date_ingested`, `type`
   - Body: structured summary, key claims, relevance to our work, open questions
   - `[[backlinks]]` to existing wiki articles where concepts overlap
4. Update `INDEX.md` with new entry and one-line summary.
5. Create `.processed` sidecar for each raw file (contains timestamp).

### Article Template

```markdown
---
source: raw/filename.pdf
date_ingested: 2026-04-03
type: paper
---

# Title (Author, Year)

## Summary
[2-3 paragraph summary]

## Key Claims
- [bulleted list]

## Methods
- [if applicable]

## Relevance to Our Work
- Links to [[concept-a]], [[concept-b]]
- [how this connects to our research program]

## Open Questions
- [anything worth investigating further]
```

### Constraints
- Ingest only creates new articles. It does not modify existing wiki articles.
- If an article for the same source already exists, skip and report.
- Never delete or move raw files.

## Skill 2: `/kb-query`

### Trigger
Run with a natural language question: `/kb-query "What's the relationship between Peres-33 and cyclotomic constructions?"`

### Process
1. Read `INDEX.md` to identify relevant articles (typically 3-8).
2. Read the relevant articles.
3. If needed, follow `[[backlinks]]` to pull in connected articles.
4. Synthesize an answer in the terminal.
5. Ask: "File this back into the wiki?" If yes:
   - Save to `wiki/outputs/YYYY-MM-DD-slug.md`
   - Update `INDEX.md`

### Modes
- Default: answer in terminal, offer to file back
- `--save`: auto-file without asking
- `--deep`: also reads raw source files (PDFs, .tex, .py), not just wiki summaries

### Scalability
At ~100 articles with one-line summaries, `INDEX.md` is ~5-10K tokens — easily scannable. If the wiki grows past ~500 articles, add category-level sub-indexes (`concepts/INDEX.md`, `papers/INDEX.md`) and the skill reads the top-level index to pick which sub-indexes to drill into.

## Skill 3: `/kb-lint`

### Trigger
Run periodically (weekly, or before paper submission).

### Structural Checks
- Orphan articles (in wiki but not in `INDEX.md`)
- Dead links (`[[broken-reference]]` pointing to nonexistent articles)
- Unprocessed files in `raw/`
- Empty or stub articles

### Content Checks
- Inconsistent claims across articles (e.g., conflicting vector counts)
- Stale data (articles referencing conjectures since resolved)
- Missing backlinks (two articles discuss the same concept but don't link)

### Suggestions
- New article candidates (concepts mentioned in multiple articles with no dedicated page)
- Research questions worth investigating (connections across articles)

### Output
Report in terminal. Optionally saved to `wiki/outputs/lint-YYYY-MM-DD.md`. Does NOT auto-fix — reports issues for human decision.

### Implementation Priority
Initial version: structural checks only. Content checks and suggestions added later.

## Obsidian Setup

- Vault path: `~/contextuality/wiki/`
- No plugins required initially — core Obsidian provides graph view, backlinks, `[[wiki-links]]`
- Optional later: Marp (slides), Dataview (metadata queries), Canvas (spatial layouts)

## Ownership Model

| Component | Owner | Notes |
|-----------|-------|-------|
| Wiki articles | LLM | LLM writes, maintains, and links all articles |
| INDEX.md | LLM | Auto-maintained, never edited manually |
| raw/ files | User | User drops files here |
| Obsidian browsing | User | User explores graph, reads articles |
| docs/ (MkDocs) | User | Manual curation for public site, separate from wiki |

The wiki is the LLM's domain. The user rarely edits articles directly. If they do, the LLM respects existing content during linting.

## MkDocs Relationship

Completely separate. To promote a wiki article to the public site, manually copy/adapt into `docs/`. No automation — the wiki is messy research notes, `docs/` is polished publication.

## Initial Seeding

Before the skills are useful, the wiki needs a bootstrap population from existing material:
1. Ingest the 16 PDFs in `references/corpus/` (already indexed in `CORPUS-INDEX.md`)
2. Ingest the 5 LaTeX papers from `paper/`
3. Ingest the scattered files found outside the repo (TQFT paper, peer reviews)
4. Create concept articles for core topics already documented in `docs/`
5. Create computation articles for the key Python scripts

For seeding, the ingest skill reads these sources in-place (no need to copy to `raw/`). The skill accepts a `--seed` flag that scans `references/corpus/`, `paper/`, and a provided list of external paths. After seeding, normal operation uses `raw/` exclusively.

## Future Enhancements (Not In Scope)

- Semantic search tool over the wiki (Python CLI, handed to LLM)
- Structured outputs: Marp slides, matplotlib plots filed back into wiki
- Auto-sync between wiki and MkDocs for selected articles
- Fine-tuning on the knowledge base
