"""Send a LaTeX paper to GPT-5.4-pro for Oxford-style challenge review.

Usage: python oxford_review.py <path_to_tex_file>
"""
import re
import sys
import requests
from datetime import datetime
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: python oxford_review.py <path_to_tex_file>")
    sys.exit(1)

file_path = Path(sys.argv[1])
if not file_path.exists():
    print(f"ERROR: File not found: {file_path}")
    sys.exit(1)

# Read API key
api_key = None
for line in Path(r"E:\Blockchain-Backups\Keystores\API-Keys\api-keys-master.txt").read_text(encoding="utf-8").splitlines():
    if "sk-svcacct-" in line:
        for part in line.strip().split():
            if part.startswith("sk-svcacct-"):
                api_key = part
                break
        if api_key:
            break

if not api_key:
    print("ERROR: Could not find OpenAI service account API key")
    sys.exit(1)

print(f"API key: {api_key[:30]}...")

# Read and clean LaTeX
tex = file_path.read_text(encoding="utf-8")
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

if len(text) > 80000:
    text = text[:80000] + "\n\n[TRUNCATED]"

word_count = len(text.split())
print(f"File: {file_path.name} ({word_count} words, {len(text)} chars)")

prompt = """You are conducting an Oxford-style challenge review of a research paper in quantum foundations and algebraic combinatorics. Complete ALL THREE steps thoroughly:

STEP 1 — HOSTILE EXAMINER:
What are the 3 weakest logical jumps in this reasoning? Where would a hostile examiner attack first? Look for:
- Implicit assumptions that aren't stated
- Terse proofs where the reader has to fill gaps
- Rhetorical moves that overstate connections between results

STEP 2 — LITERATURE CHECK:
What claims in this argument contradict or oversimplify what cited authors actually found? Check:
- Do citations say what the authors claim they say?
- Are result types conflated (e.g., computational evidence treated as proof)?
- Are referenced results published/accessible?

STEP 3 — PHILOSOPHY OF SCIENCE:
What would a philosopher of science say is missing? What assumptions are undefended?
- Is this a universal result or specific to their parameterization?
- Are lemmas being oversold as phenomena?
- Does the sufficiency proof illuminate or just inherit from a known result?

OUTPUT: Produce a table of actionable items with columns: Priority (High/Medium/Low), Step (1/2/3), Issue, and Suggested Fix.

THE PAPER:

"""

print("Sending to GPT-5.4-pro via Responses API...")

response = requests.post(
    "https://api.openai.com/v1/responses",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    },
    json={
        "model": "gpt-5.4-pro",
        "input": prompt + text,
    },
    timeout=600,
)

if response.status_code != 200:
    print(f"ERROR: API returned {response.status_code}")
    print(response.text[:2000])
    sys.exit(1)

data = response.json()

# Extract output text
review = ""
for item in data.get("output", []):
    if item.get("type") == "message":
        for content_block in item.get("content", []):
            if content_block.get("type") == "output_text":
                review += content_block.get("text", "")

if not review:
    import json
    print("WARNING: No review text found. Raw response:")
    print(json.dumps(data, indent=2)[:3000])
    sys.exit(1)

usage = data.get("usage", {})

# Save to file FIRST (before printing — Windows encoding crash prevention)
stem = file_path.stem
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
outpath = Path(r"C:\Users\Michael Kernaghan\claude-inbox\peer-reviews") / f"{stem}-oxford-gpt54-{timestamp}.txt"
outpath.parent.mkdir(parents=True, exist_ok=True)
with open(outpath, "w", encoding="utf-8") as f:
    f.write(f"Oxford Challenge Review: {file_path.name}\n")
    f.write(f"Date: {datetime.now().isoformat()}\n")
    f.write(f"Reviewer: GPT-5.4-pro (Oxford 3-step method)\n")
    f.write(f"Tokens: {usage.get('input_tokens', '?')} input, {usage.get('output_tokens', '?')} output\n")
    f.write(f"{'='*80}\n\n")
    f.write(review)

print(f"\nTokens: {usage.get('input_tokens', '?')} input, {usage.get('output_tokens', '?')} output")
print(f"Review saved to: {outpath}")

# Print with safe encoding
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
print(f"\n{'='*80}")
print(review)
print(f"{'='*80}")
