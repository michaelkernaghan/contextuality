from pathlib import Path

pages = [
    ("Site Index", "docs/index.md"),
    ("Research Overview", "docs/research/index.md"),
    ("The Six Algebraic Islands", "docs/research/algebraic-islands.md"),
    ("Research Papers", "docs/research/papers.md"),
    ("Eisenstein 33-Vector KS Set", "docs/ks-sets/eisenstein-33-3d.md"),
    ("Heegner-7 43-Vector KS Set", "docs/ks-sets/heegner7-43-3d.md"),
    ("Golden Ratio 52-Vector KS Set", "docs/ks-sets/golden-52-3d.md"),
    ("Z[sqrt(-2)] 33-Vector KS Set", "docs/ks-sets/zsqrt2-neg-33-3d.md"),
    ("Conway-Kochen 31 (updated)", "docs/ks-sets/conway-kochen-31-3d.md"),
    ("Peres 33 (updated)", "docs/ks-sets/peres-33-3d.md"),
    ("Michael Kernaghan (updated)", "docs/people/michael-kernaghan.md"),
    ("Bibliography (updated)", "docs/bibliography.md"),
    ("Recent Papers (updated)", "docs/recent-papers.md"),
]

header = """# Contextuality & KS Set Atlas — Full Site Review Bundle

This document bundles all key pages of the Contextuality & KS Set Atlas website
(https://contextuality.netlify.app/) for peer review. The site documents Kochen-Specker
sets, quantum contextuality, and recent 2026 research discovering six algebraic islands
that classify all KS-producing number rings in dimension 3.

"""

parts = [header]
for i, (title, path) in enumerate(pages, 1):
    content = Path(path).read_text(encoding="utf-8")
    parts.append(f"\n{'='*80}\n# PAGE {i}: {title}\n# Source: {path}\n{'='*80}\n\n{content}\n")

bundle = "\n".join(parts)
Path("site_review_bundle.md").write_text(bundle, encoding="utf-8")
words = len(bundle.split())
print(f"Bundle: {len(pages)} pages, {words} words, {len(bundle)} chars")
