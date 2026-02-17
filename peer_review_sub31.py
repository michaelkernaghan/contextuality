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

# Read API key
with open(r"E:\Blockchain-Backups\Keystores\API-Keys\api-keys-master.txt", "r") as f:
    key_text = f.read()
import re as re2
match = re2.search(r"OpenAI.*?:\s*(sk-[^\s]+)", key_text)
if match:
    api_key = match.group(1)
else:
    # Fallback to hardcoded key from template
    raise ValueError("OpenAI API key not found in api-keys-master.txt")

prompt = """You are an expert peer reviewer in quantum foundations, contextuality theory, and mathematical physics.

Please provide a detailed peer review of this paper. The paper reports a systematic computational search for Kochen-Specker sets with fewer than 31 vectors in dimension 3.

Structure your review as:
1. Summary (2-3 sentences)
2. Strengths (bulleted)
3. Weaknesses (bulleted)
4. Methodology Assessment (are the six strategies well-designed and comprehensive?)
5. The norm-2 / cancellation identity finding (is the observation that {0,+-1,+-3} fails significant?)
6. Novelty Assessment (is this publishable? what does it add to the field?)
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
    f.write("Focus: All areas\n")
    f.write("---\n\n")
    f.write(review_text)

print(f"Review saved to: {outpath}")
print("---")
print(review_text)
