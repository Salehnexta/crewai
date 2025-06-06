"""
Agent Context Manager - Enhanced Data Sharing Between M1-M5 Marketing Agents
Uses MCP for advanced context sharing patterns in the Morvo AI Platform
"""

from typing import Dict, List, Any, Optional
import asyncio
import logging
import json
import os
from datetime import datetime

from mcp_integration import MCPIntegration
from agent_memory import AgentMemoryManager

# Configure logging
logger = logging.getLogger(__name__)

class AgentContextManager:
    """
    Enhanced context manager for M1-M5 marketing agents
    Implements advanced data sharing and context synchronization
    """
    
    def __init__(self):
        """Initialize the context manager with MCP integration"""
        self.mcp = MCPIntegration()
        self.memory_manager = AgentMemoryManager()
        self.context_stats = {}
        self.shared_context_keys = [
            "company_profile",
            "marketing_insights", 
            "seo_data",
            "social_analytics",
            "campaign_metrics",
            "content_performance"
        ]

    async def synchronize_context(self, 
                                company_id: str,
                                context_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synchronize context across all agents for a company
        
        Args:
            company_id: Company identifier
            context_data: Context data to synchronize
            
        Returns:
            Dict with synchronization results
        """
        results = {}
        
        # Get all active agents for this company
        agents = ["M1", "M2", "M3", "M4", "M5"]
        
        # Synchronize context data across all agents
        for agent_id in agents:
            try:
                # Store core context for this agent
                context_result = await self.memory_manager.store_memory(
                    agent_id=agent_id,
                    company_id=company_id,
                    memory_data={
                        "sync_timestamp": datetime.utcnow().isoformat(),
                        "context_type": "sync",
                        "data": self._filter_context_for_agent(agent_id, context_data)
                    }
                )
                
                results[agent_id] = context_result
                
                # Record stats
                self.context_stats[f"{company_id}_{agent_id}"] = {
                    "last_sync": datetime.utcnow().isoformat(),
                    "context_size": len(json.dumps(context_data)),
                    "sync_status": "success" if context_result.get("status") != "error" else "error"
                }
                
            except Exception as e:
                logger.error(f"Error synchronizing context for agent {agent_id}: {e}")
                results[agent_id] = {"status": "error", "message": str(e)}
                
        return {
            "status": "success",
            "message": f"Context synchronized across {len(agents)} agents",
            "results": results
        }
    
    def _filter_context_for_agent(self, agent_id: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filter context data based on agent specialization
        
        Each agent receives data relevant to its domain:
        - M1: SEO and market analysis focused
        - M2: Social media focused
        - M3: Campaign optimization focused
        - M4: Content strategy focused
        - M5: Analytics focused
        
        Args:
            agent_id: Agent identifier (M1-M5)
            context_data: Complete context data
            
        Returns:
            Filtered context data specific to agent
        """
        # Common data all agents receive
        common_keys = ["company_profile", "marketing_goals", "budget_allocation"]
        filtered_data = {k: context_data.get(k, {}) for k in common_keys if k in context_data}
        
        # Agent-specific data
        if agent_id == "M1":  # SEO Expert
            relevant_keys = ["seo_data", "keyword_rankings", "competitor_analysis", "site_performance"]
            
        elif agent_id == "M2":  # Social Media Expert
            relevant_keys = ["social_analytics", "engagement_metrics", "audience_demographics", "sentiment_analysis"]
            
        elif agent_id == "M3":  # Campaign Manager
            relevant_keys = ["campaign_metrics", "budget_allocation", "conversion_rates", "ad_performance"]
            
        elif agent_id == "M4":  # Content Strategist
            relevant_keys = ["content_performance", "content_calendar", "topic_analysis", "content_engagement"]
            
        elif agent_id == "M5":  # Data Analyst
            relevant_keys = ["analytics_data", "roi_metrics", "traffic_sources", "user_behavior"]
            
        else:
            # Unknown agent gets minimal data
            relevant_keys = []
            
        # Add agent-specific data
        for key in relevant_keys:
            if key in context_data:
                filtered_data[key] = context_data[key]
                
        return filtered_data
    
    async def get_synchronized_context(self, 
                                      company_id: str,
                                      agent_id: str,
                                      context_keys: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Get synchronized context for a specific agent
        
        Args:
            company_id: Company identifier
            agent_id: Agent identifier
            context_keys: Optional list of specific context keys to retrieve
            
        Returns:
            Dict with merged context data
        """
        # Default to all shared context keys if none specified
        if context_keys is None:
            context_keys = self.shared_context_keys
            
        # Get this agent's memories
        agent_memories = await self.memory_manager.get_memories(
            agent_id=agent_id,
            company_id=company_id,
            limit=50  # Get plenty of context
        )
        
        # Get shared contexts from other agents
        shared_contexts = await self.memory_manager.get_shared_context(
            agent_id=agent_id,
            limit=100
        )
        
        # Merge contexts with priority to most recent data
        merged_context = {}
        
        # Process shared contexts from other agents first (base layer)
        for shared in shared_contexts:
            if "data" in shared:
                for key, value in shared["data"].items():
                    if key in context_keys:
                        merged_context[key] = value
                        
        # Layer the agent's own memories on top (higher priority)
        for memory in agent_memories:
            if "data" in memory:
                for key, value in memory["data"].items():
                    if key in context_keys:
                        merged_context[key] = value
        
        return {
            "status": "success",
            "message": f"Synchronized context retrieved for agent {agent_id}",
            "data": merged_context,
            "memory_count": len(agent_memories),
            "shared_context_count": len(shared_contexts)
        }
    
    async def push_context_update(self,
                                 from_agent_id: str,
                                 to_agent_ids: List[str],
                                 company_id: str,
                                 context_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Push context updates from one agent to specific others
        
        Args:
            from_agent_id: Source agent identifier
            to_agent_ids: List of target agent identifiers
            company_id: Company identifier
            context_data: Context data to update
            
        Returns:
            Dict with update results
        """
        results = {}
        timestamp = datetime.utcnow().isoformat()
        
        for target_agent in to_agent_ids:
            # Filter data for the target agent
            filtered_data = self._filter_context_for_agent(target_agent, context_data)
            
            # Add metadata
            enhanced_data = {
                **filtered_data,
                "source_agent": from_agent_id,
                "update_timestamp": timestamp,
                "update_type": "push",
                "company_id": company_id
            }
            
            # Share to target agent
            try:
                result = await self.memory_manager.share_context(
                    from_agent_id=from_agent_id,
                    to_agent_id=target_agent,
                    context_data=enhanced_data
                )
                results[target_agent] = result
                
            except Exception as e:
                logger.error(f"Error pushing context to agent {target_agent}: {e}")
                results[target_agent] = {"status": "error", "message": str(e)}
        
        return {
            "status": "success",
            "message": f"Context pushed to {len(to_agent_ids)} agents",
            "results": results
        }
    
    async def broadcast_critical_update(self,
                                     company_id: str,
                                     update_type: str,
                                     update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Broadcast critical updates to all agents
        
        Args:
            company_id: Company identifier
            update_type: Type of update (seo, social, campaign, content, analytics)
            update_data: Update data
            
        Returns:
            Dict with broadcast results
        """
        # All active agents
        all_agents = ["M1", "M2", "M3", "M4", "M5"]
        
        # Prioritize which agents need this update most
        priority_mapping = {
            "seo": ["M1", "M4", "M5", "M3", "M2"],
            "social": ["M2", "M4", "M3", "M5", "M1"],
            "campaign": ["M3", "M2", "M5", "M4", "M1"],
            "content": ["M4", "M2", "M1", "M3", "M5"],
            "analytics": ["M5", "M3", "M1", "M4", "M2"]
        }
        
        # Get priority order or default to alphabetical
        priority_order = priority_mapping.get(update_type.lower(), all_agents)
        
        # Enhanced metadata
        broadcast_data = {
            **update_data,
            "broadcast_timestamp": datetime.utcnow().isoformat(),
            "broadcast_type": update_type,
            "priority": "critical",
            "company_id": company_id
        }
        
        # Broadcast to agents in priority order
        results = {}
        
        for agent_id in priority_order:
            # Store as memory for this agent
            filtered_data = self._filter_context_for_agent(agent_id, broadcast_data)
            
            try:
                result = await self.memory_manager.store_memory(
                    agent_id=agent_id,
                    company_id=company_id,
                    memory_data={
                        "broadcast_data": filtered_data,
                        "broadcast_timestamp": datetime.utcnow().isoformat(),
                        "broadcast_type": update_type,
                        "priority": "critical"
                    }
                )
                results[agent_id] = result
                
            except Exception as e:
                logger.error(f"Error broadcasting to agent {agent_id}: {e}")
                results[agent_id] = {"status": "error", "message": str(e)}
        
        return {
            "status": "success",
            "message": f"Critical {update_type} update broadcast to all agents",
            "priority_order": priority_order,
            "results": results
        }
