#!/bin/bash
# Quick Start Script for Kiroween Demo
# Sets up and runs the EU AI Act Compliance Agent

set -e

echo "🏆 EU AI Act Compliance Agent - Kiroween 2024"
echo "=============================================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.13+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python $PYTHON_VERSION found"

# Check for .env file
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.example .env
    echo "📝 Please edit .env and add your GOOGLE_GENAI_API_KEY"
    echo "   Get one at: https://aistudio.google.com/"
    exit 1
fi

# Check for API key
if ! grep -q "GOOGLE_GENAI_API_KEY=.*[^=]" .env; then
    echo "❌ GOOGLE_GENAI_API_KEY not set in .env"
    echo "   Get one at: https://aistudio.google.com/"
    exit 1
fi

echo "✅ API key configured"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check for EU AI Act data
if [ ! -f "data/eu_act_recitals.txt" ]; then
    echo "📚 Downloading EU AI Act data..."
    bash scripts/download_eu_ai_act.sh
fi

# Check for vector indexes
if [ ! -d "data/embeddings_cache" ]; then
    echo "🔍 Building vector indexes (one-time setup, ~2 minutes)..."
    python scripts/build_vector_indexes.py
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Choose a demo to run:"
echo ""
echo "1. 🎬 Interactive Terminal Demo (recommended for hackathon)"
echo "   python demo_hackathon.py"
echo ""
echo "2. 🌐 Web UI Demo (visual interface)"
echo "   python web_demo.py"
echo "   Then open: http://localhost:5000"
echo ""
echo "3. 🧪 Run Tests (show 87.5% accuracy)"
echo "   python evaluate.py"
echo ""
echo "4. 📊 Original Demo (single assessment)"
echo "   python demo_final.py"
echo ""

# Ask user which demo to run
read -p "Enter choice (1-4) or press Enter to exit: " choice

case $choice in
    1)
        echo ""
        echo "🎬 Starting interactive demo..."
        python demo_hackathon.py
        ;;
    2)
        echo ""
        echo "🌐 Starting web server..."
        echo "📱 Open http://localhost:5000 in your browser"
        python web_demo.py
        ;;
    3)
        echo ""
        echo "🧪 Running evaluation suite..."
        python evaluate.py
        ;;
    4)
        echo ""
        echo "📊 Running original demo..."
        python demo_final.py
        ;;
    *)
        echo ""
        echo "👋 Setup complete! Run any demo script when ready."
        ;;
esac
