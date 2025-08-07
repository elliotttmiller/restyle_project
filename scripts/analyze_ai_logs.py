import re
import json
import sys
import subprocess
from pathlib import Path

# Path to the backend debug log
LOG_PATH = Path(__file__).parent.parent / 'backend' / 'debug.log'
# Output file
OUTPUT_PATH = Path(__file__).parent / 'ai_image_search_log_summary.json'

# Regex patterns for log extraction
PROMPT_PATTERN = re.compile(r'Vertex AI Prompt: (.+)')
RESPONSE_PATTERN = re.compile(r'Gemini Response: (.+)')
EBAY_QUERY_PATTERN = re.compile(r"\[EbayService\] Searching eBay with query: '(.+?)' params=(\{.+?\})")
EBAY_RESULTS_PATTERN = re.compile(r"\[EbayService\] Found (\d+) items for query: '(.+?)'")

# Store results
results = []

# Usage: python analyze_ai_logs.py [--docker]
def get_log_lines(use_docker=False):
    if use_docker:
        # Run 'docker compose logs backend' and capture output
        proc = subprocess.run([
            'docker', 'compose', 'logs', 'backend', '--no-color'
        ], capture_output=True, text=True)
        return proc.stdout.splitlines()
    else:
        with open(LOG_PATH, 'r', encoding='utf-8', errors='ignore') as f:
            return f.readlines()

def main():
    use_docker = '--docker' in sys.argv
    lines = get_log_lines(use_docker)
    current = {}
    for line in lines:
        prompt_match = PROMPT_PATTERN.search(line)
        if prompt_match:
            if current:
                results.append(current)
                current = {}
            current['prompt'] = prompt_match.group(1)
            continue
        response_match = RESPONSE_PATTERN.search(line)
        if response_match:
            current['ai_response'] = response_match.group(1)
            continue
        ebay_query_match = EBAY_QUERY_PATTERN.search(line)
        if ebay_query_match:
            current['ebay_query'] = ebay_query_match.group(1)
            current['ebay_params'] = ebay_query_match.group(2)
            continue
        ebay_results_match = EBAY_RESULTS_PATTERN.search(line)
        if ebay_results_match:
            current['ebay_results_count'] = int(ebay_results_match.group(1))
            current['ebay_results_query'] = ebay_results_match.group(2)
            continue
    # Add last
    if current:
        results.append(current)
    # Write summary to JSON
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print(f"Extracted {len(results)} AI image search log entries. Summary written to {OUTPUT_PATH}")
    if len(results) == 0:
        print("No AI image search log entries found. Try running with --docker if using Docker logs.")

if __name__ == '__main__':
    main() 