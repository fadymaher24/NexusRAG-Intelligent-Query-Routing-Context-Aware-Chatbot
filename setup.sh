#!/bin/bash

# Setup script for NexusRAG Chatbot
# This script sets up the development environment

echo "================================================"
echo "NexusRAG Chatbot - Setup Script"
echo "================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Check if Python 3.8+ is installed
required_version="3.8"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "ERROR: Python 3.8 or higher is required"
    exit 1
fi

echo "✓ Python version is compatible"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo "✓ pip upgraded"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✓ Dependencies installed successfully"
else
    echo "ERROR: Failed to install dependencies"
    exit 1
fi
echo ""

# Create necessary directories
echo "Creating directories..."
mkdir -p logs
mkdir -p dataset
echo "✓ Directories created"
echo ""

# Setup environment file
if [ ! -f ".env" ]; then
    echo "Setting up environment file..."
    cp .env.example .env
    echo "✓ .env file created from template"
    echo "⚠️  Please edit .env file with your configuration"
else
    echo "✓ .env file already exists"
fi
echo ""

# Check for dataset files
echo "Checking dataset files..."
if [ -f "dataset/faq.joblib" ] && [ -f "dataset/clothes_json.joblib" ]; then
    echo "✓ Dataset files found"
else
    echo "⚠️  WARNING: Dataset files not found in dataset/"
    echo "   Please ensure the following files exist:"
    echo "   - dataset/faq.joblib"
    echo "   - dataset/clothes_json.joblib"
fi
echo ""

echo "================================================"
echo "Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Ensure dataset files are in the dataset/ directory"
echo "3. Start Weaviate if not already running"
echo "4. Run the application:"
echo "   - Web mode: python main.py"
echo "   - CLI mode: python main.py --mode cli"
echo ""
echo "To activate the virtual environment later, run:"
echo "   source venv/bin/activate"
echo ""
