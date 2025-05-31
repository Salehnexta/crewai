#!/usr/bin/env python3
"""
Simple test script for Morvo AI Platform
"""
import os
from dotenv import load_dotenv
from fastapi import FastAPI

# Load environment variables
load_dotenv()

# Test environment variables
print("Testing Environment Variables:")
print(f"OPENAI_API_KEY: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Missing'}")
print(f"SUPABASE_URL: {'✅ Set' if os.getenv('SUPABASE_URL') else '❌ Missing'}")
print(f"SUPABASE_KEY: {'✅ Set' if os.getenv('SUPABASE_KEY') else '❌ Missing'}")

# Create minimal FastAPI app
app = FastAPI(
    title="Morvo AI Test API",
    description="Testing Morvo AI Platform",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "🚀 Morvo AI Platform is running!"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "morvo-ai-platform",
        "openai_configured": bool(os.getenv('OPENAI_API_KEY')),
        "supabase_configured": bool(os.getenv('SUPABASE_URL'))
    }

@app.get("/test")
async def test_endpoint():
    return {
        "message": "✅ Test endpoint working!",
        "platform": "Morvo AI Marketing Platform",
        "status": "operational"
    }

if __name__ == "__main__":
    import uvicorn
    print("\n🚀 Starting Morvo AI Test Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
