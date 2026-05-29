"""Send galois_letter.tex to Gemini 2.5 Pro for Oxford-style aggressive peer review."""
import re
import sys
import json
from datetime import datetime
from pathlib import Path

import google.generativeai as genai

# Read API key from master keystore
api_key = None
for line in Path(r"E:\Blockchain-Backups\Keystores\API-Keys\api-keys-master.txt").read_text(encoding="utf-8").splitlines():
    stripped = line.strip()
    if stripped.startswith("API Key: AIza"):
        api_key = stripped.split("API Key: ")[1]
        break

if not api_key:
    print("ERROR: Could not find Gemini API key (looking for 'API Key: AIza...')")
    sys.exit(1)

print(f"API key: {api_key[:15]}...")

# Read the paper
tex_path = Path(r"C:\Users\Michael Kernaghan\contextuality\paper\galois_letter.tex")
tex = tex_path.read_text(encoding="utf-8")

# Strip LaTeX commands for readability (same pipeline as GPT review script)
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

word_count = len(text.split())
print(f"Extracted {word_count} words from LaTeX ({len(text)} chars)")

# Reuse the same Oxford-style bundle as the GPT run for apples-to-apples comparison
review_bundle_path = Path(r"C:\Users\Michael Kernaghan\claude-inbox\galois-letter-review-v6.md")
prompt = review_bundle_path.read_text(encoding="utf-8") + "\n\nTHE PAPER:\n\n"

print("Sending to Gemini 2.5 Pro for Oxford-style review...")
print("(This may take 2-5 minutes)")

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-3-pro-preview")

from google.api_core import retry as gcp_retry
response = model.generate_content(
    prompt + text,
    generation_config={
        "max_output_tokens": 40000,
        "temperature": 0.3,
    },
    request_options={"timeout": 600, "retry": gcp_retry.Retry(predicate=lambda e: False)},
)

review = response.text or ""
usage = getattr(response, "usage_metadata", None)

if not review:
    print("WARNING: Empty response. Raw object:")
    print(response)

input_tokens = getattr(usage, "prompt_token_count", "?") if usage else "?"
output_tokens = getattr(usage, "candidates_token_count", "?") if usage else "?"
print(f"\nTokens: {input_tokens} input, {output_tokens} output")

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
print(f"\n{'='*80}")
print(review)
print(f"{'='*80}")

# Save review
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
outpath = Path(r"C:\Users\Michael Kernaghan\claude-inbox\peer-reviews") / f"galois_letter-oxford-review-gemini-{timestamp}.txt"
outpath.parent.mkdir(parents=True, exist_ok=True)
with open(outpath, "w", encoding="utf-8") as f:
    f.write(f"Oxford-Style Peer Review: Galois-Theoretic KS Classification\n")
    f.write(f"Date: {datetime.now().isoformat()}\n")
    f.write(f"Reviewer: Gemini 3 Pro Preview (via Google AI Studio)\n")
    f.write(f"Tokens: {input_tokens} input, {output_tokens} output\n")
    f.write(f"{'='*80}\n\n")
    f.write(review)

print(f"\nReview saved to: {outpath}")
