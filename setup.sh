#!/bin/bash
# Setup script for EU AI Act Compliance Agent

echo "Setting up EU AI Act Compliance Agent..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Copy .env.example to .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "WARNING: Please update .env with your API keys"
fi

# Install/upgrade dependencies
echo "Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

echo "Setup complete!"
echo "To activate the environment, run: source venv/bin/activate"
