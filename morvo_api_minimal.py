#!/usr/bin/env python3
"""
🔧 Minimal Morvo API for Railway Deployment Testing
هذا اختبار مبسط للتأكد من أن Railway يمكنه نشر FastAPI بشكل أساسي
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

# إنشاء التطبيق
app = FastAPI(
    title="🔧 Morvo API - Minimal Test",
    description="اختبار مبسط لنشر Railway",
    version="1.0.0"
)

# إعداد CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """الصفحة الرئيسية"""
    return {
        "service": "🔧 Morvo AI - Minimal Test",
        "status": "working",
        "timestamp": datetime.now().isoformat(),
        "message": "Minimal FastAPI deployment test"
    }

@app.get("/health")
async def health_check():
    """فحص الصحة المبسط"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "environment": "Railway Test",
        "port": os.getenv("PORT", "8000"),
        "message": "Basic health check working"
    }

@app.get("/test")
async def test_endpoint():
    """نقطة اختبار إضافية"""
    return {
        "test": "success",
        "timestamp": datetime.now().isoformat(),
        "message": "Test endpoint is working"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
