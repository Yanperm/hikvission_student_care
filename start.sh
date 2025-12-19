#!/bin/bash

echo "=========================================="
echo "  🎓 Student Care System"
echo "  © 2025 SOFTUBON CO.,LTD."
echo "=========================================="
echo ""

# Detect Python
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo "❌ Python not found!"
    exit 1
fi

echo "🚀 Starting Student Care System..."
echo "🌐 Open browser: http://localhost:5000"
echo "☁️  Cloud Sync: Active"
echo ""
echo "Press Ctrl+C to stop"
echo "=========================================="
echo ""

$PYTHON_CMD local_app.py
