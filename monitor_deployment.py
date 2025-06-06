#!/usr/bin/env python3
"""
Railway Deployment Monitor for Smart Alerts v2.0
Continuously checks for new deployment and smart alerts endpoints
"""

import time
import requests
import json
from datetime import datetime

BASE_URL = "https://crewai-production-d99a.up.railway.app"

def check_deployment_status():
    """Check if Railway has deployed latest version with smart alerts"""
    try:
        # Check health endpoint timestamp
        health_response = requests.get(f"{BASE_URL}/health", timeout=10)
        health_data = health_response.json()
        timestamp = health_data.get('timestamp')
        
        if timestamp:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            now = datetime.now()
            diff = now - dt.replace(tzinfo=None)
            seconds_ago = diff.total_seconds()
            
            print(f"📅 Health timestamp: {timestamp}")
            print(f"⏰ Last updated: {seconds_ago:.0f} seconds ago")
            
            # Check for smart alerts endpoints
            openapi_response = requests.get(f"{BASE_URL}/openapi.json", timeout=10)
            openapi_data = openapi_response.json()
            paths = openapi_data.get('paths', {})
            
            alerts_endpoints = [path for path in paths.keys() if 'alerts' in path]
            total_endpoints = len(paths)
            
            print(f"📊 Total endpoints: {total_endpoints}")
            
            if alerts_endpoints:
                print("✅ SMART ALERTS ENDPOINTS FOUND:")
                for path in alerts_endpoints:
                    methods = list(paths[path].keys())
                    print(f"  {path} - {methods}")
                print("🎉 DEPLOYMENT SUCCESSFUL!")
                
                # Test smart alerts endpoints
                print("\n🧪 Testing smart alerts endpoints...")
                
                # Test status endpoint
                status_response = requests.get(f"{BASE_URL}/api/v2/alerts/status", timeout=10)
                print(f"📋 Status endpoint: {status_response.status_code}")
                if status_response.status_code == 200:
                    print(f"   Response: {status_response.json()}")
                
                return True
            else:
                print("❌ Smart alerts endpoints still missing")
                if seconds_ago < 300:
                    print("🔄 Fresh deployment detected but endpoints not ready")
                else:
                    print("⏳ Still waiting for new deployment...")
                return False
                
    except Exception as e:
        print(f"❌ Error checking deployment: {e}")
        return False

def main():
    print("🔍 Starting Railway Deployment Monitor...")
    print("📡 Monitoring: Smart Alerts v2.0 deployment")
    print("🎯 Target: /api/v2/alerts/status and /api/v2/alerts/check/{org_id}")
    print("=" * 60)
    
    check_count = 0
    while True:
        check_count += 1
        print(f"\n🔍 Check #{check_count} - {datetime.now().strftime('%H:%M:%S')}")
        
        if check_deployment_status():
            print("\n✅ SMART ALERTS v2.0 SUCCESSFULLY DEPLOYED!")
            print("🎯 Ready for frontend integration and testing")
            break
        
        print("\n⏳ Waiting 30 seconds for next check...")
        time.sleep(30)

if __name__ == "__main__":
    main()
