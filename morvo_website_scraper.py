# 🕷️ **مورفو - وكيل الـ Scraping الذكي للمواقع السعودية**

from crewai import Agent, Task, Crew
from crewai_tools import ScrapeWebsiteTool, WebsiteSearchTool
from bs4 import BeautifulSoup
import requests
import json
from typing import Dict, List, Any, Optional
import re
from urllib.parse import urljoin, urlparse
import asyncio
import aiohttp
from pydantic import BaseModel
import logging
from datetime import datetime

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebsiteAnalysisResult(BaseModel):
    """نموذج نتائج تحليل الموقع"""
    url: str
    title: str
    description: str
    business_type: str
    industry: str
    products: List[Dict]
    services: List[Dict]
    contact_info: Dict
    social_media: Dict
    competitors: List[str]
    seo_analysis: Dict
    saudi_compliance: Dict
    ecommerce_data: Dict
    content_analysis: Dict
    recommendations: List[str]
    confidence_score: float
    analysis_timestamp: datetime

class MorvoWebsiteScraper:
    """🕷️ وكيل مورفو للحصول على بيانات المواقع وتحليلها"""
    
    def __init__(self):
        self.scrape_tool = ScrapeWebsiteTool()
        self.search_tool = WebsiteSearchTool()
        
        # Headers للتصفح
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ar,en-US;q=0.7,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # إنشاء الوكلاء المتخصصين
        self.website_analyzer = self._create_website_analyzer()
        self.seo_specialist = self._create_seo_specialist()
        self.saudi_market_expert = self._create_saudi_market_expert()
        self.competitor_researcher = self._create_competitor_researcher()
        self.ecommerce_specialist = self._create_ecommerce_specialist()
        
    def _create_website_analyzer(self):
        """🔍 وكيل تحليل المواقع العام"""
        return Agent(
            role="Website Analysis Specialist",
            goal="تحليل شامل للمواقع الإلكترونية وفهم نوع العمل والمنتجات والخدمات",
            backstory="""أنت خبير في تحليل المواقع الإلكترونية مع تركيز خاص على السوق السعودي.
            تتمتع بخبرة 10 سنوات في تحليل مواقع التجارة الإلكترونية والشركات الخدمية.
            تفهم الثقافة السعودية ومتطلبات السوق المحلي وتستطيع تحديد نوع العمل بدقة.
            خبرتك تشمل: المتاجر الإلكترونية، الشركات الخدمية، المطاعم، العقارات، التعليم، والصحة.""",
            tools=[self.scrape_tool, self.search_tool],
            verbose=True,
            allow_delegation=False
        )
    
    def _create_seo_specialist(self):
        """📊 خبير SEO وتحليل الأداء"""
        return Agent(
            role="SEO & Performance Analyst",
            goal="تحليل SEO شامل ونصائح تحسين الموقع للسوق السعودي",
            backstory="""خبير SEO متخصص في السوق السعودي والمحتوى العربي.
            تعرف أفضل الممارسات لتحسين المواقع في محركات البحث العربية وGoogle.
            خبرة واسعة في تحليل سرعة المواقع، التوافق مع الأجهزة المحمولة، وتحليل الكلمات المفتاحية العربية.
            تركز على متطلبات SEO الخاصة بالسوق السعودي والمنطقة العربية.""",
            tools=[self.scrape_tool],
            verbose=True,
            allow_delegation=False
        )
    
    def _create_saudi_market_expert(self):
        """🇸🇦 خبير السوق السعودي"""
        return Agent(
            role="Saudi Market Compliance Expert",
            goal="تحليل مدى توافق الموقع مع السوق السعودي ومتطلبات العملاء المحليين",
            backstory="""خبير في السوق السعودي والامتثال للقوانين والثقافة المحلية.
            تفهم متطلبات التجارة الإلكترونية في السعودية، أنظمة الدفع المحلية، وسائل الشحن.
            خبرة في تحليل توافق المواقع مع اللوائح السعودية، طرق الدفع المحلية (مدى، STC Pay، إلخ).
            تعرف الأعياد والمواسم التجارية السعودية وتأثيرها على التسويق.""",
            tools=[self.scrape_tool],
            verbose=True,
            allow_delegation=False
        )
    
    def _create_competitor_researcher(self):
        """🎯 باحث المنافسين"""
        return Agent(
            role="Competitive Intelligence Researcher",
            goal="تحديد المنافسين المباشرين في السوق السعودي وتحليل استراتيجياتهم",
            backstory="""باحث متخصص في تحليل المنافسة والذكاء التجاري.
            خبرة واسعة في تحديد المنافسين المباشرين وغير المباشرين في السوق السعودي.
            تحلل استراتيجيات التسعير، المنتجات، التسويق الرقمي، وتجربة العملاء للمنافسين.
            تركز على المنافسين المحليين والإقليميين والدوليين في السوق السعودي.""",
            tools=[self.search_tool, self.scrape_tool],
            verbose=True,
            allow_delegation=False
        )
    
    def _create_ecommerce_specialist(self):
        """🛒 خبير التجارة الإلكترونية"""
        return Agent(
            role="E-commerce Platform Specialist",
            goal="تحليل منصات التجارة الإلكترونية وتحديد نوع المنصة والميزات المتاحة",
            backstory="""خبير في منصات التجارة الإلكترونية مع معرفة عميقة بالمنصات المستخدمة في السعودية.
            خبرة في تحديد نوع المنصة (Shopify, Salla, Zid, WooCommerce, Magento, إلخ).
            تحلل ميزات المتجر، طرق الدفع، خيارات الشحن، إدارة المخزون، وتجربة المستخدم.
            تفهم متطلبات التجارة الإلكترونية في السعودية ومنصات الدفع المحلية.""",
            tools=[self.scrape_tool],
            verbose=True,
            allow_delegation=False
        )

    async def analyze_website(self, url: str) -> WebsiteAnalysisResult:
        """🎯 تحليل شامل للموقع الإلكتروني"""
        
        logger.info(f"🚀 بدء تحليل الموقع: {url}")
        
        try:
            # مهمة التحليل العام
            general_analysis_task = Task(
                description=f"""
                قم بتحليل شامل للموقع: {url}
                
                المطلوب تحديد:
                1. نوع العمل والصناعة (تجارة إلكترونية، خدمات، مطاعم، إلخ)
                2. المنتجات والخدمات الرئيسية
                3. معلومات الاتصال الكاملة
                4. الهيكل العام للموقع
                5. جودة المحتوى العربي
                6. التقنيات المستخدمة
                
                ركز على استخراج أكبر قدر من المعلومات لفهم العمل بشكل كامل.
                """,
                agent=self.website_analyzer,
                expected_output="تحليل شامل بتنسيق JSON يتضمن جميع البيانات المستخرجة"
            )
            
            # مهمة تحليل SEO
            seo_analysis_task = Task(
                description=f"""
                قم بتحليل SEO شامل للموقع: {url}
                
                المطلوب:
                1. تحليل العلامات الوصفية (title, description, keywords)
                2. هيكل الURL والروابط الداخلية
                3. سرعة تحميل الصفحات
                4. التوافق مع الأجهزة المحمولة
                5. استخدام HTTPS
                6. جودة المحتوى العربي والكلمات المفتاحية
                7. Schema markup وبيانات منظمة
                
                قدم نقاط القوة والضعف مع توصيات للتحسين.
                """,
                agent=self.seo_specialist,
                expected_output="تقرير SEO مفصل مع نقاط وتوصيات التحسين"
            )
            
            # مهمة تحليل السوق السعودي
            saudi_compliance_task = Task(
                description=f"""
                قم بتحليل مدى توافق الموقع مع السوق السعودي: {url}
                
                المطلوب:
                1. دعم اللغة العربية ومستوى جودة الترجمة
                2. طرق الدفع المحلية (مدى، STC Pay، Apple Pay، إلخ)
                3. خيارات الشحن المحلي والسريع
                4. أسعار بالريال السعودي
                5. التوافق مع القوانين السعودية
                6. المحتوى الثقافي المناسب
                7. خدمة العملاء باللغة العربية
                
                حدد مستوى التوافق مع السوق السعودي ونقاط التحسين.
                """,
                agent=self.saudi_market_expert,
                expected_output="تقييم التوافق مع السوق السعودي مع توصيات التحسين"
            )
            
            # مهمة تحليل المنافسين
            competitor_analysis_task = Task(
                description=f"""
                ابحث عن المنافسين المباشرين للموقع: {url}
                
                المطلوب:
                1. تحديد 5-10 منافسين مباشرين في السوق السعودي
                2. تحليل نقاط القوة والضعف لكل منافس
                3. مقارنة الأسعار والمنتجات
                4. تحليل استراتيجيات التسويق الرقمي
                5. تحديد الفرص التنافسية
                6. توصيات للتميز عن المنافسين
                
                ركز على المنافسين في السوق السعودي والخليجي.
                """,
                agent=self.competitor_researcher,
                expected_output="تحليل تنافسي شامل مع قائمة المنافسين والتوصيات"
            )
            
            # مهمة تحليل التجارة الإلكترونية
            ecommerce_analysis_task = Task(
                description=f"""
                إذا كان الموقع متجر إلكتروني، قم بتحليل شامل: {url}
                
                المطلوب:
                1. تحديد منصة التجارة الإلكترونية المستخدمة
                2. تحليل كتالوج المنتجات والفئات
                3. استراتيجية التسعير ونطاقات الأسعار
                4. عملية الشراء وتجربة المستخدم
                5. طرق الدفع والشحن المتاحة
                6. سياسات الإرجاع والضمان
                7. برامج الولاء والعروض
                
                إذا لم يكن متجر إلكتروني، حلل الخدمات المقدمة بنفس التفصيل.
                """,
                agent=self.ecommerce_specialist,
                expected_output="تحليل التجارة الإلكترونية أو الخدمات مع التوصيات"
            )
            
            # إنشاء الفريق وتنفيذ المهام
            analysis_crew = Crew(
                agents=[
                    self.website_analyzer,
                    self.seo_specialist, 
                    self.saudi_market_expert,
                    self.competitor_researcher,
                    self.ecommerce_specialist
                ],
                tasks=[
                    general_analysis_task,
                    seo_analysis_task,
                    saudi_compliance_task,
                    competitor_analysis_task,
                    ecommerce_analysis_task
                ],
                verbose=True,
                process="sequential"
            )
            
            # تنفيذ التحليل
            logger.info("🔍 تنفيذ تحليل الموقع...")
            result = analysis_crew.kickoff()
            
            # معالجة النتائج وتحويلها إلى نموذج مهيكل
            analysis_result = self._process_analysis_results(url, result)
            
            logger.info(f"✅ اكتمل تحليل الموقع: {url}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"❌ خطأ في تحليل الموقع {url}: {str(e)}")
            raise

    def _process_analysis_results(self, url: str, raw_results: Any) -> WebsiteAnalysisResult:
        """معالجة النتائج الخام وتحويلها إلى نموذج مهيكل"""
        
        try:
            # استخراج البيانات من النتائج
            # هذا مثال - يجب تخصيصه حسب شكل النتائج الفعلية
            
            return WebsiteAnalysisResult(
                url=url,
                title=self._extract_title(raw_results),
                description=self._extract_description(raw_results),
                business_type=self._extract_business_type(raw_results),
                industry=self._extract_industry(raw_results),
                products=self._extract_products(raw_results),
                services=self._extract_services(raw_results),
                contact_info=self._extract_contact_info(raw_results),
                social_media=self._extract_social_media(raw_results),
                competitors=self._extract_competitors(raw_results),
                seo_analysis=self._extract_seo_analysis(raw_results),
                saudi_compliance=self._extract_saudi_compliance(raw_results),
                ecommerce_data=self._extract_ecommerce_data(raw_results),
                content_analysis=self._extract_content_analysis(raw_results),
                recommendations=self._extract_recommendations(raw_results),
                confidence_score=self._calculate_confidence_score(raw_results),
                analysis_timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"خطأ في معالجة النتائج: {str(e)}")
            # إرجاع نتيجة افتراضية في حالة الخطأ
            return self._create_default_result(url)

    def _extract_title(self, results) -> str:
        """استخراج عنوان الموقع"""
        try:
            # منطق استخراج العنوان
            return "عنوان الموقع"
        except:
            return ""

    def _extract_description(self, results) -> str:
        """استخراج وصف الموقع"""
        try:
            return "وصف الموقع"
        except:
            return ""

    def _extract_business_type(self, results) -> str:
        """تحديد نوع العمل"""
        try:
            return "تجارة إلكترونية"
        except:
            return "غير محدد"

    def _extract_industry(self, results) -> str:
        """تحديد الصناعة"""
        try:
            return "التجارة الإلكترونية"
        except:
            return "غير محدد"

    def _extract_products(self, results) -> List[Dict]:
        """استخراج قائمة المنتجات"""
        try:
            return []
        except:
            return []

    def _extract_services(self, results) -> List[Dict]:
        """استخراج قائمة الخدمات"""
        try:
            return []
        except:
            return []

    def _extract_contact_info(self, results) -> Dict:
        """استخراج معلومات التواصل"""
        try:
            return {}
        except:
            return {}

    def _extract_social_media(self, results) -> Dict:
        """استخراج روابط وسائل التواصل"""
        try:
            return {}
        except:
            return {}

    def _extract_competitors(self, results) -> List[str]:
        """استخراج قائمة المنافسين"""
        try:
            return []
        except:
            return []

    def _extract_seo_analysis(self, results) -> Dict:
        """استخراج تحليل SEO"""
        try:
            return {}
        except:
            return {}

    def _extract_saudi_compliance(self, results) -> Dict:
        """استخراج تحليل التوافق السعودي"""
        try:
            return {}
        except:
            return {}

    def _extract_ecommerce_data(self, results) -> Dict:
        """استخراج بيانات التجارة الإلكترونية"""
        try:
            return {}
        except:
            return {}

    def _extract_content_analysis(self, results) -> Dict:
        """استخراج تحليل المحتوى"""
        try:
            return {}
        except:
            return {}

    def _extract_recommendations(self, results) -> List[str]:
        """استخراج التوصيات"""
        try:
            return []
        except:
            return []

    def _calculate_confidence_score(self, results) -> float:
        """حساب نقاط الثقة في التحليل"""
        try:
            return 0.85
        except:
            return 0.5

    def _create_default_result(self, url: str) -> WebsiteAnalysisResult:
        """إنشاء نتيجة افتراضية في حالة الخطأ"""
        return WebsiteAnalysisResult(
            url=url,
            title="",
            description="",
            business_type="غير محدد",
            industry="غير محدد",
            products=[],
            services=[],
            contact_info={},
            social_media={},
            competitors=[],
            seo_analysis={},
            saudi_compliance={},
            ecommerce_data={},
            content_analysis={},
            recommendations=["يتطلب تحليل يدوي إضافي"],
            confidence_score=0.0,
            analysis_timestamp=datetime.now()
        )

# دالة مساعدة للاستخدام السريع
async def quick_website_analysis(url: str) -> WebsiteAnalysisResult:
    """🚀 تحليل سريع للموقع"""
    scraper = MorvoWebsiteScraper()
    return await scraper.analyze_website(url)

# مثال للاستخدام
if __name__ == "__main__":
    import asyncio
    
    async def test_analysis():
        url = "https://example-saudi-store.com"
        result = await quick_website_analysis(url)
        print(f"تم تحليل الموقع: {result.title}")
        print(f"نوع العمل: {result.business_type}")
        print(f"نقاط الثقة: {result.confidence_score}")
    
    # تشغيل الاختبار
    # asyncio.run(test_analysis())
