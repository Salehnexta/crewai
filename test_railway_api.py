#!/usr/bin/env python3
"""
Test script for Railway-deployed Morvo AI Marketing Platform
Tests all M1-M5 agent endpoints after successful deployment
"""

import requests
import json
import time
import os

# Railway URL - Update this with your actual deployment URL
RAILWAY_BASE_URL = "https://crewai-production-d99a.up.railway.app"

def detect_railway_url():
    """Try to detect Railway URL from common patterns"""
    print("💡 Please update RAILWAY_BASE_URL in this script with your actual Railway URL")
    print("   It should look like: https://your-app-name.railway.app")
    print("   Or: https://your-app-name-production.up.railway.app")
    return RAILWAY_BASE_URL

def test_endpoint(endpoint, method="GET", data=None, timeout=30):
    """Test a single API endpoint"""
    try:
        url = f"{RAILWAY_BASE_URL}{endpoint}"
        print(f"\n🔍 Testing: {method} {endpoint}")
        
        if method == "GET":
            response = requests.get(url, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=timeout)
        
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Success!")
        else:
            print(f"   ❌ Failed: {response.status_code}")
        
        # Show response preview
        text = response.text[:300]
        if len(response.text) > 300:
            text += "..."
        print(f"   Response: {text}")
        
        return response.status_code == 200
    except requests.exceptions.Timeout:
        print(f"   ⏱️ Timeout after {timeout}s")
        return False
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return False

def main():
    """Test all Railway endpoints"""
    print("🚀 Testing Railway-Deployed Morvo AI Marketing Platform")
    print(f"🌐 Base URL: {detect_railway_url()}")
    
    # Basic endpoints
    endpoints_to_test = [
        "/health",
        "/",
        "/docs",
    ]
    
    # M1-M5 Agent endpoints (if they exist)
    agent_endpoints = [
        "/api/v2/agents/m1/strategic-analysis",
        "/api/v2/agents/m2/social-monitoring", 
        "/api/v2/agents/m3/campaign-optimization",
        "/api/v2/agents/m4/content-strategy",
        "/api/v2/agents/m5/data-analytics",
    ]
    
    print("\n" + "="*50)
    print("🔧 Testing Basic Endpoints")
    print("="*50)
    
    for endpoint in endpoints_to_test:
        test_endpoint(endpoint)
        time.sleep(1)
    
    print("\n" + "="*50)
    print("🤖 Testing M1-M5 Agent Endpoints")
    print("="*50)
    
    # Test with sample data
    sample_request = {
        "company_id": "test-company",
        "task_description": "Test marketing analysis",
        "additional_context": "This is a test request"
    }
    
    for endpoint in agent_endpoints:
        test_endpoint(endpoint, method="POST", data=sample_request)
        time.sleep(2)  # Longer delay for AI endpoints
    
    print("\n🎉 Railway API Testing Complete!")
    print("💡 Update RAILWAY_BASE_URL variable with your actual Railway URL")

if __name__ == "__main__":
    main()
