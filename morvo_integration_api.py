"""
Morvo Integration API - FastAPI Backend for M1-M5 Marketing Agents
Designed for Railway deployment with MCP, Supabase, and Zapier integration
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import asyncio
import uvicorn
import os
from datetime import datetime
import json
import logging

from crews.morvo_marketing_crew import MorvoMarketingCrew

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Morvo AI Marketing Platform API",
    description="Advanced AI-powered marketing automation with M1-M5 specialized agents",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration for Railway deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your Railway deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize Morvo Marketing Crew
morvo_crew = MorvoMarketingCrew()

# Pydantic models for request/response
class CompanyInfo(BaseModel):
    name: str = Field(..., description="اسم الشركة")
    website: Optional[str] = Field(None, description="الموقع الإلكتروني")
    industry: str = Field(..., description="القطاع أو الصناعة")
    target_market: str = Field("السعودية ودول الخليج", description="السوق المستهدف")
    target_audience: Optional[str] = Field(None, description="الجمهور المستهدف")
    brand_message: Optional[str] = Field(None, description="رسالة العلامة التجارية")

class CampaignInfo(BaseModel):
    objective: str = Field(..., description="هدف الحملة")
    budget: str = Field(..., description="الميزانية المخصصة")
    duration: str = Field("30 يوم", description="مدة الحملة")
    platforms: str = Field("جميع المنصات", description="المنصات المستهدفة")

class MarketingRequest(BaseModel):
    company_info: CompanyInfo
    campaign_info: Optional[CampaignInfo] = None
    analysis_period: str = Field("آخر 30 يوم", description="فترة التحليل")

class AgentResponse(BaseModel):
    status: str
    message: str
    filename: Optional[str] = None
    timestamp: str
    agent_used: str

class IntegrationStatus(BaseModel):
    platform: str
    backend: str
    context_protocol: str
    agents_count: int
    apis_connected: List[str]
    deployment_status: str

# Dependency for API key validation
async def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify API key for secure access"""
    api_key = os.getenv("MORVO_API_KEY")
    if api_key and credentials.credentials != api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    return credentials.credentials

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check for Railway deployment monitoring"""
    return {
        "status": "healthy",
        "platform": "Railway",
        "backend": "Supabase",
        "context_protocol": "MCP",
        "agents": ["M1", "M2", "M3", "M4", "M5"],
        "timestamp": datetime.now().isoformat()
    }

# Root endpoint
@app.get("/")
async def root():
    """Welcome endpoint with API information"""
    return {
        "message": "مرحباً بك في منصة Morvo للتسويق الذكي",
        "version": "2.0.0",
        "agents": {
            "M1": "Ahmed - Strategic Manager",
            "M2": "Fatima - Social Media Manager", 
            "M3": "Mohammed - Campaign Manager",
            "M4": "Nora - Content Manager",
            "M5": "Khalid - Data Manager"
        },
        "endpoints": {
            "strategic_analysis": "/api/v2/agents/m1/strategic-analysis",
            "social_monitoring": "/api/v2/agents/m2/social-monitoring",
            "campaign_optimization": "/api/v2/agents/m3/campaign-optimization",
            "content_strategy": "/api/v2/agents/m4/content-strategy", 
            "data_analytics": "/api/v2/agents/m5/data-analytics",
            "complete_automation": "/api/v2/marketing/complete-automation"
        },
        "integration": "Railway + MCP + Supabase + Zapier"
    }

# Individual Agent Endpoints

@app.post("/api/v2/agents/m1/strategic-analysis")
async def run_m1_strategic_analysis(
    request: MarketingRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """Run M1 (Ahmed) Strategic Analysis - Advanced market research and ROI optimization"""
    try:
        logger.info(f"Starting M1 Strategic Analysis for company: {request.company_info.name}")
        
        # Run the analysis in background
        result_filename = morvo_crew.run_strategic_analysis(request.company_info.dict())
        
        return AgentResponse(
            status="completed",
            message="تم إكمال التحليل الاستراتيجي بواسطة أحمد (M1) بنجاح",
            filename=result_filename,
            timestamp=datetime.now().isoformat(),
            agent_used="M1 - Ahmed (Strategic Manager)"
        )
    except Exception as e:
        logger.error(f"Error in M1 Strategic Analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"خطأ في التحليل الاستراتيجي: {str(e)}")

@app.post("/api/v2/agents/m2/social-monitoring")
async def run_m2_social_monitoring(
    request: MarketingRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """Run M2 (Fatima) Social Media Monitoring - Real-time monitoring and crisis management"""
    try:
        logger.info(f"Starting M2 Social Monitoring for company: {request.company_info.name}")
        
        result_filename = morvo_crew.run_social_media_monitoring(request.company_info.dict())
        
        return AgentResponse(
            status="completed",
            message="تم إكمال مراقبة وسائل التواصل الاجتماعي بواسطة فاطمة (M2) بنجاح",
            filename=result_filename,
            timestamp=datetime.now().isoformat(),
            agent_used="M2 - Fatima (Social Media Manager)"
        )
    except Exception as e:
        logger.error(f"Error in M2 Social Monitoring: {str(e)}")
        raise HTTPException(status_code=500, detail=f"خطأ في مراقبة وسائل التواصل: {str(e)}")

@app.post("/api/v2/agents/m3/campaign-optimization")
async def run_m3_campaign_optimization(
    request: MarketingRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """Run M3 (Mohammed) Campaign Optimization - Auto-optimization and A/B testing"""
    if not request.campaign_info:
        raise HTTPException(status_code=400, detail="معلومات الحملة مطلوبة لتحسين الحملات")
    
    try:
        logger.info(f"Starting M3 Campaign Optimization for campaign: {request.campaign_info.objective}")
        
        result_filename = morvo_crew.run_campaign_optimization(request.campaign_info.dict())
        
        return AgentResponse(
            status="completed",
            message="تم إكمال تحسين الحملات بواسطة محمد (M3) بنجاح",
            filename=result_filename,
            timestamp=datetime.now().isoformat(),
            agent_used="M3 - Mohammed (Campaign Manager)"
        )
    except Exception as e:
        logger.error(f"Error in M3 Campaign Optimization: {str(e)}")
        raise HTTPException(status_code=500, detail=f"خطأ في تحسين الحملات: {str(e)}")

@app.post("/api/v2/agents/m4/content-strategy")
async def run_m4_content_strategy(
    request: MarketingRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """Run M4 (Nora) Content Strategy - Comprehensive content planning and calendar management"""
    try:
        logger.info(f"Starting M4 Content Strategy for company: {request.company_info.name}")
        
        result_filename = morvo_crew.run_content_strategy(request.company_info.dict())
        
        return AgentResponse(
            status="completed",
            message="تم إكمال استراتيجية المحتوى بواسطة نورا (M4) بنجاح",
            filename=result_filename,
            timestamp=datetime.now().isoformat(),
            agent_used="M4 - Nora (Content Manager)"
        )
    except Exception as e:
        logger.error(f"Error in M4 Content Strategy: {str(e)}")
        raise HTTPException(status_code=500, detail=f"خطأ في استراتيجية المحتوى: {str(e)}")

@app.post("/api/v2/agents/m5/data-analytics")
async def run_m5_data_analytics(
    request: MarketingRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """Run M5 (Khalid) Data Analytics - Comprehensive business intelligence and reporting"""
    try:
        logger.info(f"Starting M5 Data Analytics with period: {request.analysis_period}")
        
        result_filename = morvo_crew.run_data_analytics(request.analysis_period)
        
        return AgentResponse(
            status="completed",
            message="تم إكمال تحليل البيانات بواسطة خالد (M5) بنجاح",
            filename=result_filename,
            timestamp=datetime.now().isoformat(),
            agent_used="M5 - Khalid (Data Manager)"
        )
    except Exception as e:
        logger.error(f"Error in M5 Data Analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"خطأ في تحليل البيانات: {str(e)}")

# Combined Crew Endpoints

@app.post("/api/v2/crews/market-analysis")
async def run_market_analysis_crew(
    request: MarketingRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """Run Market Analysis Crew: M1 (Strategic) + M5 (Data Analytics)"""
    try:
        logger.info(f"Starting Market Analysis Crew for company: {request.company_info.name}")
        
        result_filename = morvo_crew.run_market_analysis_crew(request.company_info.dict())
        
        return AgentResponse(
            status="completed",
            message="تم إكمال تحليل السوق بواسطة فريق التحليل (M1 + M5) بنجاح",
            filename=result_filename,
            timestamp=datetime.now().isoformat(),
            agent_used="Market Analysis Crew (M1 + M5)"
        )
    except Exception as e:
        logger.error(f"Error in Market Analysis Crew: {str(e)}")
        raise HTTPException(status_code=500, detail=f"خطأ في تحليل السوق: {str(e)}")

@app.post("/api/v2/crews/content-social")
async def run_content_social_crew(
    request: MarketingRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """Run Content & Social Crew: M2 (Social Media) + M4 (Content Strategy)"""
    try:
        logger.info(f"Starting Content & Social Crew for company: {request.company_info.name}")
        
        result_filename = morvo_crew.run_content_and_social_crew(request.company_info.dict())
        
        return AgentResponse(
            status="completed",
            message="تم إكمال استراتيجية المحتوى ووسائل التواصل بواسطة الفريق (M2 + M4) بنجاح",
            filename=result_filename,
            timestamp=datetime.now().isoformat(),
            agent_used="Content & Social Crew (M2 + M4)"
        )
    except Exception as e:
        logger.error(f"Error in Content & Social Crew: {str(e)}")
        raise HTTPException(status_code=500, detail=f"خطأ في فريق المحتوى ووسائل التواصل: {str(e)}")

@app.post("/api/v2/crews/campaign-execution")
async def run_campaign_execution_crew(
    request: MarketingRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """Run Campaign Execution Crew: M3 (Campaign Manager) + M2 (Social Media) + M5 (Analytics)"""
    if not request.campaign_info:
        raise HTTPException(status_code=400, detail="معلومات الحملة مطلوبة لتنفيذ الحملات")
    
    try:
        logger.info(f"Starting Campaign Execution Crew for campaign: {request.campaign_info.objective}")
        
        result_filename = morvo_crew.run_campaign_execution_crew(
            request.company_info.dict(),
            request.campaign_info.dict()
        )
        
        return AgentResponse(
            status="completed",
            message="تم إكمال تنفيذ الحملة بواسطة فريق التنفيذ (M3 + M2 + M5) بنجاح",
            filename=result_filename,
            timestamp=datetime.now().isoformat(),
            agent_used="Campaign Execution Crew (M3 + M2 + M5)"
        )
    except Exception as e:
        logger.error(f"Error in Campaign Execution Crew: {str(e)}")
        raise HTTPException(status_code=500, detail=f"خطأ في تنفيذ الحملة: {str(e)}")

# Complete Marketing Automation
@app.post("/api/v2/marketing/complete-automation")
async def run_complete_marketing_automation(
    request: MarketingRequest,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(verify_api_key)
):
    """Run Complete Marketing Automation with all 5 agents (M1-M5)"""
    try:
        logger.info(f"Starting Complete Marketing Automation for company: {request.company_info.name}")
        
        campaign_info = request.campaign_info.dict() if request.campaign_info else None
        result_filename = morvo_crew.run_complete_marketing_automation(
            request.company_info.dict(),
            campaign_info
        )
        
        return AgentResponse(
            status="completed",
            message="تم إكمال التسويق الآلي الشامل بواسطة جميع الوكلاء (M1-M5) بنجاح",
            filename=result_filename,
            timestamp=datetime.now().isoformat(),
            agent_used="Complete Marketing Automation (All M1-M5 Agents)"
        )
    except Exception as e:
        logger.error(f"Error in Complete Marketing Automation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"خطأ في التسويق الآلي الشامل: {str(e)}")

# Integration and Status Endpoints

@app.get("/api/v2/status/integration")
async def get_integration_status():
    """Get complete integration status for Railway, MCP, Supabase, and Zapier"""
    try:
        integration_details = morvo_crew.get_integration_details()
        
        return IntegrationStatus(
            platform=integration_details["platform"],
            backend=integration_details["backend"],
            context_protocol=integration_details["context_protocol"],
            agents_count=len(integration_details["agents"]),
            apis_connected=[
                *integration_details["apis"]["social_media"],
                *integration_details["apis"]["analytics"],
                *integration_details["apis"]["business_intelligence"],
                *integration_details["apis"]["ai_services"]
            ],
            deployment_status="active"
        )
    except Exception as e:
        logger.error(f"Error getting integration status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"خطأ في حالة التكامل: {str(e)}")

@app.get("/api/v2/agents/status")
async def get_agents_status():
    """Get status of all M1-M5 agents"""
    return {
        "agents": {
            "M1": {"name": "Ahmed", "role": "Strategic Manager", "status": "active"},
            "M2": {"name": "Fatima", "role": "Social Media Manager", "status": "active"},
            "M3": {"name": "Mohammed", "role": "Campaign Manager", "status": "active"},
            "M4": {"name": "Nora", "role": "Content Manager", "status": "active"},
            "M5": {"name": "Khalid", "role": "Data Manager", "status": "active"}
        },
        "total_agents": 5,
        "platform": "Railway",
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/v2/demo/test")
async def demo_test():
    """Demo endpoint for testing API functionality"""
    sample_company = {
        "name": "متجر الأزياء العصرية",
        "website": "https://fashion-store.sa",
        "industry": "الموضة والأزياء",
        "target_market": "السعودية ودول الخليج",
        "target_audience": "النساء من عمر 18-35",
        "brand_message": "أزياء عصرية بجودة عالية وأسعار منافسة"
    }
    
    return {
        "message": "مرحباً بك في تجربة Morvo للتسويق الذكي",
        "sample_request": sample_company,
        "next_steps": [
            "اختر الوكيل المناسب (M1-M5)",
            "أرسل طلب POST مع معلومات شركتك",
            "احصل على تحليل مخصص من الذكاء الاصطناعي"
        ],
        "agents_available": ["M1", "M2", "M3", "M4", "M5"]
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {"error": exc.detail, "status_code": exc.status_code}

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unexpected error: {str(exc)}")
    return {"error": "خطأ داخلي في الخادم", "status_code": 500}

# Railway deployment configuration
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "morvo_integration_api:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Set to False for production
        log_level="info"
    )
