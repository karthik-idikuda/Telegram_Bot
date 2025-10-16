#!/bin/bash

# 🚀 Railway Deployment Script
# This script helps you deploy your bot to Railway quickly!

echo "🚀 SycproBot - Railway Deployment Helper"
echo "========================================"
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📦 Initializing Git repository..."
    git init
    echo "✅ Git initialized!"
else
    echo "✅ Git already initialized"
fi

# Check if .gitignore exists
if [ ! -f .gitignore ]; then
    echo "🔒 Creating .gitignore to protect secrets..."
    cat > .gitignore << 'EOF'
.env
*.pyc
__pycache__/
credentials.json
xerironx-studio-472418-a23db74a64d6.json
tasks.json
gamification_data.json
.DS_Store
*.log
venv/
env/
EOF
    echo "✅ .gitignore created!"
else
    echo "✅ .gitignore already exists"
fi

# Add all files
echo ""
echo "📝 Adding files to Git..."
git add .

# Commit
echo "💾 Creating commit..."
git commit -m "Ready for Railway deployment - $(date '+%Y-%m-%d %H:%M:%S')"

echo ""
echo "✅ Repository is ready for deployment!"
echo ""
echo "📋 Next Steps:"
echo "1. Create a repository on GitHub.com"
echo "2. Run these commands:"
echo ""
echo "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "3. Then go to railway.app and deploy!"
echo ""
echo "📖 Full instructions in DEPLOYMENT.md"
