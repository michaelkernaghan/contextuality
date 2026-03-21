"""
oxford_review.py -- Oxford hostile-examiner peer review via OpenAI API
"""

import re
import sys
import json
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def strip_latex(text):
    text = re.sub(r'%.*$', '', text, flags=re.MULTILINE)
    match = re.search(r'\\begin\{document\}', text)
    if match:
        text = text[match.end():]
    end_match = re.search(r'\\end\{document\}', text)
    if end_match:
        text = text[:end_match.start()]
    text = re.sub(r'\\(?:textbf|textit|emph|texttt)\{([^}]*)\}', r'\1', text)
    text = re.sub(r'\\(?:section|subsection|subsubsection)\*?\{([^}]*)\}', r'\n\n## \1\n', text)
    text = re.sub(r'\\(?:label|ref|cite|eqref|url)\{[^}]*\}', '', text)
    text = re.sub(r'\\item\b', '- ', text)
    text = re.sub(r'\\caption\{([^}]*)\}', r'Caption: \1', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def get_api_key():
    key_file = Path(r"E:\Blockchain-Backups\Keystores\API-Keys\api-keys-master.txt")
    content = key_file.read_text(encoding='utf-8')
    match = re.search(r'OPENAI API KEY.*?API Key:\s*(sk-[^\s]+)', content, re.DOTALL)
    if match:
        return match.group(1)
    raise ValueError("OpenAI API key not found")


OXFORD_PROMPT = (
    "You are a hostile Oxford examiner reviewing a paper for Physical Review A. "
    "This paper has been through 6 rounds of GPT peer review already. "
    "Your job is to find what they missed.\n\n"
    "Apply the three-step Oxford Thinking Partner method:\n\n"
    "STEP 1 - HOSTILE EXAMINER:\n"
    "What are the 5 weakest logical jumps in this reasoning? "
    "Where would a hostile examiner attack first? Look for implicit assumptions, "
    "terse proofs where the reader fills gaps, rhetorical moves that overstate connections, "
    "computational observations dressed as theorems, and places where 'among tested fields' "
    "quietly drops out and claims become universal.\n\n"
    "STEP 2 - LITERATURE CHECK:\n"
    "What claims contradict or oversimplify what cited authors actually found? "
    "Are citations used accurately?\n\n"
    "STEP 3 - PHILOSOPHY OF SCIENCE:\n"
    "What would a philosopher of science say is missing? "
    "Is this universal or specific to the parameterization? "
    "Are we overselling a survey as a classification? "
    "Does the two-mechanism thesis have the status of conjecture, framework, or theorem? "
    "Is 'algebraic island' a natural kind or convenient label?\n\n"
    "OUTPUT: Produce a table with columns: "
    "Priority (High/Medium/Low) | Issue | Section | Suggested Fix. Be ruthless."
)


def call_openai(api_key, paper_text):
    prompt = (
        OXFORD_PROMPT
        + "\n\n--- Paper text ---\n"
        + paper_text
        + "\n--- End of paper ---\n\n"
        + "Provide your hostile examination now."
    )

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

    with urllib.request.urlopen(req, timeout=900) as resp:
        result = json.loads(resp.read().decode('utf-8'))
        for item in result.get('output', []):
            if item.get('type') == 'message':
                for c in item.get('content', []):
                    if c.get('type') == 'output_text':
                        return c['text']
        raise RuntimeError(f"No text output: {json.dumps(result)[:500]}")


if __name__ == "__main__":
    file_path = Path(r"C:\Users\Michael Kernaghan\contextuality\paper\algebraic_islands.tex")

    print(f"Reading: {file_path}")
    content = file_path.read_text(encoding='utf-8')
    content = strip_latex(content)

    if len(content) > 80000:
        print(f"Truncating from {len(content)} to 80000 chars")
        content = content[:80000]

    print(f"Document: {len(content)} chars")
    print("Sending to GPT-5.4-pro for Oxford hostile review...")
    t0 = datetime.now()

    api_key = get_api_key()
    review = call_openai(api_key, content)

    elapsed = (datetime.now() - t0).total_seconds()
    print(f"Review received ({elapsed:.1f}s)")

    reviews_dir = Path.home() / "claude-inbox" / "peer-reviews"
    reviews_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    review_file = reviews_dir / f"algebraic_islands-oxford-gpt54-{timestamp}.txt"

    sep = "=" * 70
    header = (
        f"Oxford Hostile Examiner Review: algebraic_islands.tex\n"
        f"Date: {datetime.now()}\n"
        f"Reviewer: GPT-5.4-pro\n"
        f"Elapsed: {elapsed:.1f}s\n\n"
        f"{sep}\n\n"
    )
    review_file.write_text(header + (review or "NO REVIEW"), encoding='utf-8')
    print(f"Review saved to: {review_file}")
    print()
    print(sep)
    print(review or "NO REVIEW")
