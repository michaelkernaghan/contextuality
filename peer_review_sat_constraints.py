"""Send sub31_letter.tex to GPT-5.2 for peer review."""
import requests
import re
import sys
from datetime import datetime

# Read the paper
with open(r"C:\Users\Michael Kernaghan\contextuality\paper\sub31_letter.tex", "r", encoding="utf-8") as f:
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

if len(text) > 60000:
    text = text[:60000] + "\n\n[TRUNCATED]"

import os
api_key = os.environ.get("OPENAI_API_KEY", "")
if not api_key:
    # Fall back to key file
    with open(r"E:\Blockchain-Backups\Keystores\API-Keys\api-keys-master.txt") as kf:
        for line in kf:
            if "openai" in line.lower() and "sk-" in line:
                api_key = line.strip().split()[-1]
                break
if not api_key:
    print("ERROR: No OpenAI API key found. Set OPENAI_API_KEY or check api-keys-master.txt")
    sys.exit(1)

prompt = """You are an expert peer reviewer in quantum foundations, SAT solving, combinatorial optimization, and mathematical physics. You are reviewing a 4-page letter reporting computational evidence for the optimality of Conway-Kochen's 31-vector KS set.

Please provide a detailed peer review with focus on:
1. Whether the computational methodology is sound and the strategies are complementary
2. Whether the finite pool SAT encoding (C4a-C4c) is correct and the claimed results credible
3. Whether the norm-2 boundary claim and density trend arguments are well-supported
4. Whether the criticality results (exhaustive k<=8, sampled k<=12) are convincing
5. Whether the vertex-merging experiment and its implications are clearly explained
6. Whether the proposed integration with the Li-Bright-Ganesh pipeline is well-motivated
7. Whether the distinction between proven and empirical constraints is clearly communicated
8. Overall coherence, positioning, and contribution level

Structure your review as:
1. Summary (2-3 sentences)
2. Strengths (bulleted)
3. Weaknesses (bulleted)
4. Methodology Assessment (are the six strategies sound and complementary?)
5. SAT Encoding and Realizability Assessment (is the finite pool encoding correct and useful?)
6. Novelty and Contribution Assessment
7. Specific Suggestions for Improvement
8. Minor Issues
9. Overall Recommendation (Accept / Minor Revision / Major Revision / Reject) with justification

Be honest and critical. Do not inflate the contribution."""

print("Sending to GPT-5.2 for peer review...")
print(f"Document length: {len(text)} chars")

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
    print(response.text[:1000])
    sys.exit(1)

result = response.json()
review_text = result["choices"][0]["message"]["content"]

# Save
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
outpath = f"C:/Users/Michael Kernaghan/claude-inbox/peer-reviews/sub31_letter-review-{timestamp}.txt"
with open(outpath, "w", encoding="utf-8") as f:
    f.write("Peer Review: Computational evidence for the optimality of CK-31\n")
    f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("Reviewer: GPT-5.2 (via OpenAI API)\n")
    f.write("Focus: SAT encoding correctness, finite pool realizability, novelty\n")
    f.write("---\n\n")
    f.write(review_text)

print(f"\nReview saved to: {outpath}")
print("---")
print(review_text)
