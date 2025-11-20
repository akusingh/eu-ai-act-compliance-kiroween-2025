#!/bin/bash

# Render all .dot files to PNG images
# Usage: ./render_all.sh

echo "🎨 Rendering all Graphviz diagrams..."
echo ""

# Check if graphviz is installed
if ! command -v dot &> /dev/null; then
    echo "❌ Error: Graphviz not installed"
    echo "Install with: brew install graphviz"
    exit 1
fi

# Count files
total=$(ls *.dot 2>/dev/null | wc -l | tr -d ' ')

if [ "$total" -eq 0 ]; then
    echo "❌ No .dot files found in current directory"
    exit 1
fi

echo "Found $total diagram files"
echo ""

# Render each file
count=0
for file in *.dot; do
    count=$((count + 1))
    output="${file%.dot}.png"
    
    echo "[$count/$total] Rendering $file → $output"
    
    if dot -Tpng "$file" -o "$output" 2>/dev/null; then
        echo "  ✅ Success"
    else
        echo "  ❌ Failed"
    fi
done

echo ""
echo "✨ Done! Rendered $count diagrams"
echo ""
echo "📊 Files created:"
ls -lh *.png 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'
echo ""
echo "🖼️  Open all images:"
echo "  open *.png"
echo ""
