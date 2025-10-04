#!/bin/bash

# Git setup script for Hand Landmarks Detection project
echo "🔧 Setting up Git repository for Hand Landmarks Detection"
echo "========================================================"

# Initialize git if not already initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
else
    echo "✅ Git repository already exists"
fi

# Add all files
echo "📝 Adding files to Git..."
git add .

# Check git status
echo "📊 Git status:"
git status

echo ""
echo "🎯 Ready for Git operations!"
echo ""
echo "Next steps:"
echo "1. Commit your changes:"
echo "   git commit -m 'Initial commit: Hand landmarks detection system'"
echo ""
echo "2. Add remote repository (if needed):"
echo "   git remote add origin <your-repo-url>"
echo ""
echo "3. Create and switch to a new branch:"
echo "   git checkout -b hand-landmarks-feature"
echo ""
echo "4. Push to remote repository:"
echo "   git push -u origin hand-landmarks-feature"
echo ""
echo "📋 Files ready for commit:"
git ls-files --others --cached
