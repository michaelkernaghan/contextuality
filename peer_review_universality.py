"""Send universality_letter.tex to GPT-5.2 for peer review."""

import requests
import json
import re
from datetime import datetime
from pathlib import Path

import re as _re
with open(r"E:\Blockchain-Backups\Keystores\API-Keys\api-keys-master.txt") as _f:
    _m = _re.search(r"OpenAI.*?:\s*(sk-[^\s]+)", _f.read())
API_KEY = _m.group(1) if _m else (_ for _ in ()).throw(ValueError("OpenAI key not found"))

# Read the paper
tex_path = Path("paper/universality_letter.tex")
tex_content = tex_path.read_text(encoding="utf-8")

# Strip LaTeX commands for readability but keep structure
def strip_latex(text):
    text = re.sub(r'\\documentclass.*?\n', '', text)
    text = re.sub(r'\\usepackage.*?\n', '', text)
    text = re.sub(r'\\newcommand.*?\n', '', text)
    text = re.sub(r'\\begin\{document\}', '', text)
    text = re.sub(r'\\end\{document\}', '', text)
    text = re.sub(r'\\maketitle', '', text)
    text = re.sub(r'\\begin\{abstract\}', '\nABSTRACT:', text)
    text = re.sub(r'\\end\{abstract\}', '\n', text)
    text = re.sub(r'\\section\{([^}]+)\}', r'\n## \1\n', text)
    text = re.sub(r'\\subsection\{([^}]+)\}', r'\n### \1\n', text)
    text = re.sub(r'\\textbf\{([^}]+)\}', r'**\1**', text)
    text = re.sub(r'\\emph\{([^}]+)\}', r'*\1*', text)
    text = re.sub(r'\\cite\{[^}]+\}', '[ref]', text)
    text = re.sub(r'\\label\{[^}]+\}', '', text)
    text = re.sub(r'\\ref\{[^}]+\}', '[ref]', text)
    text = re.sub(r'\\title\{([^}]+)\}', r'TITLE: \1', text)
    text = re.sub(r'\\author\{([^}]+)\}', r'AUTHOR: \1', text)
    text = re.sub(r'\\affiliation\{([^}]+)\}', r'AFFILIATION: \1', text)
    text = re.sub(r'\\begin\{(table|figure)\}.*?\\end\{(table|figure)\}', '[TABLE/FIGURE]', text, flags=re.DOTALL)
    text = re.sub(r'\\begin\{acknowledgments\}', '\n## Acknowledgments\n', text)
    text = re.sub(r'\\end\{acknowledgments\}', '', text)
    text = re.sub(r'\\begin\{thebibliography\}.*?\\end\{thebibliography\}', '[REFERENCES]', text, flags=re.DOTALL)
    return text.strip()

readable = strip_latex(tex_content)

prompt = f"""You are a referee for Physical Review Letters. Please provide a detailed peer review of the following manuscript. The paper reports two main results: (1) that a single algebraic invariant (generator norm <= 2) controls KS-uncolorability across all tested number fields in dimension 3, and (2) that every construction achieving the minimum of 31 rays produces the same orthogonality graph (graph universality of CK-31).

Evaluate:
1. **Academic Rigor**: Are claims properly supported? Is the methodology sound? Are there logical gaps?
2. **Novelty**: Is the norm-2 boundary genuinely new? Is graph universality a significant finding?
3. **Completeness**: What is missing? Are there obvious experiments or comparisons not performed?
4. **Significance for PRL**: Does this meet PRL's standard of broad interest and significant advance? Or is it better suited to PRA?
5. **Writing Quality**: Is the paper clear, well-structured, and at appropriate length for PRL?
6. **Technical Issues**: Any mathematical errors, unsupported claims, or questionable assumptions?
7. **Specific Suggestions**: Numbered list of concrete improvements.

Overall recommendation: Accept / Minor Revision / Major Revision / Reject (with reasoning).

Note: The author (Michael Kernaghan) published the 20-vector KS result in 1994 (J. Phys. A) and the 36-vector 8-dimensional result with Peres in 1995 (Phys. Lett. A), so has a track record in this area. A companion paper on new KS sets from Heegner-7 and golden ratio fields is being prepared separately.

MANUSCRIPT:

{readable}

FULL LATEX (for reference on tables and equations):

{tex_content}
"""

print("Sending universality_letter.tex to GPT-5.2 for peer review...")
response = requests.post(
    "https://api.openai.com/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    },
    json={
        "model": "gpt-5.2",
        "messages": [
            {"role": "system", "content": "You are an expert referee for Physical Review Letters, specializing in quantum foundations, contextuality, and graph theory."},
            {"role": "user", "content": prompt},
        ],
        "max_completion_tokens": 4000,
        "temperature": 0.3,
    },
    timeout=120,
)

if response.status_code != 200:
    print(f"API Error {response.status_code}: {response.text}")
    exit(1)

result = response.json()
review_text = result["choices"][0]["message"]["content"]

# Save the review
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
review_dir = Path(r"C:\Users\Michael Kernaghan\claude-inbox\peer-reviews")
review_dir.mkdir(parents=True, exist_ok=True)
review_path = review_dir / f"universality_letter-review-{timestamp}.txt"

header = f"""Peer Review: Graph universality of CK-31 and the norm-2 boundary
Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Reviewer: GPT-5.2 (via OpenAI API)
Model: gpt-5.2

---

"""

review_path.write_text(header + review_text, encoding="utf-8")
print(f"\nReview saved to: {review_path}")
print(f"\nUsage: {result.get('usage', {})}")
print("\n" + "=" * 70)
print(review_text)
