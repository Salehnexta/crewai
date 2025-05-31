"""
Morvo Marketing Agents - 5 Specialized AI Agents (M1-M5) for Arabic Marketing Automation
Designed for Railway hosting with MCP, Supabase, and Zapier integrations
"""
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool, WebsiteSearchTool
from langchain_openai import ChatOpenAI
from typing import Dict, Any, List, Optional
import os

class MorvoMarketingAgents:
    """
    5 Specialized Marketing Agents (M1-M5) for Arabic Markets
    Integrated with MCP, Supabase, and Zapier for comprehensive automation
    """
    
    def __init__(self):
        """Initialize the marketing agents with Railway/MCP configuration"""
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.7,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Initialize tools with MCP integration - make SerperDevTool optional
        serper_key = os.getenv("SERPER_API_KEY")
        if serper_key:
            self.search_tool = SerperDevTool(api_key=serper_key)
        else:
            self.search_tool = None  # Will use basic web search instead
        self.website_tool = WebsiteSearchTool()
    
    def m1_strategic_manager_agent(self) -> Agent:
        """
        M1: Ahmed - Strategic Manager (المدير الاستراتيجي)
        Advanced market analysis, competitor intelligence, long-term strategy, ROI optimization
        """
        tools = [tool for tool in [self.search_tool, self.website_tool] if tool is not None]
        
        return Agent(
            role="M1 - المدير الاستراتيجي أحمد",
            goal="""تحليل السوق والمنافسين بشكل متقدم ووضع استراتيجيات طويلة المدى 
            مع حساب عائد الاستثمار وتحسين الميزانيات للأسواق العربية""",
            backstory="""أنا أحمد، المدير الاستراتيجي M1 في منصة Morvo. لدي خبرة 15 سنة في 
            التحليل الاستراتيجي للأسواق العربية. أتقن استخدام نماذج متقدمة لتحليل السوق والمنافسين، 
            وأضع استراتيجيات طويلة المدى مع التكامل مع بيانات الصناعة والترندات. 
            أستطيع حساب ROI بدقة وتحسين الميزانيات لتحقيق أفضل النتائج.""",
            verbose=True,
            allow_delegation=True,
            tools=tools,
            llm=self.llm,
            max_iter=3,
            max_execution_time=1800  # 30 minutes for complex analysis
        )
    
    def m2_social_media_manager_agent(self) -> Agent:
        """
        M2: Fatima - Social Media Manager (مديرة السوشال ميديا)
        Real-time monitoring, sentiment analysis, crisis alerts, trend suggestions
        """
        tools = [tool for tool in [self.search_tool, self.website_tool] if tool is not None]
        
        return Agent(
            role="M2 - مديرة السوشال ميديا فاطمة",
            goal="""مراقبة real-time لجميع المنصات الاجتماعية مع تحليل المشاعر المتقدم 
            ونظام إنذار مبكر للأزمات واقتراح المحتوى المناسب للترندات""",
            backstory="""أنا فاطمة، مديرة السوشال ميديا M2 في منصة Morvo. متخصصة في المراقبة 
            المباشرة لجميع منصات التواصل الاجتماعي مع خبرة في تحليل المشاعر المتقدم. 
            لدي نظام إنذار مبكر للأزمات وأقدم اقتراحات محتوى تتماشى مع الترندات الحالية. 
            أتقن إدارة Facebook, Instagram, Twitter, LinkedIn, TikTok, YouTube.""",
            verbose=True,
            allow_delegation=False,
            tools=tools,
            llm=self.llm,
            max_iter=2,
            max_execution_time=1200  # 20 minutes for social monitoring
        )
    
    def m3_campaign_manager_agent(self) -> Agent:
        """
        M3: Mohammed - Campaign Manager (مدير الحملات)
        Campaign tracking, automatic optimization, A/B testing, opportunity alerts
        """
        tools = [tool for tool in [self.search_tool] if tool is not None]
        
        return Agent(
            role="M3 - مدير الحملات محمد",
            goal="""تتبع أداء الحملات من جميع المنصات مع التحسين التلقائي للاستهداف والميزانيات 
            وإجراء A/B tests وتقديم تنبيهات للفرص والمشاكل""",
            backstory="""أنا محمد، مدير الحملات M3 في منصة Morvo. خبير في تتبع أداء الحملات 
            عبر جميع المنصات الرقمية مع قدرة على التحسين التلقائي للاستهداف والميزانيات. 
            أتقن إجراء A/B tests وتحليل النتائج، وأقدم تنبيهات فورية للفرص الجديدة والمشاكل المحتملة. 
            متصل مع Google Ads, Facebook Ads, وجميع منصات الإعلان الرقمي.""",
            verbose=True,
            allow_delegation=False,
            tools=tools,
            llm=self.llm,
            max_iter=3,
            max_execution_time=1500  # 25 minutes for campaign optimization
        )
    
    def m4_content_manager_agent(self) -> Agent:
        """
        M4: Nora - Content Manager (مديرة المحتوى)
        Content strategy creation, calendar management, performance tracking, creative suggestions
        """
        tools = [tool for tool in [self.search_tool] if tool is not None]
        
        return Agent(
            role="M4 - مديرة المحتوى نورا",
            goal="""إنشاء استراتيجيات محتوى مخصصة وإدارة تقويم المحتوى مع تتبع أداء كل نوع محتوى 
            وتقديم اقتراحات إبداعية للحملات باللغة العربية""",
            backstory="""أنا نورا، مديرة المحتوى M4 في منصة Morvo. متخصصة في إنشاء استراتيجيات 
            محتوى مخصصة للأسواق العربية وإدارة تقويم المحتوى بكفاءة عالية. أتتبع أداء كل نوع محتوى 
            وأقدم اقتراحات إبداعية للحملات. لدي خبرة واسعة في المحتوى متعدد الصيغ: نصوص، 
            فيديوهات، إنفوجرافيك، بودكاست، وقصص تفاعلية.""",
            verbose=True,
            allow_delegation=False,
            tools=tools,
            llm=self.llm,
            max_iter=2,
            max_execution_time=1200  # 20 minutes for content strategy
        )
    
    def m5_data_manager_agent(self) -> Agent:
        """
        M5: Khalid - Data Manager (مدير البيانات)
        Data aggregation, interactive reports, brand monitoring, actionable insights
        """
        tools = [tool for tool in [self.search_tool, self.website_tool] if tool is not None]
        
        return Agent(
            role="M5 - مدير البيانات خالد",
            goal="""تجميع البيانات من جميع المصادر وإنشاء تقارير تفاعلية مع مراقبة العلامة التجارية 
            وتقديم رؤى عملية للتحسين المستمر""",
            backstory="""أنا خالد، مدير البيانات M5 في منصة Morvo. خبير في تجميع البيانات من 
            جميع المصادر الرقمية وإنشاء تقارير تفاعلية شاملة. أتقن مراقبة العلامة التجارية 
            وأقدم رؤى عملية للتحسين المستمر. متصل مع Google Analytics, SEMrush, Ahrefs, 
            SimilarWeb, Brand24 وجميع أدوات الذكاء التجاري المتقدمة.""",
            verbose=True,
            allow_delegation=False,
            tools=tools,
            llm=self.llm,
            max_iter=2,
            max_execution_time=1800  # 30 minutes for comprehensive data analysis
        )
    
    def get_all_agents(self) -> List[Agent]:
        """Get all 5 marketing agents (M1-M5)"""
        return [
            self.m1_strategic_manager_agent(),
            self.m2_social_media_manager_agent(),
            self.m3_campaign_manager_agent(),
            self.m4_content_manager_agent(),
            self.m5_data_manager_agent()
        ]
    
    def get_agent_integrations(self) -> Dict[str, Any]:
        """Get comprehensive integration details for Railway/MCP deployment"""
        return {
            "social_media_apis": {
                "facebook_instagram": "Facebook/Instagram Graph API - تحليل الصفحات والإعلانات",
                "twitter": "Twitter API v2 - مراقبة الإشارات والتفاعلات",
                "linkedin": "LinkedIn API - تحليل الشركات والمحتوى B2B",
                "tiktok": "TikTok API - تتبع الترندات والفيديوهات",
                "youtube": "YouTube API - تحليل القنوات والفيديوهات"
            },
            "analytics_ads_apis": {
                "google_analytics": "Google Analytics 4 - تحليل موقع الويب والسلوك",
                "google_ads": "Google Ads API - أداء الحملات الإعلانية",
                "facebook_ads": "Facebook Ads API - تتبع وتحسين الإعلانات",
                "search_console": "Search Console API - أداء SEO والكلمات المفتاحية"
            },
            "business_intelligence": {
                "semrush": "SEMrush API - تحليل المنافسين والكلمات المفتاحية",
                "ahrefs": "Ahrefs API - باك لينكس وتحليل السيو",
                "similarweb": "SimilarWeb API - تحليل حركة المرور والجمهور",
                "brand24": "Brand24 API - مراقبة العلامة التجارية"
            },
            "automation_integration": {
                "zapier": "Zapier Platform - ربط مع آلاف التطبيقات",
                "make": "Make (Integromat) - أتمتة متقدمة للعمليات",
                "ifttt": "IFTTT - أتمتة بسيطة للمهام",
                "webhooks": "Webhooks - تكاملات مخصصة",
                "mcp": "Model Context Protocol - تكامل مع Supabase",
                "supabase": "Supabase - قاعدة البيانات والمصادقة"
            },
            "deployment": {
                "platform": "Railway",
                "database": "Supabase PostgreSQL",
                "authentication": "Supabase Auth",
                "realtime": "Supabase Realtime",
                "edge_functions": "Supabase Edge Functions",
                "mcp_integration": "Model Context Protocol",
                "automation": "Zapier/Make/IFTTT"
            }
        }
