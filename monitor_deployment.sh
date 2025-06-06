#!/bin/bash

echo "🔍 Monitoring Railway Deployment Status..."
echo "=========================================="

# Function to check health endpoint
check_health() {
    local response=$(curl -s https://crewai-production-d99a.up.railway.app/health)
    local environment=$(echo "$response" | jq -r '.environment // .server // "unknown"')
    local status=$(echo "$response" | jq -r '.status // "unknown"')
    local timestamp=$(echo "$response" | jq -r '.timestamp // "unknown"')
    
    echo "$(date): Status=$status, Environment=$environment"
    
    # Check if it's the new version (should have "environment" field)
    if echo "$response" | jq -e '.environment' > /dev/null 2>&1; then
        echo "✅ New deployment detected!"
        echo "📋 Full health check response:"
        echo "$response" | jq .
        return 0
    else
        echo "⏳ Still on old deployment (has 'server' field instead of 'environment')"
        return 1
    fi
}

# Monitor for up to 10 minutes
echo "⏰ Monitoring for new deployment (max 10 minutes)..."
echo ""

for i in {1..20}; do
    echo "Check #$i:"
    if check_health; then
        echo ""
        echo "🎉 Deployment update successful!"
        exit 0
    fi
    echo ""
    
    if [ $i -lt 20 ]; then
        echo "💤 Waiting 30 seconds before next check..."
        sleep 30
    fi
done

echo "⚠️ Timeout reached. New deployment may still be in progress."
echo "🔗 Check Railway dashboard for deployment status."
