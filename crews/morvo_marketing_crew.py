"""
Morvo Marketing Crew - Complete Integration System for M1-M5 Agents
Designed for Railway hosting with MCP, Supabase, and Zapier integrations
"""
from crewai import Crew, Process
from typing import Dict, Any, List, Optional
import json
import os
from datetime import datetime
from agents.morvo_marketing_agents import MorvoMarketingAgents
from tasks.morvo_marketing_tasks import MorvoMarketingTasks

class MorvoMarketingCrew:
    """
    Complete Morvo Marketing automation system with 5 specialized agents (M1-M5)
    Integrates with Railway, MCP, Supabase, and Zapier for full automation
    """
    
    def __init__(self):
        self.agents = MorvoMarketingAgents()
        self.tasks = MorvoMarketingTasks()
        self.results_directory = "results"
        self.ensure_results_directory()
    
    def ensure_results_directory(self):
        """Create results directory if it doesn't exist"""
        if not os.path.exists(self.results_directory):
            os.makedirs(self.results_directory)
    
    def run_strategic_analysis(self, company_info: Dict[str, Any]) -> str:
        """
        Run M1 Strategic Analysis - Advanced market research and ROI optimization
        """
        crew = Crew(
            agents=[self.agents.m1_strategic_manager_agent()],
            tasks=[self.tasks.m1_strategic_analysis_task(company_info)],
            process=Process.sequential,
            verbose=True,
            memory=True
        )
        
        result = crew.kickoff()
        filename = self.save_result(result, "m1_strategic_analysis")
        return f"Strategic analysis completed and saved to {filename}"
    
    def run_social_media_monitoring(self, company_info: Dict[str, Any]) -> str:
        """
        Run M2 Social Media Monitoring - Real-time monitoring and crisis management
        """
        crew = Crew(
            agents=[self.agents.m2_social_media_manager_agent()],
            tasks=[self.tasks.m2_social_monitoring_task(company_info)],
            process=Process.sequential,
            verbose=True,
            memory=True
        )
        
        result = crew.kickoff()
        filename = self.save_result(result, "m2_social_monitoring")
        return f"Social media monitoring completed and saved to {filename}"
    
    def run_campaign_optimization(self, campaign_info: Dict[str, Any]) -> str:
        """
        Run M3 Campaign Optimization - Auto-optimization and A/B testing
        """
        crew = Crew(
            agents=[self.agents.m3_campaign_manager_agent()],
            tasks=[self.tasks.m3_campaign_optimization_task(campaign_info)],
            process=Process.sequential,
            verbose=True,
            memory=True
        )
        
        result = crew.kickoff()
        filename = self.save_result(result, "m3_campaign_optimization")
        return f"Campaign optimization completed and saved to {filename}"
    
    def run_content_strategy(self, company_info: Dict[str, Any]) -> str:
        """
        Run M4 Content Strategy - Comprehensive content planning and calendar management
        """
        crew = Crew(
            agents=[self.agents.m4_content_manager_agent()],
            tasks=[self.tasks.m4_content_strategy_task(company_info)],
            process=Process.sequential,
            verbose=True,
            memory=True
        )
        
        result = crew.kickoff()
        filename = self.save_result(result, "m4_content_strategy")
        return f"Content strategy completed and saved to {filename}"
    
    def run_data_analytics(self, analysis_period: str = "آخر 30 يوم") -> str:
        """
        Run M5 Data Analytics - Comprehensive business intelligence and reporting
        """
        crew = Crew(
            agents=[self.agents.m5_data_manager_agent()],
            tasks=[self.tasks.m5_data_analytics_task(analysis_period)],
            process=Process.sequential,
            verbose=True,
            memory=True
        )
        
        result = crew.kickoff()
        filename = self.save_result(result, "m5_data_analytics")
        return f"Data analytics completed and saved to {filename}"
    
    def run_market_analysis_crew(self, company_info: Dict[str, Any]) -> str:
        """
        Run Market Analysis Crew: M1 (Strategic) + M5 (Data Analytics)
        """
        market_analysis_agents = [
            self.agents.m1_strategic_manager_agent(),
            self.agents.m5_data_manager_agent()
        ]
        
        market_analysis_tasks = [
            self.tasks.m1_strategic_analysis_task(company_info),
            self.tasks.m5_data_analytics_task()
        ]
        
        crew = Crew(
            agents=market_analysis_agents,
            tasks=market_analysis_tasks,
            process=Process.sequential,
            verbose=True,
            memory=True
        )
        
        result = crew.kickoff()
        filename = self.save_result(result, "market_analysis_crew")
        return f"Market analysis crew completed and saved to {filename}"
    
    def run_content_and_social_crew(self, company_info: Dict[str, Any]) -> str:
        """
        Run Content & Social Crew: M2 (Social Media) + M4 (Content Strategy)
        """
        content_social_agents = [
            self.agents.m4_content_manager_agent(),
            self.agents.m2_social_media_manager_agent()
        ]
        
        content_social_tasks = [
            self.tasks.m4_content_strategy_task(company_info),
            self.tasks.m2_social_monitoring_task(company_info)
        ]
        
        crew = Crew(
            agents=content_social_agents,
            tasks=content_social_tasks,
            process=Process.sequential,
            verbose=True,
            memory=True
        )
        
        result = crew.kickoff()
        filename = self.save_result(result, "content_social_crew")
        return f"Content and social crew completed and saved to {filename}"
    
    def run_campaign_execution_crew(self, company_info: Dict[str, Any], 
                                  campaign_info: Dict[str, Any]) -> str:
        """
        Run Campaign Execution Crew: M3 (Campaign Manager) + M2 (Social Media) + M5 (Analytics)
        """
        campaign_agents = [
            self.agents.m3_campaign_manager_agent(),
            self.agents.m2_social_media_manager_agent(),
            self.agents.m5_data_manager_agent()
        ]
        
        campaign_tasks = [
            self.tasks.m3_campaign_optimization_task(campaign_info),
            self.tasks.m2_social_monitoring_task(company_info),
            self.tasks.m5_data_analytics_task()
        ]
        
        crew = Crew(
            agents=campaign_agents,
            tasks=campaign_tasks,
            process=Process.sequential,
            verbose=True,
            memory=True
        )
        
        result = crew.kickoff()
        filename = self.save_result(result, "campaign_execution_crew")
        return f"Campaign execution crew completed and saved to {filename}"
    
    def run_complete_marketing_automation(self, 
                                        company_info: Dict[str, Any],
                                        campaign_info: Optional[Dict[str, Any]] = None) -> str:
        """
        Run Complete Marketing Automation with all 5 agents (M1-M5)
        The ultimate workflow for comprehensive marketing automation
        """
        # All 5 agents in the marketing automation workflow
        all_agents = [
            self.agents.m1_strategic_manager_agent(),    # Strategic Analysis
            self.agents.m4_content_manager_agent(),      # Content Strategy
            self.agents.m2_social_media_manager_agent(), # Social Media Monitoring
            self.agents.m5_data_manager_agent()          # Data Analytics
        ]
        
        # Core tasks for complete automation
        all_tasks = [
            self.tasks.m1_strategic_analysis_task(company_info),
            self.tasks.m4_content_strategy_task(company_info),
            self.tasks.m2_social_monitoring_task(company_info),
            self.tasks.m5_data_analytics_task()
        ]
        
        # Add campaign optimization if campaign info is provided
        if campaign_info:
            all_agents.append(self.agents.m3_campaign_manager_agent())
            all_tasks.append(self.tasks.m3_campaign_optimization_task(campaign_info))
        
        crew = Crew(
            agents=all_agents,
            tasks=all_tasks,
            process=Process.sequential,
            verbose=True,
            memory=True,
            max_rpm=100  # Rate limiting for API calls
        )
        
        result = crew.kickoff()
        filename = self.save_result(result, "complete_marketing_automation")
        return f"Complete marketing automation completed and saved to {filename}"
    
    def save_result(self, result: Any, operation_name: str) -> str:
        """
        Save results to file with timestamp and return filename
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.results_directory}/{operation_name}_{timestamp}.json"
        
        # Convert result to string if it's not already
        if hasattr(result, 'raw'):
            result_data = result.raw
        else:
            result_data = str(result)
        
        # Create a structured result
        structured_result = {
            "operation": operation_name,
            "timestamp": timestamp,
            "result": result_data,
            "status": "completed"
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(structured_result, f, ensure_ascii=False, indent=2)
        
        return filename
    
    def get_integration_details(self) -> Dict[str, Any]:
        """
        Get complete integration details for Morvo platform
        """
        return {
            "platform": "Railway",
            "backend": "Supabase PostgreSQL",
            "context_protocol": "MCP (Model Context Protocol)",
            "automation": ["Zapier", "Make (Integromat)", "IFTTT"],
            "agents": {
                "M1": "Ahmed - Strategic Manager (ROI optimization, market intelligence)",
                "M2": "Fatima - Social Media Manager (Real-time monitoring, crisis management)",
                "M3": "Mohammed - Campaign Manager (Auto-optimization, A/B testing)",
                "M4": "Nora - Content Manager (Content strategy, calendar management)",
                "M5": "Khalid - Data Manager (Business intelligence, comprehensive analytics)"
            },
            "apis": {
                "social_media": [
                    "Facebook/Instagram Graph API",
                    "Twitter API v2", 
                    "LinkedIn API",
                    "TikTok API",
                    "YouTube API"
                ],
                "analytics": [
                    "Google Analytics 4",
                    "Google Ads API",
                    "Facebook Ads API",
                    "Search Console API"
                ],
                "business_intelligence": [
                    "SEMrush API",
                    "Ahrefs API", 
                    "SimilarWeb API",
                    "Brand24 API"
                ],
                "ai_services": [
                    "OpenAI GPT-4o",
                    "Perplexity AI (via SerperDevTool)",
                    "WebsiteSearchTool"
                ]
            },
            "environment_variables": [
                "OPENAI_API_KEY",
                "SERPER_API_KEY", 
                "SUPABASE_URL",
                "SUPABASE_KEY",
                "ZAPIER_API_KEY",
                "FACEBOOK_ACCESS_TOKEN",
                "TWITTER_BEARER_TOKEN",
                "LINKEDIN_ACCESS_TOKEN",
                "GOOGLE_ANALYTICS_CREDENTIALS",
                "SEMRUSH_API_KEY"
            ],
            "deployment": {
                "platform": "Railway",
                "container": "Docker",
                "scaling": "Auto-scaling based on demand",
                "monitoring": "Railway metrics + custom logging"
            }
        }

# Example usage and testing
if __name__ == "__main__":
    # Initialize the crew
    crew = MorvoMarketingCrew()
    
    # Sample company info for testing
    sample_company = {
        "name": "تطبيق توصيل الطعام السريع",
        "website": "https://fastfood-delivery.sa",
        "industry": "خدمات توصيل الطعام",
        "target_market": "السعودية ودول الخليج",
        "target_audience": "الشباب والعائلات في المدن الكبرى",
        "brand_message": "توصيل سريع وآمن للطعام اللذيذ"
    }
    
    # Sample campaign info
    sample_campaign = {
        "objective": "زيادة عدد المستخدمين الجدد بنسبة 50%",
        "budget": "100,000 ريال سعودي",
        "duration": "45 يوم",
        "platforms": "فيسبوك، إنستغرام، تيك توك، سناب شات"
    }
    
    print("=== Morvo Marketing Crew Demo ===")
    print("Available operations:")
    print("1. Strategic Analysis (M1)")
    print("2. Social Media Monitoring (M2)")
    print("3. Campaign Optimization (M3)")
    print("4. Content Strategy (M4)")
    print("5. Data Analytics (M5)")
    print("6. Complete Marketing Automation (All agents)")
    print("7. Show Integration Details")
    
    # For demo purposes, you can uncomment any of these:
    # result = crew.run_strategic_analysis(sample_company)
    # result = crew.run_complete_marketing_automation(sample_company, sample_campaign)
    # integration_info = crew.get_integration_details()
    # print(json.dumps(integration_info, indent=2, ensure_ascii=False))
