#!/usr/bin/env python3
"""
Quick startup test for Railway deployment
"""
import sys
import os

def test_imports():
    """Test if all required imports work"""
    try:
        print("Testing FastAPI imports...")
        from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, BackgroundTasks
        from fastapi.middleware.cors import CORSMiddleware
        from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
        print("✅ FastAPI imports successful")
        
        print("Testing Pydantic imports...")
        from pydantic import BaseModel, Field
        print("✅ Pydantic imports successful")
        
        print("Testing standard library imports...")
        import asyncio, json, logging, uvicorn
        from datetime import datetime, timedelta
        from pathlib import Path
        print("✅ Standard library imports successful")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_app_creation():
    """Test if the app can be created"""
    try:
        print("Testing app creation...")
        # Try to import the app
        from morvo_api_v2 import app
        print("✅ App creation successful")
        print(f"App type: {type(app)}")
        return True
    except Exception as e:
        print(f"❌ App creation error: {e}")
        return False

def main():
    print("🔧 RAILWAY DEPLOYMENT STARTUP TEST")
    print("=" * 50)
    
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print(f"PORT environment variable: {os.environ.get('PORT', 'Not set')}")
    print()
    
    # Test imports
    if not test_imports():
        sys.exit(1)
    
    print()
    
    # Test app creation
    if not test_app_creation():
        sys.exit(1)
    
    print()
    print("🎉 All startup tests passed!")
    print("✅ Ready for Railway deployment")

if __name__ == "__main__":
    main()
