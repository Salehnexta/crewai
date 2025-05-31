#!/usr/bin/env python3
"""
Minimal FastAPI test for Railway deployment
Tests basic functionality without complex imports
"""
from fastapi import FastAPI
import uvicorn
import os
from datetime import datetime

# Minimal FastAPI app
app = FastAPI(
    title="Minimal Test API",
    description="Basic Railway deployment test",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    """Minimal health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "port": os.environ.get("PORT", "8000")
    }

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Minimal API is working!"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "test_minimal_api:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
