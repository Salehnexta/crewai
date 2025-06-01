"""
Memory and Context Management Routes for Morvo AI Marketing Platform
Implements FastAPI routes for agent memory using MCP instead of Redis
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Security, status
from fastapi.security import APIKeyHeader
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import os
import logging
from datetime import datetime

from agent_memory import AgentMemoryManager

# Setup logger
logger = logging.getLogger(__name__)

# Setup API key security
API_KEY_NAME = os.getenv("API_KEY_HEADER", "X-API-Key")
API_KEY = os.getenv("API_KEY", "generated_secure_api_key_here")
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Initialize router and memory manager
memory_router = APIRouter(prefix="/api/v2/memory", tags=["memory"])
memory_manager = AgentMemoryManager()

# Pydantic models
class MemoryBase(BaseModel):
    agent_id: str
    company_id: str
    content: Dict[str, Any] = Field(..., description="Memory content to store")
    
class MemoryResponse(BaseModel):
    status: str
    message: str
    data: Optional[Dict[str, Any]] = None
    
class ContextShareRequest(BaseModel):
    from_agent_id: str
    to_agent_id: str
    company_id: str
    context_data: Dict[str, Any] = Field(..., description="Context data to share")

async def verify_api_key(api_key_header: str = Security(api_key_header)):
    """Verify API key for secured endpoints"""
    if api_key_header != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key"
        )
    return api_key_header

@memory_router.post("/store", response_model=MemoryResponse)
async def store_memory(
    memory: MemoryBase,
    api_key: str = Depends(verify_api_key)
):
    """
    Store agent memory using MCP integration
    
    Used by M1-M5 agents to persist important insights between sessions
    """
    result = await memory_manager.store_memory(
        agent_id=memory.agent_id,
        company_id=memory.company_id,
        memory_data=memory.content
    )
    
    return MemoryResponse(
        status="success" if result.get("status") != "error" else "error",
        message="Memory stored successfully" if result.get("status") != "error" else result.get("message", "Unknown error"),
        data=result
    )

@memory_router.get("/retrieve/{agent_id}", response_model=MemoryResponse)
async def retrieve_memories(
    agent_id: str,
    company_id: str,
    limit: int = Query(10, ge=1, le=100),
    api_key: str = Depends(verify_api_key)
):
    """
    Retrieve agent memories from MCP integration
    
    Used by M1-M5 agents to access previous insights and context
    """
    memories = await memory_manager.get_memories(
        agent_id=agent_id,
        company_id=company_id,
        limit=limit
    )
    
    return MemoryResponse(
        status="success",
        message=f"Retrieved {len(memories)} memories for agent {agent_id}",
        data={"memories": memories}
    )

@memory_router.post("/share", response_model=MemoryResponse)
async def share_context(
    request: ContextShareRequest,
    api_key: str = Depends(verify_api_key)
):
    """
    Share context between agents
    
    Enables cross-agent communication (e.g., M1 sharing insights with M3)
    """
    result = await memory_manager.share_context(
        from_agent_id=request.from_agent_id,
        to_agent_id=request.to_agent_id,
        context_data={
            **request.context_data,
            "company_id": request.company_id,
        }
    )
    
    return MemoryResponse(
        status="success" if result.get("status") != "error" else "error",
        message="Context shared successfully" if result.get("status") != "error" else result.get("message", "Unknown error"),
        data=result
    )

@memory_router.get("/shared/{agent_id}", response_model=MemoryResponse)
async def get_shared_context(
    agent_id: str,
    limit: int = Query(10, ge=1, le=100),
    api_key: str = Depends(verify_api_key)
):
    """
    Get context shared with an agent
    
    Allows agents to access context shared by other agents
    """
    shared_contexts = await memory_manager.get_shared_context(
        agent_id=agent_id,
        limit=limit
    )
    
    return MemoryResponse(
        status="success",
        message=f"Retrieved {len(shared_contexts)} shared contexts for agent {agent_id}",
        data={"shared_contexts": shared_contexts}
    )

@memory_router.get("/health", include_in_schema=False)
async def memory_health_check():
    """Health check endpoint for the memory service"""
    return {"status": "healthy", "message": "Memory service is operational"}
