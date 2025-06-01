"""
Agent Memory Manager using Model Context Protocol (MCP)
Provides persistent memory for AI marketing agents without Redis dependency
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import Depends, HTTPException
import httpx

from mcp_integration import MCPIntegration

logger = logging.getLogger(__name__)

class AgentMemoryManager:
    """
    Manages agent memories using MCP integration with Supabase
    Eliminates the need for Redis while providing persistent storage
    """
    
    def __init__(self):
        """Initialize the memory manager with environment variables"""
        self.mcp = MCPIntegration()
        self.enabled = os.getenv("MCP_ENABLED", "true").lower() == "true"
        self.memory_table = os.getenv("MCP_MEMORY_TABLE", "agent_memories")
        self.context_table = os.getenv("MCP_CONTEXT_TABLE", "cross_agent_context")
        self.max_memories = int(os.getenv("MCP_MAX_MEMORIES_PER_AGENT", "50"))
    
    async def store_memory(self, agent_id: str, company_id: str, memory_data: Dict[str, Any]) -> Dict[str, Any]:
        """Store agent memory in Supabase via MCP"""
        if not self.enabled:
            logger.info("MCP memory management disabled")
            return {"status": "disabled", "message": "Memory management disabled"}
        
        try:
            # Add metadata
            enriched_memory = {
                **memory_data,
                "agent_id": agent_id,
                "company_id": company_id,
                "timestamp": datetime.now().isoformat(),
            }
            
            # Store memory via MCP integration
            result = await self.mcp.store_agent_context(
                agent_id=agent_id,
                context_data=enriched_memory
            )
            
            # Trim old memories if needed
            await self.trim_old_memories(agent_id, company_id)
            
            return result
        except Exception as e:
            logger.error(f"Failed to store agent memory: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def get_memories(self, agent_id: str, company_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve agent memories from Supabase via MCP"""
        if not self.enabled:
            logger.info("MCP memory management disabled")
            return []
        
        try:
            # Get memories via MCP integration
            context_data = await self.mcp.get_agent_context(
                agent_id=agent_id,
                filter_params={"company_id": company_id},
                limit=limit
            )
            
            if not context_data:
                return []
                
            return context_data.get("contexts", [])
        except Exception as e:
            logger.error(f"Failed to retrieve agent memories: {str(e)}")
            return []
    
    async def share_context(self, from_agent_id: str, to_agent_id: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Share context between agents"""
        if not self.enabled:
            logger.info("MCP memory management disabled")
            return {"status": "disabled", "message": "Memory management disabled"}
        
        try:
            # Add metadata for cross-agent context
            enriched_context = {
                **context_data,
                "from_agent_id": from_agent_id,
                "to_agent_id": to_agent_id,
                "timestamp": datetime.now().isoformat(),
            }
            
            # Store shared context via MCP
            result = await self.mcp.share_agent_context(
                from_agent_id=from_agent_id,
                to_agent_id=to_agent_id,
                context_data=enriched_context
            )
            
            return result
        except Exception as e:
            logger.error(f"Failed to share agent context: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def get_shared_context(self, agent_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get context shared with an agent"""
        if not self.enabled:
            logger.info("MCP memory management disabled")
            return []
        
        try:
            # Get shared context via MCP
            shared_data = await self.mcp.get_shared_context(
                agent_id=agent_id,
                limit=limit
            )
            
            if not shared_data:
                return []
                
            return shared_data.get("contexts", [])
        except Exception as e:
            logger.error(f"Failed to retrieve shared context: {str(e)}")
            return []
    
    async def trim_old_memories(self, agent_id: str, company_id: str) -> None:
        """Ensure we don't exceed maximum memories per agent"""
        try:
            # Get current memory count
            current_memories = await self.get_memories(agent_id, company_id, limit=1000)
            
            # If we're under the limit, no need to trim
            if len(current_memories) <= self.max_memories:
                return
                
            # Sort by timestamp (oldest first)
            sorted_memories = sorted(
                current_memories, 
                key=lambda x: x.get("timestamp", "")
            )
            
            # Calculate how many to delete
            to_delete = len(sorted_memories) - self.max_memories
            
            # Delete oldest memories
            for i in range(to_delete):
                if i < len(sorted_memories):
                    memory_id = sorted_memories[i].get("id")
                    if memory_id:
                        await self.mcp.delete_memory(memory_id=memory_id)
        except Exception as e:
            logger.error(f"Failed to trim old memories: {str(e)}")
