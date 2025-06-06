"""
Smart Alerts System for Morvo AI Marketing Platform
Monitors data patterns and triggers intelligent notifications for marketing opportunities
"""

from typing import Dict, List, Any, Optional, Tuple
import asyncio
import logging
from datetime import datetime, timedelta
import json
import os

from agent_memory import AgentMemoryManager
from agent_context_manager import AgentContextManager

# Configure logging
logger = logging.getLogger(__name__)

class SmartAlertSystem:
    """
    Intelligent alert system for Morvo AI Marketing Platform
    Monitors marketing data and triggers timely notifications
    """
    
    def __init__(self):
        """Initialize the alert system with required components"""
        self.memory_manager = AgentMemoryManager()
        self.context_manager = AgentContextManager()
        self.alert_thresholds = self._load_alert_thresholds()
        self.alert_history = {}
        
    def _load_alert_thresholds(self) -> Dict[str, Any]:
        """Load alert thresholds from configuration or use defaults"""
        # Default thresholds for different alert types
        return {
            "traffic_spike": {
                "percentage_change": 30,  # 30% increase
                "minimum_volume": 100,    # At least 100 visits
                "time_window_hours": 24   # Within 24 hours
            },
            "keyword_opportunity": {
                "search_volume_increase": 40,  # 40% increase
                "competition_max": 0.6,        # Medium competition or lower
                "relevance_min": 0.7           # High relevance to business
            },
            "engagement_spike": {
                "percentage_increase": 50,     # 50% above normal
                "minimum_engagements": 50,     # At least 50 engagements
                "time_window_hours": 4         # Within 4 hours
            },
            "sentiment_shift": {
                "sentiment_change": 0.2,       # 0.2 point shift (on -1 to 1 scale)
                "minimum_mentions": 20,        # At least 20 mentions
                "time_window_hours": 48        # Within 48 hours
            },
            "conversion_opportunity": {
                "conversion_increase": 25,     # 25% increase in conversions
                "minimum_conversions": 10,     # At least 10 conversions
                "time_window_hours": 24        # Within 24 hours
            }
        }
    
    async def check_traffic_opportunity(self, company_id: str) -> Optional[Dict[str, Any]]:
        """
        Check for significant traffic increases that represent opportunities
        
        Args:
            company_id: Company identifier
            
        Returns:
            Alert data if opportunity detected, None otherwise
        """
        # Get latest analytics data from M5 agent
        context = await self.context_manager.get_synchronized_context(
            company_id=company_id,
            agent_id="M5",
            context_keys=["analytics_data", "traffic_sources"]
        )
        
        if "data" not in context or not context["data"]:
            return None
            
        analytics_data = context["data"].get("analytics_data", {})
        traffic_sources = context["data"].get("traffic_sources", {})
        
        # Check if we have enough data
        if not analytics_data or not traffic_sources:
            return None
            
        # Check for traffic spikes by source
        thresholds = self.alert_thresholds["traffic_spike"]
        opportunities = []
        
        for source, data in traffic_sources.items():
            if "current" in data and "previous" in data:
                current_traffic = data["current"]
                previous_traffic = data["previous"]
                
                if previous_traffic > 0 and current_traffic >= thresholds["minimum_volume"]:
                    percentage_change = ((current_traffic - previous_traffic) / previous_traffic) * 100
                    
                    if percentage_change >= thresholds["percentage_change"]:
                        opportunities.append({
                            "source": source,
                            "current_traffic": current_traffic,
                            "previous_traffic": previous_traffic,
                            "percentage_change": round(percentage_change, 1),
                            "opportunity_score": min(100, int(percentage_change))
                        })
        
        if not opportunities:
            return None
            
        # Sort by opportunity score (highest first)
        opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)
        
        # Create alert data
        alert_data = {
            "alert_type": "traffic_opportunity",
            "alert_priority": "medium",
            "timestamp": datetime.utcnow().isoformat(),
            "company_id": company_id,
            "opportunities": opportunities,
            "recommended_actions": self._get_traffic_recommendations(opportunities[0]["source"]),
            "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()
        }
        
        return alert_data
    
    def _get_traffic_recommendations(self, traffic_source: str) -> List[Dict[str, str]]:
        """Generate recommendations based on traffic source"""
        # Source-specific recommendations
        recommendations = []
        
        if traffic_source.lower() == "organic":
            recommendations = [
                {"action": "content_boost", "description": "إنشاء 3 مقالات إضافية حول الموضوع المتصدر"},
                {"action": "keyword_focus", "description": "زيادة التركيز على الكلمات المفتاحية ذات الأداء العالي"},
                {"action": "social_promotion", "description": "مشاركة المحتوى عالي الأداء على منصات التواصل الاجتماعي"}
            ]
        elif traffic_source.lower() == "social":
            recommendations = [
                {"action": "boost_post", "description": "ترويج المنشورات عالية الأداء بميزانية إضافية"},
                {"action": "create_similar", "description": "إنشاء محتوى مشابه للمحتوى عالي الأداء"},
                {"action": "engagement_campaign", "description": "إطلاق حملة تفاعلية لزيادة المشاركة"}
            ]
        elif traffic_source.lower() == "direct":
            recommendations = [
                {"action": "retention_campaign", "description": "حملة احتفاظ بالزوار المباشرين"},
                {"action": "special_offer", "description": "تقديم عرض خاص للزوار المباشرين"},
                {"action": "remarketing", "description": "استهداف الزوار المباشرين بحملة إعادة تسويق"}
            ]
        elif traffic_source.lower() == "referral":
            recommendations = [
                {"action": "partnership_expand", "description": "توسيع الشراكة مع المواقع المحيلة"},
                {"action": "backlink_campaign", "description": "حملة بناء روابط خلفية جديدة"},
                {"action": "referral_program", "description": "إطلاق برنامج إحالة مكافآت"}
            ]
        else:
            # Generic recommendations
            recommendations = [
                {"action": "traffic_analysis", "description": "تحليل مصادر الزيارات بشكل متعمق"},
                {"action": "conversion_optimize", "description": "تحسين معدلات التحويل للزوار الجدد"},
                {"action": "content_tailor", "description": "تخصيص المحتوى بناءً على مصدر الزيارة"}
            ]
            
        return recommendations
    
    async def check_keyword_opportunity(self, company_id: str) -> Optional[Dict[str, Any]]:
        """
        Check for keyword ranking opportunities
        
        Args:
            company_id: Company identifier
            
        Returns:
            Alert data if opportunity detected, None otherwise
        """
        # Get latest SEO data from M1 agent
        context = await self.context_manager.get_synchronized_context(
            company_id=company_id,
            agent_id="M1",
            context_keys=["seo_data", "keyword_rankings"]
        )
        
        if "data" not in context or not context["data"]:
            return None
            
        seo_data = context["data"].get("seo_data", {})
        keyword_rankings = context["data"].get("keyword_rankings", {})
        
        # Check if we have enough data
        if not seo_data or not keyword_rankings:
            return None
            
        # Check for keyword opportunities
        thresholds = self.alert_thresholds["keyword_opportunity"]
        opportunities = []
        
        for keyword, data in keyword_rankings.items():
            if all(k in data for k in ["current_volume", "previous_volume", "competition", "relevance"]):
                current_volume = data["current_volume"]
                previous_volume = data["previous_volume"]
                competition = data["competition"]  # 0-1 scale
                relevance = data["relevance"]      # 0-1 scale
                current_rank = data.get("current_rank", 100)
                
                if (previous_volume > 0 and 
                    competition <= thresholds["competition_max"] and
                    relevance >= thresholds["relevance_min"]):
                    
                    volume_increase = ((current_volume - previous_volume) / previous_volume) * 100
                    
                    if volume_increase >= thresholds["search_volume_increase"]:
                        opportunity_score = min(100, int(
                            (volume_increase * 0.4) + 
                            ((1 - competition) * 30) + 
                            (relevance * 30)
                        ))
                        
                        opportunities.append({
                            "keyword": keyword,
                            "current_volume": current_volume,
                            "volume_increase": round(volume_increase, 1),
                            "competition": competition,
                            "relevance": relevance,
                            "current_rank": current_rank,
                            "opportunity_score": opportunity_score
                        })
        
        if not opportunities:
            return None
            
        # Sort by opportunity score (highest first)
        opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)
        
        # Limit to top 5 opportunities
        top_opportunities = opportunities[:5]
        
        # Create alert data
        alert_data = {
            "alert_type": "keyword_opportunity",
            "alert_priority": "high",
            "timestamp": datetime.utcnow().isoformat(),
            "company_id": company_id,
            "opportunities": top_opportunities,
            "recommended_actions": self._get_keyword_recommendations(top_opportunities),
            "expires_at": (datetime.utcnow() + timedelta(hours=72)).isoformat()
        }
        
        return alert_data
    
    def _get_keyword_recommendations(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Generate keyword-specific recommendations"""
        recommendations = []
        
        # Get top keywords
        top_keywords = [o["keyword"] for o in opportunities[:3]]
        
        # Add general recommendations
        recommendations.append({
            "action": "content_creation",
            "description": f"إنشاء محتوى يستهدف الكلمات: {', '.join(top_keywords)}"
        })
        
        recommendations.append({
            "action": "ad_campaign",
            "description": f"إطلاق حملة إعلانية مدفوعة تستهدف: {top_keywords[0]}"
        })
        
        # Add rank-specific recommendations
        for opportunity in opportunities[:2]:
            current_rank = opportunity.get("current_rank", 100)
            keyword = opportunity["keyword"]
            
            if current_rank <= 20 and current_rank > 10:
                recommendations.append({
                    "action": "rank_boost",
                    "description": f"تحسين الكلمة '{keyword}' من المركز {current_rank} إلى الصفحة الأولى"
                })
            elif current_rank <= 10 and current_rank > 3:
                recommendations.append({
                    "action": "top3_push",
                    "description": f"دفع الكلمة '{keyword}' من المركز {current_rank} إلى أول 3 نتائج"
                })
                
        # Add specific content recommendation
        if opportunities and opportunities[0]["competition"] < 0.4:
            recommendations.append({
                "action": "pillar_content",
                "description": f"إنشاء محتوى شامل (2000+ كلمة) عن '{opportunities[0]['keyword']}'"
            })
            
        return recommendations
    
    async def check_social_engagement_opportunity(self, company_id: str) -> Optional[Dict[str, Any]]:
        """
        Check for social media engagement spikes that represent opportunities
        
        Args:
            company_id: Company identifier
            
        Returns:
            Alert data if opportunity detected, None otherwise
        """
        # Get latest social media data from M2 agent
        context = await self.context_manager.get_synchronized_context(
            company_id=company_id,
            agent_id="M2",
            context_keys=["social_analytics", "engagement_metrics"]
        )
        
        if "data" not in context or not context["data"]:
            return None
            
        social_analytics = context["data"].get("social_analytics", {})
        engagement_metrics = context["data"].get("engagement_metrics", {})
        
        # Check if we have enough data
        if not social_analytics or not engagement_metrics:
            return None
            
        # Check for engagement spikes by platform and content
        thresholds = self.alert_thresholds["engagement_spike"]
        opportunities = []
        
        # Check each platform
        platforms = social_analytics.get("platforms", {})
        for platform, data in platforms.items():
            recent_posts = data.get("recent_posts", [])
            
            for post in recent_posts:
                if all(k in post for k in ["post_id", "engagement_rate", "average_engagement_rate", "total_engagements"]):
                    current_rate = post["engagement_rate"]
                    average_rate = post["average_engagement_rate"]
                    total_engagements = post["total_engagements"]
                    
                    if (average_rate > 0 and 
                        total_engagements >= thresholds["minimum_engagements"]):
                        
                        percentage_increase = ((current_rate - average_rate) / average_rate) * 100
                        
                        if percentage_increase >= thresholds["percentage_increase"]:
                            opportunities.append({
                                "platform": platform,
                                "post_id": post["post_id"],
                                "post_type": post.get("type", "unknown"),
                                "content_snippet": post.get("content_snippet", ""),
                                "current_engagement_rate": round(current_rate, 2),
                                "average_engagement_rate": round(average_rate, 2),
                                "total_engagements": total_engagements,
                                "percentage_increase": round(percentage_increase, 1),
                                "opportunity_score": min(100, int(percentage_increase))
                            })
        
        if not opportunities:
            return None
            
        # Sort by opportunity score (highest first)
        opportunities.sort(key=lambda x: x["opportunity_score"], reverse=True)
        
        # Create alert data
        alert_data = {
            "alert_type": "social_engagement_opportunity",
            "alert_priority": "high",
            "timestamp": datetime.utcnow().isoformat(),
            "company_id": company_id,
            "opportunities": opportunities[:3],  # Top 3 opportunities
            "recommended_actions": self._get_social_recommendations(opportunities[0]),
            "expires_at": (datetime.utcnow() + timedelta(hours=6)).isoformat()  # Time-sensitive
        }
        
        return alert_data
    
    def _get_social_recommendations(self, opportunity: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate social-specific recommendations"""
        platform = opportunity["platform"].lower()
        post_type = opportunity["post_type"].lower()
        
        recommendations = [
            {
                "action": "boost_post",
                "description": f"ترويج المنشور عالي الأداء على {platform} بميزانية 50-100 ريال"
            },
            {
                "action": "create_similar",
                "description": f"إنشاء 2-3 منشورات مشابهة بنفس الأسلوب والمحتوى"
            }
        ]
        
        # Platform-specific recommendations
        if platform == "instagram":
            recommendations.append({
                "action": "story_highlight",
                "description": "تحويل المحتوى عالي الأداء إلى قصة مميزة (Highlight)"
            })
        elif platform == "facebook":
            recommendations.append({
                "action": "audience_expand",
                "description": "توسيع الجمهور المستهدف بناءً على تفاعلات المنشور الناجح"
            })
        elif platform == "twitter" or platform == "x":
            recommendations.append({
                "action": "hashtag_campaign",
                "description": "إطلاق حملة هاشتاج مرتبطة بالمحتوى عالي الأداء"
            })
        elif platform == "linkedin":
            recommendations.append({
                "action": "article_expand",
                "description": "تطوير المنشور إلى مقال كامل على LinkedIn"
            })
        elif platform == "tiktok":
            recommendations.append({
                "action": "challenge_create",
                "description": "إنشاء تحدي مرتبط بالمحتوى عالي الأداء"
            })
            
        # Content type recommendations
        if post_type == "video":
            recommendations.append({
                "action": "video_series",
                "description": "تطوير سلسلة فيديوهات قصيرة مبنية على المحتوى الناجح"
            })
        elif post_type == "image":
            recommendations.append({
                "action": "carousel_expand",
                "description": "تطوير المحتوى إلى carousel متعدد الصور مع تفاصيل إضافية"
            })
        elif post_type == "text":
            recommendations.append({
                "action": "visual_transform",
                "description": "تحويل المحتوى النصي إلى رسومات معلوماتية أو صور جذابة"
            })
            
        return recommendations
        
    async def check_all_opportunities(self, company_id: str) -> List[Dict[str, Any]]:
        """
        Check all opportunity types for a company
        
        Args:
            company_id: Company identifier
            
        Returns:
            List of alert data for detected opportunities
        """
        opportunities = []
        
        # Run all opportunity checks in parallel
        results = await asyncio.gather(
            self.check_traffic_opportunity(company_id),
            self.check_keyword_opportunity(company_id),
            self.check_social_engagement_opportunity(company_id),
            return_exceptions=True
        )
        
        # Process successful results
        for result in results:
            if isinstance(result, dict) and "alert_type" in result:
                opportunities.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Error checking opportunities: {result}")
                
        return opportunities
    
    async def store_alert(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Store alert in the system and notify relevant agents
        
        Args:
            alert_data: Alert data to store
            
        Returns:
            Result of the storage operation
        """
        if "company_id" not in alert_data or "alert_type" not in alert_data:
            return {"status": "error", "message": "Missing required alert data"}
            
        company_id = alert_data["company_id"]
        alert_type = alert_data["alert_type"]
        
        # Map alert types to relevant agents
        alert_agent_mapping = {
            "traffic_opportunity": ["M5", "M1", "M3"],
            "keyword_opportunity": ["M1", "M4", "M3"],
            "social_engagement_opportunity": ["M2", "M4", "M3"],
            "sentiment_shift": ["M2", "M4", "M3"],
            "conversion_opportunity": ["M3", "M5", "M1"]
        }
        
        # Get relevant agents
        relevant_agents = alert_agent_mapping.get(alert_type, ["M5"])
        
        # Store alert in memory system for relevant agents
        results = {}
        for agent_id in relevant_agents:
            try:
                # Store as memory
                result = await self.memory_manager.store_memory(
                    agent_id=agent_id,
                    company_id=company_id,
                    memory_data={
                        "alert_data": alert_data,
                        "alert_timestamp": datetime.utcnow().isoformat(),
                        "alert_type": alert_type,
                        "is_alert": True
                    }
                )
                results[agent_id] = result
                
            except Exception as e:
                logger.error(f"Error storing alert for agent {agent_id}: {e}")
                results[agent_id] = {"status": "error", "message": str(e)}
                
        # Track in alert history
        alert_id = f"{company_id}_{alert_type}_{datetime.utcnow().isoformat()}"
        self.alert_history[alert_id] = {
            "alert_data": alert_data,
            "notified_agents": relevant_agents,
            "created_at": datetime.utcnow().isoformat()
        }
        
        return {
            "status": "success",
            "message": f"Alert stored and shared with {len(relevant_agents)} agents",
            "alert_id": alert_id,
            "results": results
        }
    
    async def get_active_alerts(self, company_id: str) -> List[Dict[str, Any]]:
        """
        Get all active alerts for a company
        
        Args:
            company_id: Company identifier
            
        Returns:
            List of active alerts
        """
        active_alerts = []
        current_time = datetime.utcnow()
        
        # Check all agents for alerts
        all_agents = ["M1", "M2", "M3", "M4", "M5"]
        
        for agent_id in all_agents:
            try:
                # Get memories that contain alerts
                memories = await self.memory_manager.get_memories(
                    agent_id=agent_id,
                    company_id=company_id,
                    limit=20  # Get a reasonable number of recent memories
                )
                
                # Filter for alert data
                for memory in memories:
                    if "is_alert" in memory and memory["is_alert"]:
                        alert_data = memory.get("alert_data", {})
                        
                        # Check if alert is still active
                        if "expires_at" in alert_data:
                            expires_at = datetime.fromisoformat(alert_data["expires_at"].replace("Z", "+00:00"))
                            if expires_at > current_time:
                                # Add agent_id to alert data
                                alert_data["source_agent"] = agent_id
                                active_alerts.append(alert_data)
            
            except Exception as e:
                logger.error(f"Error getting alerts from agent {agent_id}: {e}")
                
        # Remove duplicates (same alert type and content)
        unique_alerts = []
        alert_keys = set()
        
        for alert in active_alerts:
            key = f"{alert['alert_type']}_{alert.get('timestamp', '')}"
            if key not in alert_keys:
                alert_keys.add(key)
                unique_alerts.append(alert)
                
        # Sort by priority and timestamp
        priority_values = {"high": 3, "medium": 2, "low": 1}
        unique_alerts.sort(
            key=lambda x: (
                priority_values.get(x.get("alert_priority", "low"), 0),
                x.get("timestamp", "")
            ),
            reverse=True
        )
        
        return unique_alerts
