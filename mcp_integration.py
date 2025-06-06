"""
MCP Integration Module for Morvo AI Marketing Platform
Enhances agent context, enables persistent memory, and facilitates cross-agent communication
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)

class MCPIntegration:
    """
    Model Context Protocol integration for Morvo AI Marketing Agents
    Enhances communication between agents and external systems
    """
    
    def __init__(self):
        """Initialize MCP client with Railway environment variables"""
        self.mcp_enabled = os.getenv("USE_MCP", "false").lower() == "true"
        self.mcp_endpoint = os.getenv("MCP_ENDPOINT", "https://api.mcp.morvo.ai")
        self.api_key = os.getenv("MCP_API_KEY", "")
        self.project_id = os.getenv("RAILWAY_PROJECT_ID", "morvo-marketing")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    async def store_agent_context(self, agent_id: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store agent context in MCP for persistence between sessions"""
        if not self.mcp_enabled:
            logger.info("MCP integration disabled. Context stored locally only.")
            return {"status": "disabled", "message": "MCP integration disabled"}
            
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "agent_id": agent_id,
                    "project_id": self.project_id,
                    "timestamp": datetime.now().isoformat(),
                    "context": context_data,
                    "tags": context_data.get("tags", [])
                }
                
                response = await client.post(
                    f"{self.mcp_endpoint}/context",
                    json=payload,
                    headers=self.headers
                )
                
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to store context in MCP: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    async def retrieve_agent_context(self, agent_id: str, context_type: Optional[str] = None) -> Dict[str, Any]:
        """Retrieve agent context from MCP"""
        if not self.mcp_enabled:
            logger.info("MCP integration disabled. Using local context only.")
            return {"status": "disabled", "message": "MCP integration disabled"}
            
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.mcp_endpoint}/context/{agent_id}"
                if context_type:
                    url += f"?type={context_type}"
                    
                response = await client.get(
                    url,
                    headers=self.headers
                )
                
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to retrieve context from MCP: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    async def share_context_between_agents(self, from_agent_id: str, to_agent_id: str, 
                                         context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Share context between different agents for multi-agent coordination"""
        if not self.mcp_enabled:
            logger.info("MCP integration disabled. Context shared locally only.")
            return {"status": "disabled", "message": "MCP integration disabled"}
            
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "from_agent": from_agent_id,
                    "to_agent": to_agent_id,
                    "project_id": self.project_id,
                    "timestamp": datetime.now().isoformat(),
                    "context": context_data
                }
                
                response = await client.post(
                    f"{self.mcp_endpoint}/context/share",
                    json=payload,
                    headers=self.headers
                )
                
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to share context between agents: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def store_memory(self, agent_id: str, memory_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store agent memory in MCP for long-term persistence"""
        if not self.mcp_enabled:
            logger.info("MCP integration disabled. Memory stored locally only.")
            return {"status": "disabled", "message": "MCP integration disabled"}
            
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "agent_id": agent_id,
                    "project_id": self.project_id,
                    "timestamp": datetime.now().isoformat(),
                    "memory": memory_data,
                    "tags": memory_data.get("tags", [])
                }
                
                response = await client.post(
                    f"{self.mcp_endpoint}/memory",
                    json=payload,
                    headers=self.headers
                )
                
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to store memory in MCP: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    async def retrieve_memories(self, agent_id: str, tags: Optional[List[str]] = None, 
                              limit: int = 20) -> Dict[str, Any]:
        """Retrieve agent memories from MCP based on tags"""
        if not self.mcp_enabled:
            logger.info("MCP integration disabled. Using local memories only.")
            return {"status": "disabled", "message": "MCP integration disabled"}
            
        try:
            async with httpx.AsyncClient() as client:
                url = f"{self.mcp_endpoint}/memory/{agent_id}?limit={limit}"
                if tags:
                    url += f"&tags={','.join(tags)}"
                    
                response = await client.get(
                    url,
                    headers=self.headers
                )
                
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to retrieve memories from MCP: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def query_structured_knowledge(self, query: str, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Query MCP for structured knowledge related to query"""
        if not self.mcp_enabled:
            logger.info("MCP integration disabled. Using local knowledge only.")
            return {"status": "disabled", "message": "MCP integration disabled"}
            
        try:
            payload = {
                "query": query,
                "project_id": self.project_id
            }
            
            if agent_id:
                payload["agent_id"] = agent_id
                
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.mcp_endpoint}/knowledge/query",
                    json=payload,
                    headers=self.headers
                )
                
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Failed to query MCP knowledge: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    def get_visualization_config(self, agent_id: str) -> Dict[str, Any]:
        """Get visualization configuration for the React frontend based on agent type"""
        # Base configuration for all visualizations
        base_config = {
            "theme": {
                "colors": {
                    "primary": "#0062FF",
                    "secondary": "#6B7280",
                    "success": "#10B981",
                    "warning": "#F59E0B",
                    "danger": "#EF4444",
                    "background": "#F9FAFB"
                },
                "fonts": {
                    "title": "Poppins",
                    "body": "Inter"
                }
            },
            "responsiveBreakpoints": {
                "sm": "640px",
                "md": "768px",
                "lg": "1024px",
                "xl": "1280px"
            }
        }
        
        # Agent-specific visualization configurations
        if agent_id == "M1":
            return {
                **base_config,
                "charts": [
                    {
                        "id": "strategic-health-scorecard",
                        "type": "heatmap",
                        "title": "Strategic Health Scorecard",
                        "dataKey": "kpi_framework",
                        "dimensions": {"width": "100%", "height": "300px"}
                    },
                    {
                        "id": "kpi-performance-gauges",
                        "type": "gauge",
                        "title": "KPI Performance Gauges",
                        "dataKey": "kpi_performance",
                        "dimensions": {"width": "100%", "height": "250px"}
                    },
                    {
                        "id": "roi-comparison",
                        "type": "horizontal-bar",
                        "title": "ROI Comparison by Channel",
                        "dataKey": "roi_data",
                        "dimensions": {"width": "100%", "height": "350px"}
                    },
                    {
                        "id": "opportunity-matrix",
                        "type": "bubble",
                        "title": "Opportunity Matrix",
                        "dataKey": "opportunities",
                        "dimensions": {"width": "100%", "height": "400px"}
                    },
                    {
                        "id": "revenue-forecast",
                        "type": "line-confidence",
                        "title": "Revenue Forecast",
                        "dataKey": "revenue_forecast",
                        "dimensions": {"width": "100%", "height": "300px"}
                    },
                    {
                        "id": "sales-funnel",
                        "type": "funnel",
                        "title": "Sales Funnel",
                        "dataKey": "sales_funnel",
                        "dimensions": {"width": "100%", "height": "400px"}
                    }
                ]
            }
        elif agent_id == "M2":
            return {
                **base_config,
                "charts": [
                    {
                        "id": "sentiment-gauge",
                        "type": "gauge",
                        "title": "Sentiment Gauge",
                        "dataKey": "sentiment_analysis.overall",
                        "dimensions": {"width": "100%", "height": "250px"}
                    },
                    {
                        "id": "engagement-heatmap",
                        "type": "calendar-heatmap",
                        "title": "Engagement Heat Map",
                        "dataKey": "engagement_metrics.daily",
                        "dimensions": {"width": "100%", "height": "300px"}
                    },
                    {
                        "id": "audience-demographics",
                        "type": "donut",
                        "title": "Audience Demographics",
                        "dataKey": "audience_insights.demographics",
                        "dimensions": {"width": "100%", "height": "300px"}
                    },
                    {
                        "id": "competitor-radar",
                        "type": "radar",
                        "title": "Competitor Social Performance",
                        "dataKey": "competitive_analysis",
                        "dimensions": {"width": "100%", "height": "350px"}
                    },
                    {
                        "id": "content-performance",
                        "type": "scatter",
                        "title": "Content Performance",
                        "dataKey": "content_performance",
                        "dimensions": {"width": "100%", "height": "350px"}
                    },
                    {
                        "id": "crisis-alert-panel",
                        "type": "status-indicators",
                        "title": "Crisis Alert Panel",
                        "dataKey": "crisis_alerts",
                        "dimensions": {"width": "100%", "height": "200px"}
                    },
                    {
                        "id": "share-of-voice",
                        "type": "stacked-area",
                        "title": "Share of Voice",
                        "dataKey": "share_of_voice",
                        "dimensions": {"width": "100%", "height": "300px"}
                    }
                ]
            }
        elif agent_id == "M3":
            return {
                **base_config,
                "charts": [
                    {
                        "id": "campaign-scorecard",
                        "type": "kpi-cards",
                        "title": "Campaign Scorecard",
                        "dataKey": "campaign_performance.summary",
                        "dimensions": {"width": "100%", "height": "200px"}
                    },
                    {
                        "id": "budget-sankey",
                        "type": "sankey",
                        "title": "Budget Allocation",
                        "dataKey": "budget_recommendations.flow",
                        "dimensions": {"width": "100%", "height": "400px"}
                    },
                    {
                        "id": "channel-performance",
                        "type": "grouped-bar",
                        "title": "Channel Performance",
                        "dataKey": "campaign_performance.channels",
                        "dimensions": {"width": "100%", "height": "350px"}
                    },
                    {
                        "id": "conversion-funnel",
                        "type": "funnel",
                        "title": "Conversion Funnel",
                        "dataKey": "conversion_funnel",
                        "dimensions": {"width": "100%", "height": "400px"}
                    },
                    {
                        "id": "roi-heatmap",
                        "type": "heatmap",
                        "title": "ROI Heat Map",
                        "dataKey": "roi_analysis",
                        "dimensions": {"width": "100%", "height": "350px"}
                    },
                    {
                        "id": "campaign-timeline",
                        "type": "gantt",
                        "title": "Campaign Timeline",
                        "dataKey": "campaign_plan.timeline",
                        "dimensions": {"width": "100%", "height": "350px"}
                    },
                    {
                        "id": "ab-test-results",
                        "type": "side-by-side",
                        "title": "A/B Test Results",
                        "dataKey": "ab_test_results",
                        "dimensions": {"width": "100%", "height": "300px"}
                    }
                ]
            }
        elif agent_id == "M4":
            return {
                **base_config,
                "charts": [
                    {
                        "id": "content-performance-heatmap",
                        "type": "heatmap",
                        "title": "Content Performance Heat Map",
                        "dataKey": "content_audit.performance",
                        "dimensions": {"width": "100%", "height": "350px"}
                    },
                    {
                        "id": "keyword-bubble",
                        "type": "bubble",
                        "title": "Keyword Opportunity",
                        "dataKey": "keyword_opportunities",
                        "dimensions": {"width": "100%", "height": "400px"}
                    },
                    {
                        "id": "content-gap-treemap",
                        "type": "treemap",
                        "title": "Content Gap Analysis",
                        "dataKey": "content_audit.gaps",
                        "dimensions": {"width": "100%", "height": "350px"}
                    },
                    {
                        "id": "editorial-calendar",
                        "type": "timeline",
                        "title": "Editorial Calendar",
                        "dataKey": "content_calendar",
                        "dimensions": {"width": "100%", "height": "400px"}
                    },
                    {
                        "id": "content-roi",
                        "type": "stacked-bar",
                        "title": "Content ROI by Type",
                        "dataKey": "roi_analysis",
                        "dimensions": {"width": "100%", "height": "350px"}
                    },
                    {
                        "id": "topic-cluster",
                        "type": "network",
                        "title": "Topic Cluster Network",
                        "dataKey": "topic_clusters",
                        "dimensions": {"width": "100%", "height": "400px"}
                    },
                    {
                        "id": "production-pipeline",
                        "type": "kanban",
                        "title": "Production Pipeline",
                        "dataKey": "production_pipeline",
                        "dimensions": {"width": "100%", "height": "350px"}
                    }
                ]
            }
        elif agent_id == "M5":
            return {
                **base_config,
                "charts": [
                    {
                        "id": "executive-kpi-dashboard",
                        "type": "metric-cards",
                        "title": "Executive KPI Dashboard",
                        "dataKey": "performance_dashboard.kpis",
                        "dimensions": {"width": "100%", "height": "250px"}
                    },
                    {
                        "id": "attribution-sankey",
                        "type": "sankey",
                        "title": "Multi-Channel Attribution",
                        "dataKey": "attribution_insights.flow",
                        "dimensions": {"width": "100%", "height": "400px"}
                    },
                    {
                        "id": "performance-trends",
                        "type": "multi-line",
                        "title": "Performance Trends",
                        "dataKey": "performance_dashboard.trends",
                        "dimensions": {"width": "100%", "height": "350px"}
                    },
                    {
                        "id": "customer-journey",
                        "type": "path-analysis",
                        "title": "Customer Journey",
                        "dataKey": "attribution_insights.paths",
                        "dimensions": {"width": "100%", "height": "400px"}
                    },
                    {
                        "id": "predictive-forecast",
                        "type": "area-confidence",
                        "title": "Predictive Forecast",
                        "dataKey": "predictive_forecasts",
                        "dimensions": {"width": "100%", "height": "350px"}
                    },
                    {
                        "id": "segment-comparison",
                        "type": "grouped-bar",
                        "title": "Segment Comparison",
                        "dataKey": "segment_analysis.comparison",
                        "dimensions": {"width": "100%", "height": "350px"}
                    },
                    {
                        "id": "cohort-analysis",
                        "type": "heatmap",
                        "title": "Cohort Analysis",
                        "dataKey": "segment_analysis.cohorts",
                        "dimensions": {"width": "100%", "height": "400px"}
                    }
                ]
            }
        else:
            # Default configuration
            return base_config
