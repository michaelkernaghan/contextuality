"""Submit the Contextuality & KS Set Atlas website to GPT-5.4 Pro for peer review."""
import requests
import sys
from datetime import datetime
from pathlib import Path

# Read API key
api_key = None
for line in Path(r"E:\Blockchain-Backups\Keystores\API-Keys\api-keys-master.txt").read_text(encoding="utf-8").splitlines():
    stripped = line.strip()
    if stripped.startswith("sk-svcacct-"):
        api_key = stripped
        break

if not api_key:
    print("ERROR: Could not find OpenAI service account API key")
    sys.exit(1)

print(f"API key: {api_key[:25]}...")

# Read the bundle
bundle = Path("site_review_bundle.md").read_text(encoding="utf-8")
words = len(bundle.split())
print(f"Document: {words} words ({len(bundle)} chars)")

prompt = """You are a peer reviewer with expertise in:
- Quantum foundations: Kochen-Specker theorem, contextuality, Bell nonlocality
- Algebraic number theory: number rings, quadratic fields, cyclotomic fields
- Scientific website design: structure, navigation, accuracy, completeness
- Academic writing: clarity, precision, appropriate level of detail

Please review this academic research website (the "Contextuality & KS Set Atlas") which documents:
1. Classic Kochen-Specker set constructions (Peres-33, Conway-Kochen-31, Kernaghan-20, etc.)
2. New 2026 research discovering six "algebraic islands" — number rings that produce KS sets in dimension 3
3. Four new KS set constructions (Eisenstein-33, Heegner-7-43, Golden-52, Z[sqrt(-2)]-33)
4. Supporting results: rigidity, BPQS, merge saturation, sub-31 optimality, 6|n cyclotomic theorem

The website is served from Markdown files via MkDocs/Netlify at contextuality.netlify.app.

Evaluate the site on:

1. **Scientific Accuracy**: Are the mathematical claims, theorem statements, and structural data (vector counts, orthogonal pairs, rigidity results) consistent and correct across all pages? Any contradictions between pages?

2. **Completeness**: Does the site adequately present the research? Are there important results mentioned on some pages but missing from others? Are cross-references sufficient?

3. **Accessibility**: Would a graduate student in quantum information understand the material? Is there enough context for newcomers while maintaining rigor for experts?

4. **Site Structure & Navigation**: Is the organization logical? Can readers find what they need? Are the cross-links between pages helpful and complete?

5. **Writing Quality**: Is the prose clear and precise? Any awkward phrasing, redundancy, or missing context?

6. **Presentation of New Results**: Are the four new KS sets and the algebraic islands classification presented convincingly? Is the relationship to prior work (especially Cabello 2025) handled appropriately?

7. **Bibliography & References**: Are citations complete and consistent? Any missing references that should be included?

8. **Suggestions for Improvement**: What would make this site a better resource for the quantum foundations community?

Be thorough, honest, and constructive. Point out specific issues with page references."""

print("Submitting to GPT-5.4 Pro for review...")
start = datetime.now()

resp = requests.post(
    "https://api.openai.com/v1/responses",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    },
    json={
        "model": "gpt-5.4",
        "input": [
            {"role": "user", "content": f"{prompt}\n\n--- WEBSITE CONTENT ---\n{bundle}\n--- END ---\n\nProvide your peer review now."}
        ],
        "max_output_tokens": 16000,
    },
    timeout=600,
)

elapsed = (datetime.now() - start).total_seconds()

if resp.status_code != 200:
    print(f"ERROR: HTTP {resp.status_code}")
    print(resp.text[:2000])
    sys.exit(1)

data = resp.json()

# Extract text from response
review_text = ""
for item in data.get("output", []):
    if item.get("type") == "message":
        for content in item.get("content", []):
            if content.get("type") == "output_text":
                review_text += content["text"]

if not review_text:
    print("ERROR: Empty response")
    print(str(data)[:2000])
    sys.exit(1)

# Save review
output_dir = Path(r"C:\Users\Michael Kernaghan\claude-inbox\peer-reviews")
output_dir.mkdir(parents=True, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
outpath = output_dir / f"contextuality-site-review-{timestamp}.txt"

with open(outpath, "w", encoding="utf-8") as f:
    f.write(f"Peer Review: Contextuality & KS Set Atlas Website\n")
    f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"Reviewer: GPT-5.4 Pro (via OpenAI Responses API)\n")
    f.write(f"Elapsed: {elapsed:.1f}s\n")
    f.write(f"Document: {words} words from 13 pages\n")
    f.write("---\n\n")
    f.write(review_text)

print(f"\nReview saved to: {outpath}")
print(f"Elapsed: {elapsed:.1f}s")
print(f"\n{'='*60}")
print(review_text)
