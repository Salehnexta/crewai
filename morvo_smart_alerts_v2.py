#!/usr/bin/env python3
"""
🔔 Morvo AI Smart Alerts System v2.0
Real-time intelligent alerts integrated with WebSocket and SEMrush data
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import os
from dataclasses import dataclass, asdict
import aiohttp
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("morvo_smart_alerts")

class AlertPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertCategory(Enum):
    SEO_OPPORTUNITY = "seo_opportunity"
    KEYWORD_RANKING = "keyword_ranking" 
    COMPETITOR_ACTIVITY = "competitor_activity"
    TRAFFIC_ANOMALY = "traffic_anomaly"
    CONVERSION_DROP = "conversion_drop"
    CAMPAIGN_PERFORMANCE = "campaign_performance"
    MARKET_TREND = "market_trend"

@dataclass
class SmartAlert:
    """Smart alert data structure"""
    id: str
    title: str
    message: str
    category: AlertCategory
    priority: AlertPriority
    data: Dict[str, Any]
    timestamp: str
    user_id: str
    organization_id: str
    action_url: Optional[str] = None
    expires_at: Optional[str] = None
    is_read: bool = False

class MorvoSmartAlertsV2:
    """
    Advanced Smart Alerts System for Morvo AI v2.0
    Integrates with WebSocket, SEMrush data, and real-time notifications
    """
    
    def __init__(self):
        """Initialize the smart alerts system"""
        self.alerts_queue = asyncio.Queue()
        self.websocket_connections = {}
        self.alert_rules = self._load_alert_rules()
        self.semrush_data_cache = {}
        self.last_check_time = datetime.now()
        
        # Railway/Production settings
        self.production_ws_url = "wss://crewai-production-d99a.up.railway.app"
        self.production_api_url = "https://crewai-production-d99a.up.railway.app"
        
    def _load_alert_rules(self) -> Dict[str, Any]:
        """Load alert rules configuration"""
        return {
            "keyword_ranking_drop": {
                "threshold": 5,  # positions
                "priority": AlertPriority.HIGH,
                "check_interval": 3600  # seconds
            },
            "traffic_spike": {
                "threshold": 0.3,  # 30% increase
                "priority": AlertPriority.MEDIUM,
                "check_interval": 1800
            },
            "competitor_new_content": {
                "threshold": 1,  # new pages
                "priority": AlertPriority.MEDIUM,
                "check_interval": 7200
            },
            "conversion_rate_drop": {
                "threshold": 0.2,  # 20% drop
                "priority": AlertPriority.CRITICAL,
                "check_interval": 900
            },
            "new_keyword_opportunity": {
                "threshold": 100,  # search volume
                "priority": AlertPriority.MEDIUM,
                "check_interval": 86400  # daily
            }
        }
    
    async def connect_to_production_ws(self, user_id: str) -> bool:
        """Connect to production WebSocket for real-time alerts"""
        try:
            import websockets
            
            ws_url = f"{self.production_ws_url}/ws/{user_id}"
            logger.info(f"🔌 Connecting to production WebSocket: {ws_url}")
            
            websocket = await websockets.connect(ws_url)
            self.websocket_connections[user_id] = websocket
            
            logger.info(f"✅ Connected to WebSocket for user: {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to WebSocket: {e}")
            return False
    
    async def send_alert_to_websocket(self, alert: SmartAlert):
        """Send smart alert through WebSocket"""
        try:
            websocket = self.websocket_connections.get(alert.user_id)
            if not websocket:
                logger.warning(f"⚠️ No WebSocket connection for user: {alert.user_id}")
                return False
            
            # Create rich alert message
            alert_message = {
                "type": "smart_alert",
                "alert_id": alert.id,
                "title": alert.title,
                "message": alert.message,
                "category": alert.category.value,
                "priority": alert.priority.value,
                "timestamp": alert.timestamp,
                "data": alert.data,
                "rich_components": [
                    {
                        "type": "alert_card",
                        "title": alert.title,
                        "description": alert.message,
                        "priority": alert.priority.value,
                        "action_button": {
                            "text": "View Details" if alert.action_url else "Acknowledge",
                            "url": alert.action_url
                        }
                    }
                ]
            }
            
            await websocket.send(json.dumps(alert_message))
            logger.info(f"📤 Alert sent via WebSocket: {alert.title}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send alert via WebSocket: {e}")
            return False
    
    async def check_seo_opportunities(self, organization_id: str) -> List[SmartAlert]:
        """Check for SEO opportunities using mock SEMrush data"""
        alerts = []
        
        try:
            # Mock SEMrush data check
            mock_opportunities = [
                {
                    "keyword": "تسويق رقمي السعودية",
                    "search_volume": 8100,
                    "difficulty": 45,
                    "current_position": None,
                    "opportunity_score": 85
                },
                {
                    "keyword": "التجارة الإلكترونية في الرياض",
                    "search_volume": 3200,
                    "difficulty": 38,
                    "current_position": None,
                    "opportunity_score": 78
                }
            ]
            
            for opportunity in mock_opportunities:
                if opportunity["opportunity_score"] > 75:
                    alert = SmartAlert(
                        id=f"seo_opp_{int(datetime.now().timestamp())}",
                        title=f"🎯 فرصة SEO جديدة: {opportunity['keyword']}",
                        message=f"كلمة مفتاحية عالية القيمة بحجم بحث {opportunity['search_volume']:,} ومنافسة متوسطة",
                        category=AlertCategory.SEO_OPPORTUNITY,
                        priority=AlertPriority.MEDIUM,
                        data=opportunity,
                        timestamp=datetime.now().isoformat(),
                        user_id="admin",
                        organization_id=organization_id,
                        action_url=f"/seo/opportunities/{opportunity['keyword']}"
                    )
                    alerts.append(alert)
            
        except Exception as e:
            logger.error(f"❌ Error checking SEO opportunities: {e}")
        
        return alerts
    
    async def check_competitor_activity(self, organization_id: str) -> List[SmartAlert]:
        """Monitor competitor activity"""
        alerts = []
        
        try:
            # Mock competitor data
            competitor_activities = [
                {
                    "competitor": "منافس رئيسي",
                    "activity": "نشر محتوى جديد",
                    "pages_added": 3,
                    "estimated_traffic": 1500,
                    "keywords_targeted": ["التسويق الرقمي", "السوق السعودي"]
                }
            ]
            
            for activity in competitor_activities:
                if activity["pages_added"] > 2:
                    alert = SmartAlert(
                        id=f"comp_act_{int(datetime.now().timestamp())}",
                        title=f"⚡ نشاط منافس: {activity['competitor']}",
                        message=f"أضاف {activity['pages_added']} صفحات جديدة بتقدير زيارات {activity['estimated_traffic']:,}",
                        category=AlertCategory.COMPETITOR_ACTIVITY,
                        priority=AlertPriority.MEDIUM,
                        data=activity,
                        timestamp=datetime.now().isoformat(),
                        user_id="admin",
                        organization_id=organization_id,
                        action_url=f"/competitors/{activity['competitor']}"
                    )
                    alerts.append(alert)
                    
        except Exception as e:
            logger.error(f"❌ Error checking competitor activity: {e}")
            
        return alerts
    
    async def check_traffic_anomalies(self, organization_id: str) -> List[SmartAlert]:
        """Detect traffic anomalies"""
        alerts = []
        
        try:
            # Mock traffic data
            current_traffic = 12500
            previous_traffic = 8200
            change_percent = ((current_traffic - previous_traffic) / previous_traffic) * 100
            
            if change_percent > 30:  # 30% spike
                alert = SmartAlert(
                    id=f"traffic_spike_{int(datetime.now().timestamp())}",
                    title="📈 ارتفاع مفاجئ في الزيارات!",
                    message=f"زيادة بنسبة {change_percent:.1f}% في الزيارات ({current_traffic:,} مقابل {previous_traffic:,})",
                    category=AlertCategory.TRAFFIC_ANOMALY,
                    priority=AlertPriority.HIGH,
                    data={
                        "current_traffic": current_traffic,
                        "previous_traffic": previous_traffic,
                        "change_percent": change_percent
                    },
                    timestamp=datetime.now().isoformat(),
                    user_id="admin",
                    organization_id=organization_id,
                    action_url="/analytics/traffic"
                )
                alerts.append(alert)
                
        except Exception as e:
            logger.error(f"❌ Error checking traffic anomalies: {e}")
            
        return alerts
    
    async def check_market_trends(self, organization_id: str) -> List[SmartAlert]:
        """Monitor market trends"""
        alerts = []
        
        try:
            # Mock trending topics
            trending_topics = [
                {
                    "topic": "الذكاء الاصطناعي في التجارة",
                    "growth_rate": 45,
                    "search_volume": 15600,
                    "relevance_score": 92
                },
                {
                    "topic": "التسوق الإلكتروني موسم الرياض",
                    "growth_rate": 78,
                    "search_volume": 23400,
                    "relevance_score": 88
                }
            ]
            
            for trend in trending_topics:
                if trend["growth_rate"] > 40 and trend["relevance_score"] > 85:
                    alert = SmartAlert(
                        id=f"trend_{int(datetime.now().timestamp())}",
                        title=f"🔥 اتجاه رائج: {trend['topic']}",
                        message=f"نمو بنسبة {trend['growth_rate']}% وحجم بحث {trend['search_volume']:,}",
                        category=AlertCategory.MARKET_TREND,
                        priority=AlertPriority.MEDIUM,
                        data=trend,
                        timestamp=datetime.now().isoformat(),
                        user_id="admin",
                        organization_id=organization_id,
                        action_url=f"/trends/{trend['topic']}"
                    )
                    alerts.append(alert)
                    
        except Exception as e:
            logger.error(f"❌ Error checking market trends: {e}")
            
        return alerts
    
    async def run_alert_checks(self, organization_id: str = "test_org"):
        """Run all alert checks and send notifications"""
        logger.info("🔍 Running smart alert checks...")
        
        # Connect to WebSocket first
        await self.connect_to_production_ws("admin")
        
        # Run all checks
        all_alerts = []
        
        seo_alerts = await self.check_seo_opportunities(organization_id)
        competitor_alerts = await self.check_competitor_activity(organization_id)
        traffic_alerts = await self.check_traffic_anomalies(organization_id)
        trend_alerts = await self.check_market_trends(organization_id)
        
        all_alerts.extend(seo_alerts)
        all_alerts.extend(competitor_alerts)
        all_alerts.extend(traffic_alerts)
        all_alerts.extend(trend_alerts)
        
        # Send alerts via WebSocket
        for alert in all_alerts:
            await self.send_alert_to_websocket(alert)
            await asyncio.sleep(2)  # Delay between alerts
        
        logger.info(f"✅ Sent {len(all_alerts)} smart alerts")
        return all_alerts
    
    async def start_monitoring(self, check_interval: int = 300):
        """Start continuous monitoring"""
        logger.info(f"🚀 Starting Smart Alerts monitoring (every {check_interval}s)")
        
        while True:
            try:
                await self.run_alert_checks()
                await asyncio.sleep(check_interval)
            except Exception as e:
                logger.error(f"❌ Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retry

# Test the smart alerts system
async def test_smart_alerts():
    """Test the smart alerts system"""
    print("🧪 Testing Morvo Smart Alerts v2.0...")
    
    alerts_system = MorvoSmartAlertsV2()
    
    # Run one-time alert check
    alerts = await alerts_system.run_alert_checks()
    
    print(f"✅ Generated {len(alerts)} smart alerts")
    for alert in alerts:
        print(f"   🔔 {alert.priority.value.upper()}: {alert.title}")
    
    print("🎉 Smart Alerts test completed!")

if __name__ == "__main__":
    asyncio.run(test_smart_alerts())
