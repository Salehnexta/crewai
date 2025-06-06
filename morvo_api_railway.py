#!/usr/bin/env python3
"""
Morvo AI v2.0 - Railway Production Server
Simplified version for stable Railway deployment
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import asyncio
import json
import logging
import os
import uvicorn
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="🤖 مورفو AI - Marketing API v2.0",
    description="منصة الذكاء الاصطناعي للتسويق الرقمي مع محادثة ذكية",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data models
class ChatMessage(BaseModel):
    content: str
    user_id: str = "user"
    session_id: str = "default"
    metadata: Optional[Dict] = {}

class ChatResponse(BaseModel):
    content: str
    intent_detected: Optional[str] = None
    rich_components: Optional[List[Dict]] = []
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

# Active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

# Simple intent detection for Arabic
def detect_intent(text: str) -> str:
    """Simple Arabic intent detection"""
    text_lower = text.lower()
    
    if any(word in text_lower for word in ["مرحبا", "أهلا", "السلام"]):
        return "greeting"
    elif any(word in text_lower for word in ["تحليل", "موقع", "دراسة"]):
        return "website_analysis"
    elif any(word in text_lower for word in ["منصة", "ربط", "شوبيفاي", "سلة"]):
        return "platform_connection"
    elif any(word in text_lower for word in ["مساعدة", "كيف", "ماذا"]):
        return "help"
    else:
        return "general"

# Generate response based on intent
def generate_response(message: str, intent: str) -> ChatResponse:
    """Generate appropriate response based on detected intent"""
    
    responses = {
        "greeting": "مرحباً بك في مورفو AI! 👋 أنا مساعدتك الذكية للتسويق الرقمي. كيف يمكنني مساعدتك اليوم؟",
        "website_analysis": "رائع! يمكنني تحليل موقعك الإلكتروني وتقديم توصيات لتحسين الأداء. شاركني رابط الموقع وسأبدأ التحليل فوراً! 🔍",
        "platform_connection": "ممتاز! يمكنني مساعدتك في ربط منصتك التجارية (سلة، شوبيفاي، زد) لتحليل أفضل. أي منصة تستخدم؟ 🛒",
        "help": "بالطبع! أنا هنا لمساعدتك في:\n• تحليل المواقع الإلكترونية 📊\n• ربط المنصات التجارية 🔗\n• تحسين استراتيجيات التسويق 📈\n• تحليل المنافسين 🎯\n\nما الذي تحتاج إليه تحديداً؟",
        "general": "شكراً لرسالتك! يمكنني مساعدتك في تحسين تسويقك الرقمي. هل تريد تحليل موقعك أم ربط منصة تجارية؟ 🚀"
    }
    
    content = responses.get(intent, responses["general"])
    
    # Add rich components based on intent
    rich_components = []
    if intent == "website_analysis":
        rich_components = [
            {
                "type": "button",
                "text": "بدء تحليل الموقع",
                "action": "start_analysis"
            }
        ]
    elif intent == "platform_connection":
        rich_components = [
            {
                "type": "buttons",
                "options": [
                    {"text": "سلة", "value": "salla"},
                    {"text": "شوبيفاي", "value": "shopify"},
                    {"text": "زد", "value": "zid"}
                ]
            }
        ]
    
    return ChatResponse(
        content=content,
        intent_detected=intent,
        rich_components=rich_components
    )

# Routes
@app.get("/", response_class=HTMLResponse)
async def root():
    """Welcome page with server info"""
    return """
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>مورفو AI - Railway Server</title>
        <style>
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; color: white; }
            .container { max-width: 800px; margin: 0 auto; text-align: center; }
            .card { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border-radius: 20px; padding: 30px; margin: 20px 0; border: 1px solid rgba(255,255,255,0.2); }
            .status { color: #4ade80; font-size: 1.2em; margin: 10px 0; }
            .endpoint { background: rgba(0,0,0,0.2); padding: 15px; border-radius: 10px; margin: 10px 0; font-family: monospace; }
            .btn { display: inline-block; padding: 12px 24px; background: #3b82f6; color: white; text-decoration: none; border-radius: 8px; margin: 5px; transition: transform 0.2s; }
            .btn:hover { transform: translateY(-2px); }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="card">
                <h1>🤖 مورفو AI v2.0</h1>
                <p>منصة الذكاء الاصطناعي للتسويق الرقمي</p>
                <div class="status">✅ الخادم يعمل بنجاح على Railway</div>
            </div>
            
            <div class="card">
                <h2>🔗 نقاط الاتصال المتاحة</h2>
                <div class="endpoint">GET /health - فحص صحة الخادم</div>
                <div class="endpoint">POST /api/v2/chat/message - المحادثة الذكية</div>
                <div class="endpoint">WS /ws/{user_id} - اتصال WebSocket مباشر</div>
                <div class="endpoint">GET /docs - مستندات API</div>
            </div>
            
            <div class="card">
                <h2>🛠️ الروابط السريعة</h2>
                <a href="/docs" class="btn">📚 مستندات API</a>
                <a href="/health" class="btn">💚 فحص الصحة</a>
                <a href="/redoc" class="btn">📖 ReDoc</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "message": "مورفو AI يعمل بصحة ممتازة! 🚀",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "server": "Railway Production"
    }

@app.post("/api/v2/chat/message")
async def chat_message(message: ChatMessage):
    """Process chat message with intent detection"""
    try:
        intent = detect_intent(message.content)
        response = generate_response(message.content, intent)
        
        logger.info(f"Chat message processed - Intent: {intent}")
        return response
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    connection_id = f"{user_id}_{int(datetime.now().timestamp())}"
    active_connections[connection_id] = websocket
    
    logger.info(f"WebSocket connected: {user_id}")
    
    try:
        # Send welcome message
        await websocket.send_json({
            "type": "welcome",
            "message": "مرحباً! أنا مورفو، مساعدتك الذكية في التسويق الرقمي 👋",
            "timestamp": datetime.now().isoformat()
        })
        
        while True:
            # Receive message
            data = await websocket.receive_json()
            
            # Process message
            intent = detect_intent(data.get("content", ""))
            response = generate_response(data.get("content", ""), intent)
            
            # Send response
            await websocket.send_json({
                "type": "message",
                "content": response.content,
                "intent_detected": response.intent_detected,
                "rich_components": response.rich_components,
                "timestamp": datetime.now().isoformat()
            })
            
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {user_id}")
        del active_connections[connection_id]
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        if connection_id in active_connections:
            del active_connections[connection_id]

# Available platforms endpoint
@app.get("/api/v2/platforms/available")
async def get_available_platforms():
    """Get list of available platforms for connection"""
    return {
        "platforms": [
            {"id": "salla", "name": "سلة", "type": "ecommerce", "supported": True},
            {"id": "shopify", "name": "شوبيفاي", "type": "ecommerce", "supported": True},
            {"id": "zid", "name": "زد", "type": "ecommerce", "supported": True},
            {"id": "woocommerce", "name": "ووكومرس", "type": "ecommerce", "supported": True},
            {"id": "google_analytics", "name": "Google Analytics", "type": "analytics", "supported": True},
            {"id": "facebook_ads", "name": "Facebook Ads", "type": "advertising", "supported": True}
        ]
    }

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Morvo AI v2.0 Railway Server Started Successfully!")
    logger.info("✅ All endpoints active and ready")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
