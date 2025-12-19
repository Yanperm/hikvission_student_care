#!/bin/bash

echo "=========================================="
echo "  Student Care System - Auto Installer"
echo "  © 2025 SOFTUBON CO.,LTD."
echo "=========================================="
echo ""

# Check Python
echo "🔍 Checking Python..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
    PIP_CMD=pip3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
    PIP_CMD=pip
else
    echo "❌ Python not found! Please install Python 3.7+"
    exit 1
fi

echo "✅ Python found: $($PYTHON_CMD --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
$PIP_CMD install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""

# Create data directory
echo "📁 Creating data directory..."
mkdir -p data/students
echo "✅ Data directory created!"

echo ""
echo "=========================================="
echo "  ✅ Installation Complete!"
echo "=========================================="
echo ""
echo "🚀 To start the system, run:"
echo "   $PYTHON_CMD local_app.py"
echo ""
echo "🌐 Then open browser:"
echo "   http://localhost:5000"
echo ""
echo "☁️  Cloud Sync: Automatic"
echo "=========================================="
