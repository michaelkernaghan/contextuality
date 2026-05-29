"""Send galois_letter.tex to GPT-5.4-pro for Oxford-style aggressive peer review."""
import requests
import re
import sys
import json
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
tex_path = Path(r"C:\Users\Michael Kernaghan\contextuality\paper\galois_letter.tex")
tex = tex_path.read_text(encoding="utf-8")

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

word_count = len(text.split())
print(f"Extracted {word_count} words from LaTeX ({len(text)} chars)")

# Read the review bundle as the prompt
review_bundle_path = Path(r"C:\Users\Michael Kernaghan\claude-inbox\galois-letter-review-v6.md")
prompt = review_bundle_path.read_text(encoding="utf-8") + "\n\nTHE PAPER:\n\n"

print("Sending to GPT-5.4-pro for Oxford-style review...")
print("(This may take 3-5 minutes)")

response = requests.post(
    "https://api.openai.com/v1/responses",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    },
    json={
        "model": "gpt-5.4-pro",
        "input": prompt + text,
        "max_output_tokens": 40000,
        "reasoning": {"effort": "medium"},
    },
    timeout=1800,
)

if response.status_code != 200:
    print(f"ERROR: API returned {response.status_code}")
    print(response.text[:1000])
    sys.exit(1)

data = response.json()

# Extract review text from Responses API format
review = data.get("output_text", "")
if not review:
    for item in data.get("output", []):
        if item.get("type") == "message":
            for content_block in item.get("content", []):
                if content_block.get("type") == "output_text":
                    review += content_block.get("text", "")
if not review:
    review = json.dumps(data, indent=2)[:3000] + "\n\n(Could not extract review text)"

usage = data.get("usage", {})
print(f"\nTokens: {usage.get('input_tokens', '?')} input, {usage.get('output_tokens', '?')} output")

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
print(f"\n{'='*80}")
print(review)
print(f"{'='*80}")

# Save review
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
outpath = Path(r"C:\Users\Michael Kernaghan\claude-inbox\peer-reviews") / f"galois_letter-oxford-review-{timestamp}.txt"
outpath.parent.mkdir(parents=True, exist_ok=True)
with open(outpath, "w", encoding="utf-8") as f:
    f.write(f"Oxford-Style Peer Review: Galois-Theoretic KS Classification\n")
    f.write(f"Date: {datetime.now().isoformat()}\n")
    f.write(f"Reviewer: GPT-5.4-pro (via OpenAI Responses API) — Round 6\n")
    f.write(f"Tokens: {usage.get('input_tokens', '?')} input, {usage.get('output_tokens', '?')} output\n")
    f.write(f"{'='*80}\n\n")
    f.write(review)

print(f"\nReview saved to: {outpath}")
