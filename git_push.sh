#!/bin/bash

echo "=========================================="
echo "  📤 Push to GitHub"
echo "  © 2025 SOFTUBON CO.,LTD."
echo "=========================================="
echo ""

echo "📝 Adding all files..."
git add .

echo ""
echo "💬 Committing changes..."
git commit -m "Update: Complete Student Care System with 21 features"

echo ""
echo "📤 Pushing to GitHub..."
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo "🌐 https://github.com/Yanperm/hikvission_student_care"
else
    echo ""
    echo "❌ Failed to push. Please check your connection."
fi

echo ""
