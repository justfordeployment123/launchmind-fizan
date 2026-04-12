#!/bin/bash
# LaunchMind - Deploy to GitHub

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   LaunchMind - Deploy to GitHub                              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Configure git if needed
echo "Step 1: Configure Git (if first time)"
read -p "Enter your GitHub username (justfordeployment123): " GITHUB_USER
GITHUB_USER=${GITHUB_USER:-justfordeployment123}

read -p "Enter your Git email: " GIT_EMAIL
git config --global user.name "$GITHUB_USER"
git config --global user.email "$GIT_EMAIL"

echo "✅ Git configured"
echo ""

# Add GitHub remote
echo "Step 2: Adding GitHub remote..."
REPO_URL="https://github.com/$GITHUB_USER/launchmind-fizan.git"
echo "Repository URL: $REPO_URL"

# Remove old origin if it exists
git remote remove origin 2>/dev/null

# Add new origin
git remote add origin "$REPO_URL"
echo "✅ Remote added"
echo ""

# Push to GitHub
echo "Step 3: Pushing to GitHub..."
echo "Note: If prompted, enter your GitHub username + Personal Access Token as password"
echo ""

git branch -M main
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║   ✅ SUCCESSFULLY PUSHED TO GITHUB!                           ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Your repository is now at:"
    echo "→ $REPO_URL"
    echo ""
    echo "Next steps:"
    echo "1. Verify repo is public: https://github.com/$GITHUB_USER/launchmind-fizan"
    echo "2. Get your GitHub token if you don't have it"
    echo "3. Follow SETUP.md to configure API tokens"
    echo "4. Run: python main.py"
else
    echo ""
    echo "❌ Push failed. Check error messages above."
    echo ""
    echo "Common issues:"
    echo "• GitHub token insufficient permissions (needs 'repo' scope)"
    echo "• Repository doesn't exist (create it first)"
    echo "• Authentication failed (use Personal Access Token, not password)"
fi
