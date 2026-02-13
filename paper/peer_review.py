"""Send paper to GPT-4o for peer review."""
import requests
import json
import re
from datetime import datetime

# Read the paper
with open(r'C:\Users\Michael Kernaghan\contextuality\paper\algebraic_islands.tex', 'r', encoding='utf-8') as f:
    tex_content = f.read()

# Light cleanup for readability (keep most LaTeX intact - GPT can read it)
text = tex_content

import os
api_key = os.environ.get('OPENAI_API_KEY', '')

prompt = """You are a rigorous academic referee reviewing a paper for a mathematics/physics journal (e.g., Journal of Physics A or Physical Review A). This is the FIFTH round of review -- previous rounds have already addressed many issues.

Provide a detailed referee-style review covering:
1. Overall Assessment: Is this publishable? What tier of revision is needed?
2. Mathematical Precision: Check definitions, propositions, conjectures for internal consistency. Pay special attention to ray equivalence conventions (real vs complex), the cofactor formula for complex completion, and whether the island definition covers both real and complex cases.
3. Methodology and Reproducibility: Are the computational methods clearly specified? Are the caveats honest?
4. Claims vs Evidence: Are any claims still stronger than what the computations support?
5. Novelty: What is genuinely new here? Position against the literature.
6. Specific Issues: List any remaining errors, inconsistencies, or unclear passages.
7. Minor editorial suggestions.

Be strict but constructive. Focus on what still needs fixing."""

response = requests.post(
    'https://api.openai.com/v1/chat/completions',
    headers={
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    },
    json={
        'model': 'gpt-4o',
        'messages': [
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': f'Please provide a CRITICAL REVIEW (not a rewrite or summary) of this LaTeX paper. Point out errors, inconsistencies, and weaknesses. Do NOT rewrite sections of the paper. Here is the paper:\n\n{text[:25000]}'}
        ],
        'max_tokens': 4000,
        'temperature': 0.3
    },
    timeout=120
)

result = response.json()
review_text = result['choices'][0]['message']['content']

# Save review
timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
review_path = rf'C:\Users\Michael Kernaghan\claude-inbox\peer-reviews\algebraic_islands-review-{timestamp}.txt'
with open(review_path, 'w', encoding='utf-8') as f:
    f.write(f'Peer Review: The Algebraic Landscape of Kochen-Specker Sets in Dimension Three\n')
    f.write(f'Date: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n')
    f.write(f'Reviewer: GPT-4o (via OpenAI API)\n')
    f.write(f'Round: 5\n')
    f.write(f'---\n\n')
    f.write(review_text)

print(f'Review saved to: {review_path}')
print()
print(review_text)
