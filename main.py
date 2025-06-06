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

# محرك CrewAI
class CrewAIEngine:
    def __init__(self):
        self.available = False
        
        try:
            from crewai import Agent, Task, Crew, Process
            from langchain_openai import ChatOpenAI
            from dotenv import load_dotenv
            self.available = True
            load_dotenv()
        except ImportError as e:
            print(f"⚠️ CrewAI not available: {e}")
        
        if self.available:
            try:
                # إعداد LLM
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    self.llm = ChatOpenAI(
                        model="gpt-4-turbo-preview",
                        temperature=0.7,
                        openai_api_key=api_key
                    )
                    logger.info("✅ CrewAI initialized with OpenAI GPT-4")
                else:
                    logger.warning("⚠️ OPENAI_API_KEY not found, using fallback")
                    self.available = False
            except Exception as e:
                logger.error(f"❌ CrewAI initialization failed: {e}")
                self.available = False
    
    def create_marketing_crew(self):
        """إنشاء فريق التسويق الرقمي"""
        if not self.available or not self.llm:
            return None
        
        try:
            # وكيل المحلل التسويقي
            analyst = Agent(
                role='محلل تسويق رقمي',
                goal='تحليل البيانات وتقديم رؤى تسويقية دقيقة',
                backstory="""أنت محلل تسويق رقمي خبير مع 10 سنوات من الخبرة في 
                تحليل البيانات والسوق. تجيد العربية والإنجليزية وتركز على تقديم 
                رؤى عملية وقابلة للتنفيذ.""",
                llm=self.llm,
                verbose=True,
                allow_delegation=False
            )
            
            # وكيل منشئ المحتوى
            content_creator = Agent(
                role='منشئ محتوى إبداعي',
                goal='إنشاء محتوى تسويقي جذاب ومناسب للثقافة العربية',
                backstory="""أنت منشئ محتوى إبداعي متخصص في التسويق الرقمي 
                للسوق العربي. تفهم التفاصيل الثقافية وتنشئ محتوى يتفاعل معه 
                الجمهور العربي بشكل إيجابي.""",
                llm=self.llm,
                verbose=True,
                allow_delegation=False
            )
            
            return {'analyst': analyst, 'content_creator': content_creator}
            
        except Exception as e:
            logger.error(f"❌ Failed to create marketing crew: {e}")
            return None
    
    def process_with_crewai(self, content: str, user_id: str) -> dict:
        """معالجة الرسالة باستخدام CrewAI"""
        try:
            crew_agents = self.create_marketing_crew()
            if not crew_agents:
                return None
            
            # إنشاء مهمة ديناميكية
            task = Task(
                description=f"""
                قم بتحليل هذا الطلب من المستخدم: "{content}"
                
                المطلوب:
                1. تحديد نوع الطلب (تحليل، إنشاء محتوى، استراتيجية، إلخ)
                2. تقديم إجابة شاملة ومفيدة بالعربية
                3. اقتراح خطوات عملية إن أمكن
                4. تقديم نصائح إضافية ذات صلة
                
                اجعل الرد موجهاً للسوق العربي ومناسباً ثقافياً.
                """,
                agent=crew_agents['analyst'],
                expected_output="رد تفصيلي باللغة العربية مع توصيات عملية"
            )
            
            # إنشاء وتشغيل الفريق
            crew = Crew(
                agents=[crew_agents['analyst'], crew_agents['content_creator']],
                tasks=[task],
                process=Process.sequential,
                verbose=True
            )
            
            result = crew.kickoff()
            
            return {
                "content": str(result),
                "intent_detected": "crewai_processed",
                "rich_components": [
                    {
                        "type": "ai_analysis",
                        "title": "🤖 تحليل مدعوم بالذكاء الاصطناعي",
                        "content": "تم إنتاج هذا الرد باستخدام فريق من وكلاء الذكاء الاصطناعي المتخصصين"
                    }
                ],
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "session_id": f"session_{user_id}"
            }
            
        except Exception as e:
            logger.error(f"❌ CrewAI processing failed: {e}")
            return None

# محرك المحادثة المُحدث
class EnhancedChatEngine:
    def __init__(self):
        self.crewai_engine = CrewAIEngine()
        
    def detect_intent(self, content: str) -> str:
        """كشف قصد المستخدم"""
        content_lower = content.lower()
        
        if any(word in content_lower for word in ['مرحبا', 'السلام', 'أهلا', 'hello', 'hi']):
            return "greeting"
        elif any(word in content_lower for word in ['تحليل', 'analysis', 'بيانات', 'data']):
            return "analysis_request"
        elif any(word in content_lower for word in ['محتوى', 'content', 'منشور', 'post']):
            return "content_creation"
        elif any(word in content_lower for word in ['استراتيجية', 'strategy', 'خطة', 'plan']):
            return "strategy_planning"
        elif any(word in content_lower for word in ['مساعدة', 'help', 'شرح', 'explain']):
            return "help_request"
        else:
            return "general_query"
    
    def get_rich_components(self, intent: str) -> List[Dict[str, str]]:
        """إنشاء مكونات تفاعلية حسب القصد"""
        if intent == "greeting":
            return [
                {
                    "type": "quick_actions",
                    "title": "إجراءات سريعة",
                    "buttons": [
                        {"text": "📊 تحليل موقعي", "action": "website_analysis"},
                        {"text": "🔗 ربط منصة", "action": "connect_platform"},
                        {"text": "📈 إنشاء حملة", "action": "create_campaign"},
                        {"text": "👁️ تحليل منافسين", "action": "competitor_analysis"}
                    ]
                }
            ]
        elif intent == "analysis_request":
            return [
                {
                    "type": "analysis_tools",
                    "title": "أدوات التحليل",
                    "buttons": [
                        {"text": "📈 Google Analytics", "action": "ga_analysis"},
                        {"text": "🔍 SEO Analysis", "action": "seo_analysis"},
                        {"text": "📱 Social Media", "action": "social_analysis"}
                    ]
                }
            ]
        else:
            return [
                {
                    "type": "help_menu",
                    "title": "كيف يمكنني مساعدتك؟",
                    "buttons": [
                        {"text": "💡 اقتراحات", "action": "suggestions"},
                        {"text": "📚 دليل الاستخدام", "action": "guide"},
                        {"text": "🎯 أمثلة", "action": "examples"}
                    ]
                }
            ]
    
    def generate_simple_response(self, content: str, intent: str) -> str:
        """إنشاء رد بسيط بدون CrewAI"""
        responses = {
            "greeting": "مرحباً! 👋 أنا مورفو، مساعدك الذكي في التسويق الرقمي. كيف يمكنني مساعدتك اليوم؟",
            "analysis_request": "🔍 ممتاز! يمكنني مساعدتك في تحليل البيانات. ما نوع التحليل الذي تحتاجه؟",
            "content_creation": "✍️ أحب إنشاء المحتوى! ما نوع المحتوى الذي تريد إنشاءه؟",
            "strategy_planning": "📋 دعني أساعدك في وضع استراتيجية فعالة. ما هدفك الأساسي؟",
            "help_request": "🤝 أنا هنا للمساعدة! اشرح لي ما تحتاجه وسأبذل قصارى جهدي لمساعدتك.",
            "general_query": "🤔 فهمت سؤالك. دعني أفكر في أفضل طريقة لمساعدتك..."
        }
        
        return responses.get(intent, "شكراً لتواصلك معي. كيف يمكنني مساعدتك بشكل أفضل؟")
    
    def process_message(self, content: str, user_id: str) -> dict:
        """معالجة الرسالة الرئيسية"""
        intent = self.detect_intent(content)
        
        # محاولة استخدام CrewAI أولاً
        if self.crewai_engine.available and intent in ["analysis_request", "content_creation", "strategy_planning"]:
            crewai_result = self.crewai_engine.process_with_crewai(content, user_id)
            if crewai_result:
                return crewai_result
        
        # العودة للرد البسيط
        simple_response = self.generate_simple_response(content, intent)
        rich_components = self.get_rich_components(intent)
        
        return {
            "content": simple_response,
            "intent_detected": intent,
            "rich_components": rich_components,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "session_id": f"session_{user_id}"
        }

# إنشاء محرك المحادثة المحسن
chat_engine = EnhancedChatEngine()

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
