#!/bin/bash

echo "🚀 Create New Repository for Hand Landmarks Detection"
echo "====================================================="
echo ""

# Get repository name
read -p "📝 Enter repository name (e.g., hand-landmarks-detection): " REPO_NAME

if [ -z "$REPO_NAME" ]; then
    REPO_NAME="hand-landmarks-detection"
    echo "Using default name: $REPO_NAME"
fi

# Get GitHub username
read -p "👤 Enter your GitHub username: " GITHUB_USERNAME

if [ -z "$GITHUB_USERNAME" ]; then
    echo "❌ GitHub username is required!"
    exit 1
fi

# Confirm details
echo ""
echo "📋 Repository Details:"
echo "   Name: $REPO_NAME"
echo "   Username: $GITHUB_USERNAME"
echo "   URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo ""

read -p "✅ Create repository with these details? (y/N): " CONFIRM

if [[ $CONFIRM != [yY] && $CONFIRM != [yY][eE][sS] ]]; then
    echo "❌ Repository creation cancelled"
    exit 1
fi

echo ""
echo "🔧 Setting up repository..."

# Add remote origin
git remote add origin https://github.com/$GITHUB_USERNAME/$REPO_NAME.git

# Set upstream branch
git branch -M main

echo ""
echo "📋 Next Steps:"
echo "=============="
echo ""
echo "1. 🌐 Create the repository on GitHub:"
echo "   - Go to: https://github.com/new"
echo "   - Repository name: $REPO_NAME"
echo "   - Description: Real-time hand landmarks detection using MediaPipe"
echo "   - Make it Public (recommended for open source)"
echo "   - DON'T initialize with README, .gitignore, or license (we already have them)"
echo "   - Click 'Create repository'"
echo ""
echo "2. 🚀 Push your code:"
echo "   git push -u origin main"
echo ""
echo "3. 🎯 Alternative: Push to a specific branch:"
echo "   git checkout -b hand-landmarks-feature"
echo "   git push -u origin hand-landmarks-feature"
echo ""

# Check if GitHub CLI is available
if command -v gh &> /dev/null; then
    echo "💡 GitHub CLI detected! You can also create the repo automatically:"
    echo "   gh repo create $REPO_NAME --public --description 'Real-time hand landmarks detection using MediaPipe'"
    echo "   git push -u origin main"
    echo ""
fi

echo "🔗 Repository URL: https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo ""
echo "✨ Your hand landmarks detection project is ready to be pushed!"
