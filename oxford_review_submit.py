"""
Oxford hostile-examiner review submission to GPT-5.4-pro.
One-off script for sub31_overview.tex
"""
import sys
import re
import json
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def strip_latex(text):
    text = re.sub(r'%.*$', '', text, flags=re.MULTILINE)
    match = re.search(r'\\begin\{document\}', text)
    if match:
        text = text[match.end():]
    text = re.sub(r'\\end\{document\}.*', '', text, flags=re.DOTALL)
    text = re.sub(r'\\(?:textbf|textit|emph|texttt)\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\(?:section|subsection|subsubsection)\*?\{([^}]*)\}', r'\n\n## \1\n', text)
    text = re.sub(r'\\(?:label|ref|cite|eqref|url)\{[^}]*\}', '', text)
    text = re.sub(r'\\(?:begin|end)\{(?:enumerate|itemize|description|center|table|figure|remark|observation|conjecture|proposition|proof|definition|quote)\}', '', text)
    text = re.sub(r'\\item\b', '- ', text)
    text = re.sub(r'\\caption\{([^}]*)\}', r'Caption: \1', text)
    text = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\[a-zA-Z]+', '', text)
    text = re.sub(r'[{}]', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def main():
    paper_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("paper/sub31_overview.tex")
    paper_text = strip_latex(paper_path.read_text(encoding='utf-8'))

    prompt = f"""You are an Oxford-trained hostile examiner reviewing this paper for a top physics journal (Physical Review A). Perform THREE attacks:

STEP 1 -- HOSTILE EXAMINER: What are the 3 weakest logical jumps in this reasoning? Where would a hostile examiner attack first? Look for implicit assumptions that are not stated, terse arguments where the reader has to fill gaps, and rhetorical moves that overstate connections between results.

STEP 2 -- LITERATURE CHECK: What claims in this argument contradict or oversimplify what the cited authors actually found? Check if citations say what the paper claims they say. Check if the paper conflates its result type with a cited result type. Flag referenced results that are secondary sources only.

STEP 3 -- PHILOSOPHY OF SCIENCE: What would a philosopher of science say is missing? What assumptions has the author made but not defended? Is this a universal result or specific to their parameterization? Are they overselling a lemma as a phenomenon? Does their evidence actually illuminate the claimed thesis or just inherit from a known result?

Output a table of actionable items with columns: Priority (High/Medium/Low), Issue, and Suggested Fix.

Paper text:

{paper_text}"""

    api_key_path = Path("E:/Blockchain-Backups/Keystores/API-Keys/api-keys-master.txt")
    api_key = None
    for line in api_key_path.read_text().splitlines():
        line = line.strip()
        if line.startswith("sk-svcacct-"):
            api_key = line
            break
    if not api_key:
        print("ERROR: No OpenAI service account key found")
        sys.exit(1)

    payload = {
        "model": "gpt-5.4-pro",
        "input": prompt,
        "reasoning": {"effort": "high"},
    }

    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )

    print(f"Submitting to GPT-5.4-pro ({len(paper_text)} chars)...")
    try:
        with urllib.request.urlopen(req, timeout=600) as resp:
            result = json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        print(f"HTTP {e.code}: {body[:500]}")
        sys.exit(1)

    # Extract text from response
    review_text = ""
    for item in result.get("output", []):
        if item.get("type") == "message":
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    review_text = content.get("text", "")

    if not review_text:
        print("No review text in response")
        print(json.dumps(result, indent=2)[:1000])
        sys.exit(1)

    # Save
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_path = Path(f"C:/Users/Michael Kernaghan/claude-inbox/peer-reviews/sub31_overview-oxford-gpt54-{ts}.txt")
    out_path.write_text(review_text, encoding='utf-8')
    print(f"Review saved to: {out_path}")
    print(f"Length: {len(review_text)} chars")
    print("\n--- PREVIEW ---")
    print(review_text[:2000])


if __name__ == "__main__":
    main()
