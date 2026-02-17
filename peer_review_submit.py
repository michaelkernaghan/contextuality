"""Send algebraic_islands.tex to GPT-5.2 Pro for peer review."""
import requests
import re
import sys
from datetime import datetime

# Read the paper
with open(r"C:\Users\Michael Kernaghan\contextuality\paper\algebraic_islands.tex", "r", encoding="utf-8") as f:
    tex = f.read()

# Strip LaTeX commands for readability
text = tex
# Remove preamble
text = re.sub(r"\\documentclass.*?\\begin\{document\}", "", text, flags=re.DOTALL)
text = re.sub(r"\\end\{document\}", "", text)
# Strip common formatting commands
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

raise ValueError("OpenAI API key not found in api-keys-master.txt")

prompt = """You are an expert peer reviewer in quantum foundations, contextuality theory, and mathematical physics.

Please provide a detailed peer review of this paper with SPECIAL FOCUS on:
1. The trigonometric parametrization (Section 7.3) - using cos^2(theta) + sin^2(theta) = 1 as a cancellation mechanism to sweep over angle space and show KS-uncolorability is measure-zero. Is this a genuine contribution? Does the finding that all uncolorable angles reduce to known islands strengthen the six-island classification?
2. The BPQS (Bipartite Perfect Quantum Strategy) results - SAT-based computation of B-KS input counts for all six islands, verifying Cabello's three known results and extending to three new islands (Heegner-7, Golden, Z[sqrt(-2)]).
3. Overall novelty - is discovering six algebraic islands, classifying them, and providing the trigonometric completeness argument sufficiently novel for publication?
4. The paper's positioning relative to Cabello, Trandafir, Li-Bright-Ganesh, and Cortez-Morales-Reyes.

Structure your review as:
1. Summary (2-3 sentences)
2. Strengths (bulleted)
3. Weaknesses (bulleted)
4. Trigonometric Parametrization Assessment (detailed)
5. BPQS Contribution Assessment (detailed)
6. Novelty Assessment (detailed)
7. Specific Suggestions for Improvement
8. Minor Issues
9. Overall Recommendation (Accept / Minor Revision / Major Revision / Reject) with justification

Be honest and critical. Do not inflate the contribution."""

response = requests.post(
    "https://api.openai.com/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    },
    json={
        "model": "gpt-5.2",
        "max_completion_tokens": 8000,
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"Paper text:\n\n{text}"},
        ],
    },
    timeout=300,
)

if response.status_code != 200:
    print(f"ERROR: {response.status_code}")
    print(response.text[:500])
    sys.exit(1)

result = response.json()
review_text = result["choices"][0]["message"]["content"]

# Save
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
outpath = f"C:/Users/Michael Kernaghan/claude-inbox/peer-reviews/algebraic_islands-review-{timestamp}.txt"
with open(outpath, "w", encoding="utf-8") as f:
    f.write("Peer Review: The Algebraic Landscape of Kochen-Specker Sets in Dimension Three\n")
    f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("Reviewer: GPT-5.2 Pro (via OpenAI API)\n")
    f.write("Focus: BPQS contribution and overall novelty\n")
    f.write("---\n\n")
    f.write(review_text)

print(f"Review saved to: {outpath}")
print("---")
print(review_text)
