"""
Morvo Marketing Tasks - Task System for 5 Marketing Agents (M1-M5)
Designed for Railway hosting with MCP, Supabase, and Zapier integrations
"""
from crewai import Task
from typing import Dict, Any, List
from agents.morvo_marketing_agents import MorvoMarketingAgents

class MorvoMarketingTasks:
    """
    Complete task system for the 5 Morvo marketing agents (M1-M5)
    Integrates with Railway, MCP, Supabase, and Zapier
    """
    
    def __init__(self):
        self.agents = MorvoMarketingAgents()
    
    def m1_strategic_analysis_task(self, company_info: Dict[str, Any]) -> Task:
        """
        Task for M1 (Ahmed): Strategic Market Analysis & ROI Optimization
        Advanced market analysis, competitor intelligence, long-term strategy
        """
        return Task(
            description=f"""
            M1 - المدير الاستراتيجي أحمد - تحليل استراتيجي شامل:
            
            معلومات الشركة:
            - الاسم: {company_info.get('name', '')}
            - الموقع الإلكتروني: {company_info.get('website', '')}
            - القطاع: {company_info.get('industry', '')}
            - السوق المستهدف: {company_info.get('target_market', 'السعودية ودول الخليج')}
            
            المطلوب تحليله (نموذج متقدم):
            1. تحليل حجم السوق وإمكانيات النمو مع حسابات ROI
            2. تحليل المنافسين الرئيسيين (5-7 منافسين) مع تحليل SWOT
            3. وضع استراتيجية طويلة المدى (12-24 شهر)
            4. تحسين الميزانيات وتوزيع الاستثمارات
            5. تحديد الفرص الاستراتيجية والتهديدات
            6. التكامل مع بيانات الصناعة والترندات الحالية
            7. حساب العائد المتوقع على الاستثمار (ROI) لكل قناة
            8. وضع KPIs استراتيجية قابلة للقياس
            
            استخدم تحليلاً متقدماً مع بيانات حديثة ومصادر موثوقة من APIs المختلفة.
            """,
            agent=self.agents.m1_strategic_manager_agent(),
            expected_output="""تقرير استراتيجي شامل يتضمن:
            - تحليل السوق مع حسابات ROI مفصلة
            - خريطة تنافسية متقدمة مع تحليل SWOT
            - استراتيجية طويلة المدى مع جدولة زمنية
            - توصيات تحسين الميزانية والاستثمار
            - KPIs استراتيجية ومقاييس الأداء"""
        )
    
    def m2_social_monitoring_task(self, company_info: Dict[str, Any]) -> Task:
        """
        Task for M2 (Fatima): Real-time Social Media Monitoring & Crisis Management
        """
        return Task(
            description=f"""
            M2 - مديرة السوشال ميديا فاطمة - مراقبة وإدارة المنصات الاجتماعية:
            
            معلومات الشركة:
            - الاسم: {company_info.get('name', '')}
            - القطاع: {company_info.get('industry', '')}
            - المنصات النشطة: جميع المنصات الاجتماعية
            
            المطلوب تنفيذه (مراقبة real-time):
            1. مراقبة جميع المنصات الاجتماعية في الوقت الفعلي:
               - Facebook & Instagram: تحليل المشاركات والقصص
               - Twitter: مراقبة الإشارات والهاشتاجات
               - LinkedIn: تتبع المحتوى المهني
               - TikTok: مراقبة الترندات والفيديوهات
               - YouTube: تحليل القنوات والتفاعل
            2. تحليل المشاعر المتقدم للتعليقات والإشارات
            3. نظام إنذار مبكر للأزمات المحتملة
            4. اقتراح محتوى يتماشى مع الترندات الحالية
            5. تحليل أداء المنافسين على كل منصة
            6. تحديد أوقات النشر المثلى للجمهور العربي
            7. إعداد تقارير أداء يومية وأسبوعية
            8. خطة إدارة الأزمات والاستجابة السريعة
            
            ركز على التفاعل مع الثقافة العربية والقيم المحلية.
            """,
            agent=self.agents.m2_social_media_manager_agent(),
            expected_output="""تقرير مراقبة المنصات الاجتماعية يشمل:
            - dashboard مراقبة real-time لجميع المنصات
            - تحليل مشاعر متقدم مع تصنيف إيجابي/سلبي/محايد
            - تنبيهات الأزمات مع خطة الاستجابة
            - اقتراحات محتوى مبنية على الترندات
            - جدول نشر محسّن لكل منصة"""
        )
    
    def m3_campaign_optimization_task(self, campaign_info: Dict[str, Any]) -> Task:
        """
        Task for M3 (Mohammed): Campaign Tracking & Auto-Optimization
        """
        return Task(
            description=f"""
            M3 - مدير الحملات محمد - تتبع وتحسين الحملات الإعلانية:
            
            معلومات الحملة:
            - الهدف: {campaign_info.get('objective', '')}
            - الميزانية: {campaign_info.get('budget', '')}
            - المدة: {campaign_info.get('duration', '30 يوم')}
            - المنصات: {campaign_info.get('platforms', 'جميع المنصات')}
            
            المطلوب تنفيذه (تحسين تلقائي):
            1. تتبع أداء الحملات من جميع المنصات:
               - Google Ads: تحليل الكلمات المفتاحية والإعلانات
               - Facebook/Instagram Ads: تحسين الاستهداف والإبداعات
               - Twitter Ads: تحليل الإعلانات المروجة
               - LinkedIn Ads: تحسين الحملات B2B
               - YouTube Ads: تحليل إعلانات الفيديو
            2. التحسين التلقائي للاستهداف والميزانيات
            3. إجراء A/B tests مستمرة للإبداعات والرسائل
            4. تحليل النتائج وتقديم توصيات التحسين
            5. تنبيهات فورية للفرص الجديدة (trending keywords, audience insights)
            6. مراقبة المشاكل المحتملة (ad disapprovals, budget issues)
            7. تحسين معدلات التحويل وتقليل تكلفة الاكتساب
            8. تقارير أداء مفصلة مع مقارنات زمنية
            
            استخدم APIs المختلفة للحصول على بيانات real-time.
            """,
            agent=self.agents.m3_campaign_manager_agent(),
            expected_output="""تقرير تحسين الحملات يتضمن:
            - dashboard تتبع الأداء لجميع المنصات
            - نتائج A/B tests مع التوصيات
            - تحسينات الاستهداف والميزانية المطبقة
            - تنبيهات الفرص والمشاكل
            - معدلات التحويل وتكلفة الاكتساب المحسنة"""
        )
    
    def m4_content_strategy_task(self, company_info: Dict[str, Any]) -> Task:
        """
        Task for M4 (Nora): Content Strategy & Calendar Management
        """
        return Task(
            description=f"""
            M4 - مديرة المحتوى نورا - استراتيجية وإدارة المحتوى:
            
            معلومات الشركة:
            - الاسم: {company_info.get('name', '')}
            - القطاع: {company_info.get('industry', '')}
            - الجمهور المستهدف: {company_info.get('target_audience', '')}
            - رسالة العلامة التجارية: {company_info.get('brand_message', '')}
            
            المطلوب تطويره (استراتيجية مخصصة):
            1. إنشاء استراتيجية محتوى مخصصة لمدة 3 أشهر:
               - نصوص: منشورات، مقالات، تغريدات
               - فيديوهات: ريلز، ستوريز، يوتيوب شورتس
               - إنفوجرافيك: تصاميم تفاعلية ومعلوماتية
               - بودكاست: محتوى صوتي للجمهور العربي
               - قصص تفاعلية: محتوى تفاعلي للإنستغرام
            2. إدارة تقويم المحتوى بكفاءة عالية
            3. تتبع أداء كل نوع محتوى ومقاييس التفاعل
            4. اقتراحات إبداعية للحملات الموسمية
            5. تحديد أفضل أوقات النشر لكل منصة
            6. إنشاء محتوى يناسب الثقافة العربية
            7. تطوير voice & tone للعلامة التجارية
            8. تحسين المحتوى لمحركات البحث (SEO)
            
            ركز على المحتوى متعدد الصيغ والتفاعلي.
            """,
            agent=self.agents.m4_content_manager_agent(),
            expected_output="""استراتيجية المحتوى الشاملة تشمل:
            - تقويم محتوى مفصل لمدة 3 أشهر لجميع الصيغ
            - دليل voice & tone للعلامة التجارية
            - نماذج من المحتوى لكل منصة ونوع
            - خطة المحتوى الموسمي والحملات الإبداعية
            - مقاييس أداء المحتوى وتقارير التحسين"""
        )
    
    def m5_data_analytics_task(self, analysis_period: str = "آخر 30 يوم") -> Task:
        """
        Task for M5 (Khalid): Comprehensive Data Analytics & Business Intelligence
        """
        return Task(
            description=f"""
            M5 - مدير البيانات خالد - تحليل البيانات والذكاء التجاري:
            
            فترة التحليل: {analysis_period}
            
            المطلوب تحليله (تجميع شامل):
            1. تجميع البيانات من جميع المصادر:
               - Google Analytics 4: سلوك الزوار والتحويلات
               - SEMrush: الكلمات المفتاحية وأداء SEO
               - Ahrefs: باك لينكس وسلطة النطاق
               - SimilarWeb: حركة المرور وتحليل الجمهور
               - Brand24: مراقبة العلامة التجارية والإشارات
            2. إنشاء تقارير تفاعلية شاملة:
               - dashboards بالوقت الفعلي
               - مقارنات زمنية وترندات
               - تحليل الجمهور والسلوك
               - معدلات التحويل والمبيعات
            3. مراقبة العلامة التجارية:
               - تتبع الإشارات والمراجعات
               - تحليل المشاعر العامة
               - مراقبة السمعة الرقمية
            4. تقديم رؤى عملية للتحسين:
               - اكتشاف الفرص الجديدة
               - تحديد نقاط الضعف
               - توصيات تحسين الأداء
               - تنبؤات مستقبلية مبنية على البيانات
            
            استخدم جميع أدوات الذكاء التجاري المتقدمة.
            """,
            agent=self.agents.m5_data_manager_agent(),
            expected_output="""تقرير الذكاء التجاري الشامل يشمل:
            - dashboard تفاعلي مع جميع المقاييس الرئيسية
            - تحليل شامل لحركة المرور والسلوك
            - تقرير مراقبة العلامة التجارية والسمعة
            - رؤى عملية مع توصيات التحسين المحددة
            - تنبؤات مستقبلية مبنية على تحليل البيانات"""
        )
    
    def get_complete_marketing_workflow(self, 
                                      company_info: Dict[str, Any],
                                      campaign_info: Dict[str, Any] = None) -> List[Task]:
        """
        Get the complete marketing workflow with all 5 agents (M1-M5)
        """
        tasks = []
        
        # Phase 1: Strategic Analysis (M1)
        tasks.append(self.m1_strategic_analysis_task(company_info))
        
        # Phase 2: Social Media Monitoring (M2)
        tasks.append(self.m2_social_monitoring_task(company_info))
        
        # Phase 3: Content Strategy (M4)
        tasks.append(self.m4_content_strategy_task(company_info))
        
        # Phase 4: Campaign Optimization (M3) - if campaign info provided
        if campaign_info:
            tasks.append(self.m3_campaign_optimization_task(campaign_info))
        
        # Phase 5: Data Analytics (M5)
        tasks.append(self.m5_data_analytics_task())
        
        return tasks
