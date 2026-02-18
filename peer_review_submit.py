"""Send algebraic_islands.tex to GPT-5.2 for peer review."""
import requests
import re
import sys
from datetime import datetime
from pathlib import Path

# Read API key
api_key = None
for line in Path(r"E:\Blockchain-Backups\Keystores\API-Keys\api-keys-master.txt").read_text(encoding="utf-8").splitlines():
    if line.strip().startswith("API Key: sk-proj-"):
        api_key = line.strip().split("API Key: ")[1]
        break

if not api_key:
    print("ERROR: Could not find OpenAI API key")
    sys.exit(1)

print(f"API key: {api_key[:25]}...")

# Read the paper
with open(r"C:\Users\Michael Kernaghan\contextuality\paper\algebraic_islands.tex", "r", encoding="utf-8") as f:
    tex = f.read()

# Strip LaTeX commands for readability
text = tex
text = re.sub(r"\\documentclass.*?\\begin\{document\}", "", text, flags=re.DOTALL)
text = re.sub(r"\\end\{document\}", "", text)
for cmd in ["textbf", "textit", "emph", "texttt", "mathrm", "mathbb", "mathcal"]:
    pattern = "\\\\" + cmd + r"\{([^}]*)\}"
    text = re.sub(pattern, r"\1", text)
text = re.sub(r"\\cite\{[^}]*\}", "[ref]", text)
text = re.sub(r"\\ref\{[^}]*\}", "[ref]", text)
text = re.sub(r"\\label\{[^}]*\}", "", text)
text = re.sub(r"\\url\{([^}]*)\}", r"\1", text)
text = re.sub(r"\\\\", " ", text)
text = re.sub(r"\n{3,}", "\n\n", text)

# Truncate if too long
if len(text) > 60000:
    text = text[:60000] + "\n\n[TRUNCATED]"

word_count = len(text.split())
print(f"Extracted {word_count} words from LaTeX ({len(text)} chars)")

prompt = """You are an expert peer reviewer in quantum foundations, contextuality theory, algebraic number theory, and computational mathematics.

Please provide a detailed peer review of this paper. The paper investigates which algebraic number fields support Kochen-Specker (KS) constructions in dimension 3, identifying six discrete algebraic islands controlled by cancellation identities.

Key claims to evaluate:
- Generator norm <= 2 controls KS-uncolorability (norm-2 and phase cancellation mechanisms)
- Six discrete algebraic islands, two newly discovered (Heegner-7 and golden ratio)
- Two-element alphabet completeness result (all cancellation identities enumerated)
- The trivial alphabet {0,+/-1} generates only 13 rays (too few for KS), establishing 1+1=2 as the minimal useful cancellation
- Density trend: simpler identities produce denser structures and smaller KS sets
- Discrete cancellation landscape with no intermediate steps between 13 and 49 rays
- Connection to Li-Bright-Ganesh realizability program (algebraic constraints as filter pipeline)
- Exotic untested candidates: cubic Pisot numbers, class-number > 1 fields, CM curves

Structure your review as:
1. Summary (2-3 sentences)
2. Strengths (bulleted)
3. Weaknesses (bulleted)
4. Novelty Assessment (detailed)
5. Rigor Assessment (detailed)
6. Completeness Assessment (detailed, including the exotic candidates discussion)
7. Specific Suggestions for Improvement
8. Minor Issues
9. Overall Recommendation (Accept / Minor Revision / Major Revision / Reject) with justification

Be honest and critical. Do not inflate the contribution."""

print("Submitting to GPT-5.2...")

response = requests.post(
    "https://api.openai.com/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    },
    json={
        "model": "gpt-5.2",
        "max_completion_tokens": 6000,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Paper text:\n\n{text}"},
        ],
    },
    timeout=300,
)

if response.status_code != 200:
    print(f"ERROR: {response.status_code}")
    print(response.text[:1000])
    sys.exit(1)

result = response.json()
review_text = result["choices"][0]["message"]["content"]
usage = result.get("usage", {})
print(f"Tokens: {usage.get('total_tokens', 'unknown')}")

# Save
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
outdir = Path(r"C:\Users\Michael Kernaghan\claude-inbox\peer-reviews")
outdir.mkdir(parents=True, exist_ok=True)
outpath = outdir / f"algebraic_islands-review-{timestamp}.txt"

with open(outpath, "w", encoding="utf-8") as f:
    f.write("Peer Review: The Algebraic Landscape of Kochen-Specker Sets in Dimension Three\n")
    f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Reviewer: GPT-5.2 (via OpenAI API)\n")
    f.write(f"Tokens: {usage.get('total_tokens', 'unknown')}\n")
    f.write("---\n\n")
    f.write(review_text)

print(f"\nReview saved to: {outpath}")
print(f"\n{'='*60}")
print(review_text)
