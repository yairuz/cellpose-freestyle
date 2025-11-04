#!/bin/bash
# Quick start script for the Cellpose Cell Coverage Analyzer

set -e

echo "========================================="
echo "Cellpose Cell Coverage Analyzer"
echo "========================================="
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "Error: Python 3.8+ required (found $PYTHON_VERSION)"
    exit 1
fi

echo "Python version: OK ($PYTHON_VERSION)"
echo ""

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created!"
else
    echo "Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

echo ""
echo "========================================="
echo "Starting Cellpose Web App..."
echo "========================================="
echo ""
echo "The app will be available at: http://localhost:5000"
echo ""
echo "Note: First request will download ~500MB model (one-time only)"
echo "Processing time: ~30-60 seconds per image on CPU"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start the app
python app.py
