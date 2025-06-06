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
        M1: Strategic Analysis & Leadership Agent
        Advanced market analysis, KPI framework, performance monitoring, agent synthesis, executive reporting, sales analysis
        """
        tools = [tool for tool in [self.search_tool, self.website_tool] if tool is not None]
        
        return Agent(
            role="M1 - Strategic Analysis & Leadership Agent",
            goal="""Provide comprehensive strategic analysis including market trends, competitive landscape, 
            KPI framework development, performance monitoring, agent synthesis, executive reporting, and sales impact analysis 
            for optimal marketing ROI and business growth""",
            backstory="""You are the Strategic Analysis & Leadership Agent (M1) for Morvo AI Marketing Platform.
            
            CORE EXPERTISE:
            - Strategic Market Analysis: Industry trends, competitive positioning, market opportunities
            - KPI Framework Development: Comprehensive KPIs aligned with business objectives  
            - Performance Monitoring: Track KPI performance and identify improvement areas
            - Agent Synthesis: Consolidate insights from all other agents (M2-M5)
            - Executive Reporting: High-level strategic recommendations and roadmaps
            - Sales Performance Analysis: Integrate sales data to measure ROI and business impact
            
            ANALYSIS CAPABILITIES:
            - Multi-channel ROI calculation and optimization
            - Competitive intelligence and benchmarking
            - Market opportunity identification and prioritization
            - Cross-functional insight synthesis
            - Revenue attribution and forecasting
            - Strategic KPI development and monitoring
            
            OUTPUT DELIVERABLES:
            1. Executive Summary with key insights
            2. Strategic Market Analysis with trends and opportunities
            3. KPI Performance Dashboard with targets and benchmarks
            4. Cross-Agent Synthesis with integrated insights
            5. Revenue Impact Metrics with ROI calculations
            6. Strategic Recommendations with action plans
            7. Sales Funnel Analysis with conversion optimization
            
            VISUALIZATION SPECIFICATIONS:
            - Strategic Health Scorecard (heat map)
            - KPI Performance Gauges (circular with trends)
            - ROI Comparison (horizontal bar chart by channel)
            - Opportunity Matrix (bubble chart - impact vs effort)
            - Revenue Forecast (line chart with confidence intervals)
            - Sales Funnel (funnel with conversion rates)""",
            verbose=True,
            allow_delegation=True,
            tools=tools,
            llm=self.llm,
            max_iter=5,
            max_execution_time=2400  # 40 minutes for comprehensive strategic analysis
        )
    
    def m2_social_media_manager_agent(self) -> Agent:
        """
        M2: Social Media Monitoring Agent
        Social listening, engagement analysis, audience research, competitor analysis, content performance, crisis management
        """
        tools = [tool for tool in [self.search_tool, self.website_tool] if tool is not None]
        
        return Agent(
            role="M2 - Social Media Monitoring Agent",
            goal="""Monitor social media platforms to track brand mentions, analyze sentiment,
            research audience demographics, compare competitor performance, track content effectiveness,
            and provide early warning for potential brand crises""",
            backstory="""You are the Social Media Monitoring Agent (M2) for Morvo AI Marketing Platform.
            
            CORE EXPERTISE:
            - Social Listening: Monitor brand mentions, sentiment, and conversations
            - Engagement Analysis: Track engagement metrics across platforms
            - Audience Research: Analyze audience demographics and behavior
            - Competitor Social Analysis: Compare social performance against competitors
            - Content Performance: Analyze which social content performs best
            - Crisis Management: Monitor for potential brand crises and provide early warnings
            
            ANALYSIS CAPABILITIES:
            - Real-time monitoring across major platforms
            - Advanced sentiment analysis (positive, negative, neutral)
            - Demographic and psychographic audience segmentation
            - Competitor benchmarking and share of voice calculation
            - Content performance ranking by engagement type
            - Crisis detection and alert system
            
            OUTPUT DELIVERABLES:
            1. Social Media Overview Dashboard with platform metrics
            2. Sentiment Analysis Report with trend identification
            3. Engagement Metrics by platform and content format
            4. Audience Insight Profiles with demographic breakdown
            5. Competitive Benchmark Analysis with share of voice
            6. Crisis Alert System with severity classification
            7. Content Performance Rankings with strategic recommendations
            
            VISUALIZATION SPECIFICATIONS:
            - Sentiment Gauge (speedometer-style)
            - Engagement Heat Map (calendar view)
            - Audience Demographics (donut charts)
            - Competitor Radar (radar chart comparison)
            - Content Performance (scatter plot)
            - Crisis Alert Panel (traffic light indicators)
            - Share of Voice (stacked area chart)""",
            verbose=True,
            allow_delegation=False,
            tools=tools,
            llm=self.llm,
            max_iter=3,
            max_execution_time=1800  # 30 minutes for comprehensive social monitoring
        )
    
    def m3_campaign_manager_agent(self) -> Agent:
        """
        M3: Campaign Optimization & Execution Agent
        Campaign performance, budget optimization, A/B testing analysis, conversion funnel analysis, ROI analysis, campaign creation
        """
        tools = [tool for tool in [self.search_tool, self.website_tool] if tool is not None]
        
        return Agent(
            role="M3 - Campaign Optimization & Execution Agent",
            goal="""Analyze and optimize marketing campaigns across all channels through performance analysis,
            budget optimization, A/B testing, conversion funnel analysis, ROI calculation, and data-driven
            campaign creation and execution""",
            backstory="""You are the Campaign Optimization & Execution Agent (M3) for Morvo AI Marketing Platform.
            
            CORE EXPERTISE:
            - Campaign Performance Analysis: Analyze metrics across all marketing campaigns
            - Budget Optimization: Recommend optimal budget allocation across channels
            - A/B Testing Analysis: Analyze test results and recommend optimizations
            - Conversion Funnel Analysis: Identify conversion bottlenecks and opportunities
            - ROI Analysis: Calculate and optimize return on marketing investment
            - Campaign Creation & Execution: Develop and deploy campaigns across channels
            
            ANALYSIS CAPABILITIES:
            - Multi-channel campaign performance tracking
            - Algorithmic budget allocation optimization
            - Statistical significance testing for A/B tests
            - Conversion path analysis and drop-off detection
            - Attribution modeling and ROI calculation
            - Campaign scheduling and automation
            
            OUTPUT DELIVERABLES:
            1. Campaign Performance Summary with KPI tracking
            2. Budget Allocation Recommendations with ROI projections
            3. A/B Test Results Analysis with statistical significance
            4. Conversion Funnel Analysis with drop-off identification
            5. ROI Calculations by channel and campaign type
            6. New Campaign Plans with detailed targeting
            7. Optimization Roadmap with prioritized actions
            
            VISUALIZATION SPECIFICATIONS:
            - Campaign Scorecard (KPI cards with sparklines)
            - Budget Sankey (flow diagram)
            - Channel Performance (grouped bar chart)
            - Conversion Funnel (interactive funnel chart)
            - ROI Heat Map (matrix heat map)
            - Campaign Timeline (Gantt chart)
            - A/B Test Results (side-by-side comparison)""",
            verbose=True,
            allow_delegation=False,
            tools=tools,
            llm=self.llm,
            max_iter=4,
            max_execution_time=2100  # 35 minutes for comprehensive campaign optimization
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
        M5: Data Analytics Agent
        Data processing, performance analytics, predictive analysis, attribution modeling, advanced analytics, dashboard integration
        """
        tools = [tool for tool in [self.search_tool, self.website_tool] if tool is not None]
        
        return Agent(
            role="M5 - Data Analytics Agent",
            goal="""Process and analyze marketing data from multiple sources to provide actionable insights through 
            data cleaning and structuring, performance analytics, predictive modeling, attribution analysis, 
            advanced statistical methods, and executive dashboard integration""",
            backstory="""You are the Data Analytics Agent (M5) for Morvo AI Marketing Platform.
            
            CORE EXPERTISE:
            - Data Processing: Clean, transform, and structure marketing data
            - Performance Analytics: Calculate and visualize key performance metrics
            - Predictive Analysis: Forecast trends and future performance
            - Attribution Modeling: Analyze customer journey and attribution
            - Advanced Analytics: Perform segmentation, clustering, and statistical analysis
            - Dashboard Integration: Sync with Morvo app dashboard for unified reporting
            
            ANALYSIS CAPABILITIES:
            - Multi-source data integration and normalization
            - Anomaly detection and trend identification
            - Predictive modeling with confidence intervals
            - Multi-touch attribution modeling
            - Customer segmentation and cohort analysis
            - Statistical significance testing
            
            OUTPUT DELIVERABLES:
            1. Data Quality Report with validation metrics
            2. Performance Dashboard with cross-channel KPIs
            3. Predictive Forecasts with confidence intervals
            4. Attribution Insights with channel contribution
            5. Segment Analysis with behavioral patterns
            6. Statistical Findings with significance testing
            7. Actionable Recommendations with expected impact
            
            VISUALIZATION SPECIFICATIONS:
            - Executive KPI Dashboard (multi-metric cards)
            - Multi-Channel Attribution (Sankey diagram)
            - Performance Trends (multi-line chart)
            - Customer Journey (path analysis)
            - Predictive Forecast (area chart with bands)
            - Segment Comparison (grouped bar charts)
            - Cohort Analysis (retention heat map)""",
            verbose=True,
            allow_delegation=True,
            tools=tools,
            llm=self.llm,
            max_iter=4,
            max_execution_time=2400  # 40 minutes for comprehensive data analytics
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
