# 🤖 **مورفو AI - FastAPI Integration Server v2.0**
# Server محدث مع Website Scraping + Chat Engine + Intent Detection

from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
import asyncio
import json
import logging
from datetime import datetime, timedelta
import os
from pathlib import Path
import uvicorn
import warnings

# إزالة التحذيرات غير المهمة
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

# إعداد التسجيل المحسن أولاً
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('morvo_api.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# مورفو imports
try:
    from morvo_website_scraper import MorvoWebsiteScraper, WebsiteAnalysisResult
    from crewai import Agent, Task, Crew
    from crewai_tools import ScrapeWebsiteTool
    logger.info("✅ تم تحميل مورفو modules بنجاح")
except Exception as e:
    logger.error(f"❌ خطأ في تحميل المورفو modules: {e}")
    # في حالة فقدان المورفو modules، استخدم fallback
    MorvoWebsiteScraper = None
    WebsiteAnalysisResult = None

# إعداد FastAPI
app = FastAPI(
    title="🤖 مورفو AI - Marketing Companion API v2.0",
    description="منصة الذكاء الاصطناعي للتسويق الرقمي مع محادثة ذكية وتحليل المواقع",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# إعداد CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # في الإنتاج، حدد المواقع المسموحة
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# نماذج البيانات
class ChatMessage(BaseModel):
    content: str
    user_id: str
    session_id: str
    message_type: str = "user"
    metadata: Optional[Dict] = {}

class ChatResponse(BaseModel):
    content: str
    message_type: str = "assistant"
    rich_components: Optional[List[Dict]] = []
    intent_detected: Optional[str] = None
    confidence_score: Optional[float] = None
    next_actions: Optional[List[str]] = []

class WebsiteAnalysisRequest(BaseModel):
    url: str
    organization_id: str
    analysis_type: str = "full"  # full, seo, competitors, quick

class OnboardingStep(BaseModel):
    user_id: str
    step_number: int
    step_data: Dict
    completed: bool = False

class PlatformConnectionRequest(BaseModel):
    platform_type: str
    connection_data: Dict
    organization_id: str

# متغيرات عامة
website_scraper = MorvoWebsiteScraper()
active_connections: Dict[str, WebSocket] = {}

# ============================================================================
# 🤖 **محرك المحادثة الذكي مع Intent Detection**
# ============================================================================

class MorvoConversationEngine:
    """محرك المحادثة الذكي لمورفو"""
    
    def __init__(self):
        self.intent_classifier = self._create_intent_classifier()
        self.response_generator = self._create_response_generator()
        self.onboarding_manager = self._create_onboarding_manager()
        
    def _create_intent_classifier(self):
        """🎯 وكيل تصنيف القصد"""
        return Agent(
            role="Arabic Intent Classifier",
            goal="فهم قصد المستخدم من الرسائل العربية وتصنيفها بدقة",
            backstory="""أنت خبير في تحليل اللغة العربية الطبيعية وفهم احتياجات المستخدمين في التسويق الرقمي.
            تستطيع تحديد القصد من الرسائل العربية بدقة عالية وتصنيفها إلى فئات مفيدة.
            خبرتك تشمل: طلبات التحليل، ربط المنصات، إنشاء الحملات، تحليل المنافسين، والاستفسارات العامة.""",
            tools=[],
            verbose=True,
            allow_delegation=False
        )
    
    def _create_response_generator(self):
        """📝 وكيل توليد الردود"""
        return Agent(
            role="Morvo Response Generator",
            goal="توليد ردود ذكية ومفيدة ومحادثية باللغة العربية",
            backstory="""أنت مورفو، المساعد الذكي للتسويق الرقمي. تتحدث بالعربية بطريقة ودودة ومحترفة.
            تقدم المساعدة في التسويق الرقمي، تحليل البيانات، إدارة الحملات، وربط المنصات.
            أسلوبك محادثي وودود، وتقدم معلومات مفيدة مع اقتراحات عملية.""",
            tools=[],
            verbose=True,
            allow_delegation=False
        )
    
    def _create_onboarding_manager(self):
        """👋 مدير عملية التسجيل"""
        return Agent(
            role="Onboarding Specialist",
            goal="إرشاد المستخدمين الجدد خلال عملية التسجيل والإعداد بطريقة محادثية",
            backstory="""خبير في تجربة المستخدم وإعداد الحسابات الجديدة للتسويق الرقمي.
            تساعد المستخدمين في فهم المنصة، ربط حساباتهم، وإعداد أول حملة تسويقية.
            أسلوبك صبور وودود ومفصل في الشرح.""",
            tools=[],
            verbose=True,
            allow_delegation=False
        )

    async def process_message(self, message: ChatMessage) -> ChatResponse:
        """معالجة رسالة المستخدم وإنتاج رد ذكي"""
        
        try:
            # منطق بسيط للبداية - يمكن تطويره لاحقاً
            content = message.content.lower().strip()
            
            # تحديد القصد بطريقة بسيطة
            if any(word in content for word in ["مرحبا", "السلام", "أهلا", "تحية"]):
                intent = "greeting"
                response_content = "مرحباً! 👋 أنا مورفو، مساعدتك الذكية في التسويق الرقمي. كيف يمكنني مساعدتك اليوم؟"
                components = [
                    {
                        "type": "quick_actions",
                        "title": "إجراءات سريعة",
                        "buttons": [
                            {"text": "📊 تحليل موقعي", "action": "website_analysis"},
                            {"text": "🔗 ربط منصة", "action": "connect_platform"},
                            {"text": "📈 إنشاء حملة", "action": "create_campaign"},
                            {"text": "🎯 تحليل منافسين", "action": "competitor_analysis"}
                        ]
                    }
                ]
                
            elif any(word in content for word in ["موقع", "تحليل", "سايت", "website"]):
                intent = "website_analysis"
                response_content = "ممتاز! 🔍 أستطيع تحليل موقعك الإلكتروني بشكل شامل. أرسل لي رابط الموقع وسأقوم بتحليل:\n\n• نوع العمل والصناعة\n• تحليل SEO شامل\n• التوافق مع السوق السعودي\n• تحليل المنافسين\n• توصيات للتحسين"
                components = []
                
            elif any(word in content for word in ["ربط", "منصة", "شوبيفاي", "سلة", "زد"]):
                intent = "platform_connection"
                response_content = "رائع! 🔗 أستطيع مساعدتك في ربط منصاتك التجارية. أي منصة تريد ربطها؟"
                components = [
                    {
                        "type": "platform_selection",
                        "title": "اختر المنصة",
                        "options": [
                            {"text": "Shopify", "value": "shopify"},
                            {"text": "Salla سلة", "value": "salla"},
                            {"text": "Zid زد", "value": "zid"},
                            {"text": "WooCommerce", "value": "woocommerce"}
                        ]
                    }
                ]
                
            elif any(word in content for word in ["حملة", "إعلان", "تسويق", "campaign"]):
                intent = "campaign_creation"
                response_content = "ممتاز! 📈 دعنا ننشئ حملة تسويقية ذكية. أحتاج لمعرفة:\n\n• نوع المنتج أو الخدمة\n• الجمهور المستهدف\n• الميزانية المتاحة\n• أهداف الحملة"
                components = []
                
            else:
                intent = "general_question"
                response_content = "أفهم أنك تحتاج مساعدة في التسويق الرقمي. 🤔 هل يمكنك توضيح أكثر كيف يمكنني مساعدتك؟"
                components = []
            
            return ChatResponse(
                content=response_content,
                intent_detected=intent,
                confidence_score=0.85,
                rich_components=components,
                next_actions=["يمكنك سؤالي عن أي شيء متعلق بالتسويق الرقمي"]
            )
            
        except Exception as e:
            logger.error(f"خطأ في معالجة المحادثة: {str(e)}")
            return ChatResponse(
                content="عذراً، حدث خطأ في فهم رسالتك. هل يمكنك إعادة الصياغة؟",
                intent_detected="error",
                confidence_score=0.0
            )

# إنشاء محرك المحادثة
conversation_engine = MorvoConversationEngine()

# ============================================================================
# 🕷️ **Website Scraping & Analysis Endpoints**
# ============================================================================

@app.post("/api/v2/website/analyze", response_model=Dict)
async def analyze_website(
    request: WebsiteAnalysisRequest,
    background_tasks: BackgroundTasks
) -> Dict:
    """🔍 تحليل موقع إلكتروني شامل"""
    
    try:
        logger.info(f"🚀 بدء تحليل الموقع: {request.url}")
        
        # بدء التحليل في الخلفية
        background_tasks.add_task(
            perform_website_analysis,
            request.url,
            request.organization_id,
            request.analysis_type
        )
        
        return {
            "status": "تم بدء التحليل",
            "message": "جاري تحليل الموقع، ستصلك النتائج قريباً",
            "url": request.url,
            "estimated_time": "2-5 دقائق",
            "analysis_id": f"analysis_{int(datetime.now().timestamp())}"
        }
        
    except Exception as e:
        logger.error(f"❌ خطأ في بدء تحليل الموقع: {str(e)}")
        raise HTTPException(status_code=500, detail=f"خطأ في التحليل: {str(e)}")

async def perform_website_analysis(url: str, org_id: str, analysis_type: str):
    """تنفيذ تحليل الموقع في الخلفية"""
    
    try:
        logger.info(f"🔍 تنفيذ تحليل الموقع: {url}")
        
        # تنفيذ التحليل
        analysis_result = await website_scraper.analyze_website(url)
        
        # حفظ النتائج في قاعدة البيانات (ستتم إضافة Supabase لاحقاً)
        logger.info(f"✅ اكتمل تحليل الموقع: {url}")
        
        # إرسال إشعار للمستخدم عبر WebSocket
        await notify_analysis_complete(org_id, analysis_result)
        
    except Exception as e:
        logger.error(f"❌ خطأ في تحليل الموقع {url}: {str(e)}")

async def notify_analysis_complete(org_id: str, result: WebsiteAnalysisResult):
    """إشعار المستخدم باكتمال التحليل"""
    
    try:
        # البحث عن اتصالات WebSocket نشطة للمؤسسة
        for connection_id, websocket in active_connections.items():
            if org_id in connection_id:
                await websocket.send_json({
                    "type": "website_analysis_complete",
                    "data": {
                        "title": result.title,
                        "business_type": result.business_type,
                        "confidence_score": result.confidence_score,
                        "recommendations_count": len(result.recommendations)
                    },
                    "message": "🎉 اكتمل تحليل موقعك! إليك النتائج:",
                    "timestamp": datetime.now().isoformat()
                })
    except Exception as e:
        logger.error(f"خطأ في إرسال الإشعار: {str(e)}")

@app.get("/api/v2/website/analysis/{analysis_id}")
async def get_analysis_result(analysis_id: str) -> Dict:
    """استرجاع نتائج تحليل الموقع"""
    
    try:
        # هنا ستتم استراجع النتائج من قاعدة البيانات
        return {
            "analysis_id": analysis_id,
            "status": "مكتمل",
            "results": {
                "title": "متجر المثال",
                "business_type": "تجارة إلكترونية",
                "confidence_score": 0.92
            }
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail="تحليل غير موجود")

# ============================================================================
# 💬 **Chat & Conversation Endpoints**
# ============================================================================

@app.post("/api/v2/chat/message", response_model=ChatResponse)
async def send_chat_message(message: ChatMessage) -> ChatResponse:
    """💬 إرسال رسالة لمورفو والحصول على رد ذكي"""
    
    try:
        logger.info(f"💬 رسالة جديدة من {message.user_id}: {message.content[:50]}...")
        
        # معالجة الرسالة مع محرك المحادثة
        response = await conversation_engine.process_message(message)
        
        # حفظ المحادثة في قاعدة البيانات (ستتم إضافة Supabase لاحقاً)
        
        return response
        
    except Exception as e:
        logger.error(f"❌ خطأ في معالجة رسالة الشات: {str(e)}")
        raise HTTPException(status_code=500, detail=f"خطأ في المحادثة: {str(e)}")

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """🔄 اتصال WebSocket للمحادثة المباشرة"""
    
    await websocket.accept()
    connection_id = f"{user_id}_{int(datetime.now().timestamp())}"
    active_connections[connection_id] = websocket
    
    try:
        # رسالة ترحيب
        await websocket.send_json({
            "type": "welcome",
            "message": "مرحباً! أنا مورفو، مساعدتك الذكية في التسويق الرقمي 👋",
            "timestamp": datetime.now().isoformat()
        })
        
        while True:
            # استقبال الرسائل
            data = await websocket.receive_json()
            
            # معالجة الرسالة
            message = ChatMessage(
                content=data.get("content", ""),
                user_id=user_id,
                session_id=data.get("session_id", ""),
                metadata=data.get("metadata", {})
            )
            
            # الحصول على رد من مورفو
            response = await conversation_engine.process_message(message)
            
            # إرسال الرد
            await websocket.send_json({
                "type": "message",
                "content": response.content,
                "rich_components": response.rich_components,
                "intent_detected": response.intent_detected,
                "timestamp": datetime.now().isoformat()
            })
            
    except WebSocketDisconnect:
        logger.info(f"انقطع اتصال WebSocket: {user_id}")
        del active_connections[connection_id]
    except Exception as e:
        logger.error(f"خطأ في WebSocket: {str(e)}")
        if connection_id in active_connections:
            del active_connections[connection_id]

# ============================================================================
# 🎯 **Onboarding & User Setup Endpoints**
# ============================================================================

@app.post("/api/v2/onboarding/start")
async def start_onboarding(user_data: Dict) -> Dict:
    """👋 بدء عملية التسجيل للمستخدم الجديد"""
    
    try:
        return {
            "message": "مرحباً بك في مورفو! دعنا نبدأ رحلتك في التسويق الرقمي",
            "current_step": 1,
            "steps": [
                "التعارف وفهم نوع العمل",
                "ربط المنصات والحسابات", 
                "تحليل الموقع الإلكتروني",
                "إعداد أول حملة تسويقية",
                "تفعيل التحليلات والتقارير"
            ],
            "next_questions": [
                "ما اسم شركتك أو مشروعك؟",
                "في أي مجال تعملون؟"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v2/onboarding/step")
async def complete_onboarding_step(step: OnboardingStep) -> Dict:
    """✅ إتمام خطوة في عملية التسجيل"""
    
    try:
        # معالجة بيانات الخطوة
        # حفظ في قاعدة البيانات
        
        next_step = step.step_number + 1
        
        return {
            "step_completed": step.step_number,
            "next_step": next_step,
            "message": f"ممتاز! تم إتمام الخطوة {step.step_number}",
            "progress_percentage": (step.step_number / 5) * 100
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# 🔗 **Platform Connection Endpoints**
# ============================================================================

@app.get("/api/v2/platforms/available")
async def get_available_platforms() -> Dict:
    """📋 استعراض المنصات المتاحة للربط"""
    
    try:
        return {
            "platforms": [
                {
                    "id": "salla",
                    "name": "سلة",
                    "type": "ecommerce",
                    "description": "منصة التجارة الإلكترونية الرائدة في السعودية",
                    "logo": "https://salla.sa/favicon.ico",
                    "supported_features": ["products", "orders", "customers", "analytics"],
                    "setup_difficulty": "easy"
                },
                {
                    "id": "shopify", 
                    "name": "Shopify",
                    "type": "ecommerce",
                    "description": "منصة التجارة الإلكترونية العالمية",
                    "logo": "https://shopify.com/favicon.ico", 
                    "supported_features": ["products", "orders", "customers", "analytics", "apps"],
                    "setup_difficulty": "medium"
                },
                {
                    "id": "zid",
                    "name": "زد",
                    "type": "ecommerce", 
                    "description": "منصة التجارة الإلكترونية السعودية",
                    "logo": "https://zid.sa/favicon.ico",
                    "supported_features": ["products", "orders", "customers"],
                    "setup_difficulty": "easy"
                },
                {
                    "id": "google_analytics",
                    "name": "Google Analytics",
                    "type": "analytics",
                    "description": "تحليلات مواقع الويب والتطبيقات",
                    "logo": "https://analytics.google.com/favicon.ico",
                    "supported_features": ["website_analytics", "conversion_tracking", "audience_insights"],
                    "setup_difficulty": "medium"
                },
                {
                    "id": "facebook_ads",
                    "name": "Facebook Ads", 
                    "type": "advertising",
                    "description": "إعلانات فيسبوك وإنستقرام",
                    "logo": "https://facebook.com/favicon.ico",
                    "supported_features": ["campaigns", "audiences", "reporting"],
                    "setup_difficulty": "hard"
                },
                {
                    "id": "google_ads",
                    "name": "Google Ads",
                    "type": "advertising", 
                    "description": "إعلانات محرك البحث جوجل",
                    "logo": "https://ads.google.com/favicon.ico",
                    "supported_features": ["campaigns", "keywords", "reporting"],
                    "setup_difficulty": "hard"
                }
            ],
            "categories": {
                "ecommerce": "منصات التجارة الإلكترونية",
                "analytics": "منصات التحليلات", 
                "advertising": "منصات الإعلانات"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v2/platforms/connect")
async def connect_platform(request: PlatformConnectionRequest) -> Dict:
    """🔗 ربط منصة تجارية جديدة"""
    
    try:
        platform_type = request.platform_type.lower()
        
        if platform_type == "shopify":
            return {
                "status": "success",
                "message": "تم ربط متجر Shopify بنجاح!",
                "platform": "Shopify",
                "next_steps": [
                    "سنبدأ في جمع بيانات المبيعات",
                    "تحليل أداء المنتجات",
                    "إعداد تحليلات العملاء"
                ]
            }
        elif platform_type == "salla":
            return {
                "status": "success", 
                "message": "تم ربط متجر سلة بنجاح!",
                "platform": "Salla",
                "next_steps": [
                    "استيراد كتالوج المنتجات",
                    "تحليل بيانات العملاء",
                    "إعداد حملات تسويقية"
                ]
            }
        else:
            return {
                "status": "pending",
                "message": f"جاري العمل على دعم منصة {request.platform_type}",
                "estimated_completion": "قريباً"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v2/platforms/status/{org_id}")
async def get_platform_connections(org_id: str) -> Dict:
    """📊 استعراض حالة ربط المنصات"""
    
    try:
        return {
            "organization_id": org_id,
            "connected_platforms": [
                {
                    "platform": "Shopify",
                    "status": "connected",
                    "last_sync": "2024-01-15T10:30:00Z",
                    "data_points": 1250
                },
                {
                    "platform": "Google Analytics",
                    "status": "connected", 
                    "last_sync": "2024-01-15T09:15:00Z",
                    "data_points": 5670
                }
            ],
            "available_platforms": [
                "Salla", "Zid", "WooCommerce", "Magento", 
                "Facebook Ads", "Google Ads", "Instagram Business"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# 🔔 **Smart Alerts Endpoints**
# ============================================================================

@app.get("/api/v2/alerts/check/{organization_id}")
async def trigger_smart_alerts(organization_id: str, background_tasks: BackgroundTasks):
    """🔔 تشغيل فحص التنبيهات الذكية"""
    try:
        background_tasks.add_task(run_smart_alerts_check, organization_id)
        return {
            "status": "success",
            "message": "بدء فحص التنبيهات الذكية",
            "organization_id": organization_id,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"خطأ في تشغيل التنبيهات الذكية: {str(e)}")
        raise HTTPException(status_code=500, detail="فشل في تشغيل التنبيهات الذكية")

@app.get("/api/v2/alerts/status")
async def get_alerts_status():
    """📊 حالة نظام التنبيهات الذكية"""
    return {
        "status": "active",
        "last_check": datetime.now().isoformat(),
        "categories": [
            "seo_opportunity",
            "keyword_ranking", 
            "competitor_activity",
            "traffic_anomaly",
            "conversion_drop",
            "campaign_performance",
            "market_trend"
        ],
        "websocket_connections": len(active_connections),
        "message": "نظام التنبيهات الذكية يعمل بكفاءة"
    }

async def run_smart_alerts_check(organization_id: str):
    """تشغيل فحص التنبيهات الذكية في الخلفية"""
    try:
        # هذه دالة مساعدة لتشغيل Smart Alerts
        # سيتم استدعاء MorvoSmartAlertsV2 هنا
        logger.info(f"🔍 بدء فحص التنبيهات للمنظمة: {organization_id}")
        
        # إشعار المستخدمين عبر WebSocket
        notification = {
            "type": "alert_check_started",
            "message": "بدء فحص التنبيهات الذكية...",
            "organization_id": organization_id,
            "timestamp": datetime.now().isoformat()
        }
        
        # إرسال إشعار لجميع الاتصالات النشطة
        for connection_id, websocket in active_connections.items():
            try:
                await websocket.send_json(notification)
            except Exception as e:
                logger.error(f"خطأ في إرسال إشعار: {str(e)}")
                
    except Exception as e:
        logger.error(f"خطأ في فحص التنبيهات: {str(e)}")

# ============================================================================
# 📊 **Health Check & Status Endpoints**
# ============================================================================

@app.get("/health")
async def health_check():
    """✅ فحص صحة الخادم"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "services": {
            "chat_engine": "active",
            "website_scraper": "active",
            "websocket": f"{len(active_connections)} connections"
        }
    }

@app.get("/")
async def root():
    """📋 معلومات الخادم الرئيسية"""
    return {
        "service": "مورفو AI - Marketing Companion API",
        "version": "2.0.0",
        "description": "منصة الذكاء الاصطناعي للتسويق الرقمي مع محادثة ذكية",
        "docs": "/docs",
        "health": "/health",
        "websocket": "/ws/{user_id}",
        "features": [
            "💬 محادثة ذكية مع Intent Detection",
            "🕷️ تحليل المواقع الإلكترونية",
            "🔗 ربط المنصات التجارية",
            "📊 تحليلات وتقارير ذكية",
            "🎯 حملات تسويقية آلية"
        ]
    }

# ============================================================================
# 🚀 **تشغيل الخادم**
# ============================================================================

if __name__ == "__main__":
    # إعداد متغيرات البيئة للتطوير
    port = int(os.environ.get("PORT", 8000))
    
    logger.info("🚀 بدء تشغيل مورفو AI API Server v2.0...")
    logger.info(f"📍 الخادم يعمل على المنفذ: {port}")
    logger.info("📚 وثائق API متاحة على: /docs")
    logger.info("🔄 WebSocket متاح على: /ws/{user_id}")
    
    uvicorn.run(
        "morvo_api_v2:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
