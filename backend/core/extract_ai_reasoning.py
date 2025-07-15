import re
from pathlib import Path

LOG_PATH = Path(__file__).parent.parent / 'backend' / 'debug.log'

# Patterns to match
PROMPT_PATTERNS = [
    ('Vertex AI Prompt', re.compile(r'Vertex AI Prompt: (.+)', re.DOTALL)),
    ('Gemini Prompt', re.compile(r'Gemini Prompt: (.+)', re.DOTALL)),
    ('Gemini Raw Response', re.compile(r'Gemini Raw Response: (.+)', re.DOTALL)),
]

# Read the log file
with open(LOG_PATH, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

results = {label: None for label, _ in PROMPT_PATTERNS}

# Search backwards for the most recent occurrence of each pattern
for line in reversed(lines):
    for label, pattern in PROMPT_PATTERNS:
        if results[label] is None:
            m = pattern.search(line)
            if m:
                results[label] = m.group(1)

# Print results
found = False
for label in results:
    if results[label]:
        print(f"\n==== {label} ====")
        print(results[label])
        found = True
if not found:
    print("No Vertex AI or Gemini prompts/responses found in the log.") 