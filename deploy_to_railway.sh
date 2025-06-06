#!/bin/bash
# Railway Deployment Script for Morvo AI Marketing Platform
# Uses incremental deployment strategy to ensure successful builds

echo "🚀 Starting Morvo AI Marketing Platform deployment to Railway..."

# Step 1: Ensure Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm i -g @railway/cli
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install Railway CLI. Please install manually."
        exit 1
    fi
fi

# Step 2: Verify login status
echo "🔑 Verifying Railway login status..."
railway whoami
if [ $? -ne 0 ]; then
    echo "❌ Not logged in to Railway. Please login first with 'railway login'"
    exit 1
fi

# Step 3: Verify environment variables
echo "🔍 Checking required environment variables..."
if [ -f .env ]; then
    echo "✅ .env file found."
else
    echo "⚠️ No .env file found. Make sure to set environment variables in Railway project."
fi

# Step 4: Verify project files
echo "📋 Verifying project files..."
required_files=("morvo_integration_api.py" "Dockerfile" "railway.toml" "requirements.txt")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Required file $file not found."
        exit 1
    else
        echo "✅ $file found."
    fi
done

# Step 5: Check if in a Git repository
echo "🔄 Checking Git repository status..."
if [ ! -d .git ]; then
    echo "⚠️ Not in a Git repository. Initializing..."
    git init
    git add .
    git commit -m "Initial commit for Railway deployment"
fi

# Step 6: Deploy to Railway
echo "🚀 Deploying to Railway..."
railway up

# Step 7: Display deployment URL
echo "✅ Deployment completed!"
echo "📝 Use 'railway status' to check deployment status"
echo "🔗 Use 'railway open' to open your application in the browser"

echo "🎉 Morvo AI Marketing Platform deployment process completed!"
