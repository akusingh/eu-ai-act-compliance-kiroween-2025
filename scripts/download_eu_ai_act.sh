#!/bin/bash
################################################################################
# Download and Clean EU AI Act Regulation Text
# 
# This script downloads the official EU AI Act (Regulation 2024/1689) from
# EUR-Lex and extracts clean text suitable for vector indexing.
#
# Output:
#   - data/eu_ai_act_full.txt (raw extracted text)
#   - data/eu_ai_act_clean.txt (cleaned text for embeddings)
#
# Usage:
#   bash scripts/download_eu_ai_act.sh
################################################################################

set -e  # Exit on error

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DATA_DIR="$PROJECT_ROOT/data"

# Create data directory if it doesn't exist
mkdir -p "$DATA_DIR"

echo "========================================"
echo "EU AI Act Download and Cleanup Script"
echo "========================================"
echo ""

# Step 1: Download HTML from EUR-Lex
echo "[1/3] Downloading EU AI Act from EUR-Lex..."
EU_AI_ACT_URL="https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32024R1689&qid=1720606615699"
RAW_FILE="$DATA_DIR/eu_ai_act_full.txt"

curl -L "$EU_AI_ACT_URL" 2>/dev/null | python3 -c "
import sys
import re
import html

content = sys.stdin.read()

# Remove scripts and styles
content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)

# Remove HTML tags
text = re.sub(r'<[^>]+>', '\n', content)

# Decode HTML entities
text = html.unescape(text)

# Clean up whitespace
lines = [line.strip() for line in text.split('\n') if line.strip() and len(line.strip()) > 2]
text = '\n'.join(lines)

print(text)
" > "$RAW_FILE"

if [ ! -s "$RAW_FILE" ]; then
    echo "Error: Failed to download EU AI Act"
    exit 1
fi

echo "   ✓ Downloaded $(wc -l < "$RAW_FILE") lines to $RAW_FILE"

# Step 2: Clean the text
echo "[2/3] Cleaning extracted text..."
CLEAN_FILE="$DATA_DIR/eu_ai_act_clean.txt"

python3 << 'PYTHON_SCRIPT'
import sys
import os

# Read raw file
raw_file = os.path.join(os.environ['DATA_DIR'], 'eu_ai_act_full.txt')
clean_file = os.path.join(os.environ['DATA_DIR'], 'eu_ai_act_clean.txt')

with open(raw_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find start of actual regulation
start_idx = None
for i, line in enumerate(lines):
    if 'REGULATION (EU) 2024/1689 OF THE EUROPEAN PARLIAMENT' in line:
        start_idx = i
        break

if not start_idx:
    print("Error: Could not find regulation start marker", file=sys.stderr)
    sys.exit(1)

# Keep everything from the regulation title onward
clean_lines = lines[start_idx:]

# Remove obvious navigation/UI elements
filtered_lines = []
skip_phrases = [
    'toggle dropdown', 'expand all', 'collapse all', 'please choose',
    'sign in', 'register', 'my eur-lex', 'download notice',
    'create an email alert', 'create an rss alert', 'save to my items',
    'multilingual display', 'display text', 'hide table of contents',
    'show table of contents', 'up-to-date link', 'permanent link'
]

for line in clean_lines:
    line_lower = line.lower().strip()
    
    # Skip short navigation phrases
    if any(phrase in line_lower for phrase in skip_phrases) and len(line_lower) < 50:
        continue
    
    # Keep non-empty lines
    if line.strip():
        filtered_lines.append(line)

# Write cleaned version
with open(clean_file, 'w', encoding='utf-8') as f:
    f.writelines(filtered_lines)

print(f"Cleaned version created: {len(filtered_lines)} lines (from {len(lines)} original)")
PYTHON_SCRIPT

if [ ! -s "$CLEAN_FILE" ]; then
    echo "Error: Failed to create cleaned file"
    exit 1
fi

echo "   ✓ Created clean version: $CLEAN_FILE"

# Step 3: Verify content
echo "[3/3] Verifying content..."
FILESIZE=$(ls -lh "$CLEAN_FILE" | awk '{print $5}')
LINE_COUNT=$(wc -l < "$CLEAN_FILE")

echo "   ✓ File size: $FILESIZE"
echo "   ✓ Line count: $LINE_COUNT"

# Check for key articles
if grep -q "Article 5" "$CLEAN_FILE" && grep -q "Article 6" "$CLEAN_FILE"; then
    echo "   ✓ Key articles found (Article 5, Article 6)"
else
    echo "   ⚠ Warning: Some key articles may be missing"
fi

echo ""
echo "========================================"
echo "✓ Download and cleanup complete!"
echo "========================================"
echo ""
echo "Files created:"
echo "  - $RAW_FILE (raw extraction)"
echo "  - $CLEAN_FILE (cleaned for embeddings)"
echo ""
echo "Next steps:"
echo "  1. Review $CLEAN_FILE"
echo "  2. Run vector indexing: python3 scripts/build_vector_index.py"
echo ""
