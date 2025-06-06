#!/usr/bin/env python3
"""
🚀 Morvo AI Chat API - Clean Production Build
نسخة نظيفة تماماً لضمان نجاح النشر على Railway
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
import logging
import asyncio
from datetime import datetime
import os

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# إنشاء التطبيق
app = FastAPI(
    title="🤖 Morvo AI - Chat API",
    description="منصة الذكاء الاصطناعي للتسويق الرقمي",
    version="3.0.0"
)

# إعداد CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# النماذج
class ChatMessage(BaseModel):
    content: str
    user_id: str
    session_id: str

class ChatResponse(BaseModel):
    content: str
    intent_detected: Optional[str] = None
    rich_components: List[Dict] = []
    timestamp: str
    user_id: str
    session_id: str

# إدارة الاتصالات
active_connections: Dict[str, WebSocket] = {}

# المحرك البسيط للمحادثة
class SimpleChatEngine:
    def process_message(self, content: str, user_id: str) -> Dict:
        """معالجة الرسائل بشكل بسيط"""
        
        # اكتشاف القصد
        intent = "greeting" if any(word in content.lower() for word in ["مرحبا", "السلام", "hello", "hi"]) else "general"
        
        # إنشاء الرد
        if intent == "greeting":
            response_content = f"مرحباً! 👋 أنا مورفو، مساعدك الذكي في التسويق الرقمي. كيف يمكنني مساعدتك اليوم؟"
            components = [{
                "type": "quick_actions",
                "title": "إجراءات سريعة",
                "buttons": [
                    {"text": "📊 تحليل موقعي", "action": "website_analysis"},
                    {"text": "🔗 ربط منصة", "action": "connect_platform"},
                    {"text": "📈 إنشاء حملة", "action": "create_campaign"},
                    {"text": "👁️ تحليل منافسين", "action": "competitor_analysis"}
                ]
            }]
        else:
            response_content = f"شكراً لرسالتك! أنا هنا لمساعدتك في التسويق الرقمي. يمكنني مساعدتك في تحليل موقعك، ربط منصاتك، أو إنشاء حملات تسويقية."
            components = []
        
        return {
            "content": response_content,
            "intent_detected": intent,
            "rich_components": components,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "session_id": f"session_{user_id}"
        }

# إنشاء المحرك
chat_engine = SimpleChatEngine()

# الصفحة الرئيسية
@app.get("/")
async def root():
    """الصفحة الرئيسية"""
    return {
        "service": "🤖 Morvo AI - Clean Build",
        "status": "running",
        "version": "3.0.0",
        "timestamp": datetime.now().isoformat(),
        "message": "Clean production build for Railway deployment"
    }

# فحص الصحة
@app.get("/health")
async def health_check():
    """فحص صحة الخادم"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0.0",
        "environment": "Railway Production",
        "services": {
            "fastapi": "active",
            "websocket": f"{len(active_connections)} connections",
            "chat_engine": "active"
        },
        "port": os.getenv("PORT", "8000")
    }

# API الرسائل
@app.post("/api/v2/chat/message", response_model=ChatResponse)
async def chat_message(message: ChatMessage):
    """معالجة رسائل المحادثة"""
    try:
        # معالجة الرسالة
        response = chat_engine.process_message(
            content=message.content,
            user_id=message.user_id
        )
        
        # إشعار عبر WebSocket إن وجد
        if message.user_id in active_connections:
            try:
                await active_connections[message.user_id].send_text(
                    json.dumps({"type": "chat_response", "data": response})
                )
            except:
                pass
        
        return ChatResponse(**response)
        
    except Exception as e:
        logger.error(f"خطأ في معالجة الرسالة: {e}")
        raise HTTPException(status_code=500, detail=f"خطأ في المعالجة: {str(e)}")

# WebSocket
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """نقطة WebSocket للاتصال المباشر"""
    await websocket.accept()
    active_connections[user_id] = websocket
    
    try:
        # رسالة ترحيب
        welcome_msg = {
            "type": "connection_established",
            "message": f"مرحباً {user_id}! تم تأسيس الاتصال بنجاح.",
            "timestamp": datetime.now().isoformat()
        }
        await websocket.send_text(json.dumps(welcome_msg))
        
        # استقبال الرسائل
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # معالجة الرسالة
            if message_data.get("type") == "chat_message":
                response = chat_engine.process_message(
                    content=message_data.get("content", ""),
                    user_id=user_id
                )
                await websocket.send_text(json.dumps({
                    "type": "chat_response",
                    "data": response
                }))
                
    except WebSocketDisconnect:
        logger.info(f"User {user_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for {user_id}: {e}")
    finally:
        if user_id in active_connections:
            del active_connections[user_id]

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
