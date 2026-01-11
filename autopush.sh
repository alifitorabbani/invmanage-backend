#!/bin/bash
echo "🚀 Auto-commit and push to GitHub..."

# Add all changes
git add .

# Check if there are changes
if git diff --staged --quiet; then
    echo "✅ No changes to commit"
    exit 0
fi

# Commit with timestamp
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")
git commit -m "Auto-commit: $TIMESTAMP"

# Push to GitHub
echo "📤 Pushing to GitHub..."
if git push origin main; then
    echo "✅ Successfully pushed to GitHub!"
else
    echo "❌ Push failed. Trying to pull and merge..."
    git pull origin main --no-edit
    git push origin main
fi

echo "🎉 Done!"

