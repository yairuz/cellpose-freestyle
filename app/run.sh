#!/bin/bash
# Cellpose Freestyle - Easy Launcher Script

set -e  # Exit on error

echo "=========================================="
echo "  🔬 Cellpose Freestyle Launcher"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "backend.py" ]; then
    echo "Error: Please run this script from the app directory"
    echo "Usage: cd app && ./run.sh"
    exit 1
fi

# Check Python version
echo "Checking Python version..."
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "✓ Python $python_version"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "No virtual environment found. Creating one..."
    python -m venv venv
    echo "✓ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Check if dependencies are installed
echo "Checking dependencies..."
if ! python -c "import flask" 2>/dev/null; then
    echo "Dependencies not installed. Installing..."
    echo ""

    # Install cellpose from parent directory
    echo "Installing cellpose..."
    pip install -e .. -q

    # Install app requirements
    echo "Installing app requirements..."
    pip install -r requirements.txt -q

    echo "✓ Dependencies installed"
    echo ""
else
    echo "✓ Dependencies already installed"
    echo ""
fi

# Check for API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "⚠️  WARNING: ANTHROPIC_API_KEY not set"
    echo "   The app will work with fallback mode (rule-based interpretation)"
    echo "   For full AI agent features, set the API key:"
    echo "   export ANTHROPIC_API_KEY='your-key-here'"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting..."
        exit 0
    fi
    echo ""
else
    echo "✓ ANTHROPIC_API_KEY is set"
    echo ""
fi

# Run the app
echo "=========================================="
echo "  Starting Cellpose Freestyle App..."
echo "=========================================="
echo ""
echo "The app will be available at:"
echo "  → http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python backend.py
