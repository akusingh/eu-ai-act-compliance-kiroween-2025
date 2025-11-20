#!/usr/bin/env python3
"""
Split EU AI Act into 3 separate sources for parallel search:
1. Recitals (1-180): The "why" - context and intent
2. Articles (1-113): The "what" - legal requirements
3. Annexes (I-XIII): The "how" - specific lists and details
"""

import re
from pathlib import Path

def split_eu_ai_act():
    """Split the EU AI Act into 3 source files."""
    
    # Paths
    project_root = Path(__file__).parent.parent
    source_file = project_root / "data" / "eu_ai_act_clean.txt"
    recitals_file = project_root / "data" / "eu_act_recitals.txt"
    articles_file = project_root / "data" / "eu_act_articles.txt"
    annexes_file = project_root / "data" / "eu_act_annexes.txt"
    
    print("=" * 60)
    print("EU AI Act Splitter")
    print("=" * 60)
    print(f"\nReading from: {source_file}")
    
    with open(source_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Total lines: {len(lines)}")
    
    # Find boundaries
    recitals_start = 0
    articles_start = None
    annexes_start = None
    
    # Find where articles start (after recitals)
    for i, line in enumerate(lines):
        # Articles typically start with "Article 1"
        if re.match(r'^Article\s+1\b', line, re.IGNORECASE):
            articles_start = i
            print(f"Found Articles start at line {i}: {line.strip()[:50]}")
            break
    
    # Find where annexes start
    for i, line in enumerate(lines):
        if re.match(r'^ANNEX\s+I\b', line):
            annexes_start = i
            print(f"Found Annexes start at line {i}: {line.strip()[:50]}")
            break
    
    if not articles_start or not annexes_start:
        print("ERROR: Could not find article or annex boundaries")
        return False
    
    # Split content
    recitals_lines = lines[recitals_start:articles_start]
    articles_lines = lines[articles_start:annexes_start]
    annexes_lines = lines[annexes_start:]
    
    # Write recitals
    with open(recitals_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("EU AI ACT - RECITALS (1-180)\n")
        f.write("Context, Intent, and Definitions\n")
        f.write("=" * 80 + "\n\n")
        f.writelines(recitals_lines)
    
    print(f"\n✓ Recitals saved: {recitals_file}")
    print(f"  Lines: {len(recitals_lines)}")
    
    # Write articles
    with open(articles_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("EU AI ACT - ARTICLES (1-113)\n")
        f.write("Legal Requirements and Obligations\n")
        f.write("=" * 80 + "\n\n")
        f.writelines(articles_lines)
    
    print(f"✓ Articles saved: {articles_file}")
    print(f"  Lines: {len(articles_lines)}")
    
    # Write annexes
    with open(annexes_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("EU AI ACT - ANNEXES (I-XIII)\n")
        f.write("Specific Lists and Technical Details\n")
        f.write("=" * 80 + "\n\n")
        f.writelines(annexes_lines)
    
    print(f"✓ Annexes saved: {annexes_file}")
    print(f"  Lines: {len(annexes_lines)}")
    
    # Verify
    total_split = len(recitals_lines) + len(articles_lines) + len(annexes_lines)
    print(f"\nVerification:")
    print(f"  Original: {len(lines)} lines")
    print(f"  Split total: {total_split} lines")
    print(f"  Match: {'✓' if total_split == len(lines) else '✗'}")
    
    # Show sample content
    print("\n" + "=" * 60)
    print("SAMPLES")
    print("=" * 60)
    
    print("\nRecitals (first 5 lines):")
    for line in recitals_lines[:5]:
        print(f"  {line.strip()[:70]}")
    
    print("\nArticles (first 5 lines):")
    for line in articles_lines[:5]:
        print(f"  {line.strip()[:70]}")
    
    print("\nAnnexes (first 5 lines):")
    for line in annexes_lines[:5]:
        print(f"  {line.strip()[:70]}")
    
    print("\n" + "=" * 60)
    print("✓ Split complete! 3 sources ready for vector indexing")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = split_eu_ai_act()
    exit(0 if success else 1)
