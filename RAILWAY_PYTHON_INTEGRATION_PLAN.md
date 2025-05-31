# Railway Python Backend Integration Plan
## For Existing React Dashboard + Supabase Authentication

## 🏗️ **Architecture Overview**

```
┌─────────────────────┐    API Calls    ┌─────────────────────┐
│   React Dashboard   │ ◄────────────► │   Railway Python    │
│   (Lovable + Auth)  │                 │   (M1-M5 Agents)    │
└─────────────────────┘                 └─────────────────────┘
           │                                       │
           │ Auth & Data                          │ Results
           ▼                                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    Supabase Backend                         │
│  ├── User Authentication                                    │
│  ├── Agent Results Storage                                  │
│  ├── Campaign Data                                          │
│  └── External API Data (SEMrush, etc.)                     │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 **Railway Python Backend Setup**

### 1. **FastAPI Service Architecture**
```python
# morvo_integration_api.py - Main Railway Service
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
import os

app = FastAPI(title="Morvo AI Agents Backend")

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-react-app.lovable.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase client
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")  # Use service key for backend
)
```

### 2. **Agent-to-Data Connection Flow**
```python
# agents/base_agent.py
class BaseAgent:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_SERVICE_KEY")
        )
    
    async def save_results(self, task_type: str, input_data: dict, output_data: dict):
        """Save agent results to Supabase"""
        result = self.supabase.table("agent_results").insert({
            "agent_id": self.agent_id,
            "task_type": task_type,
            "input_data": input_data,
            "output_data": output_data,
            "status": "completed",
            "created_at": datetime.now().isoformat()
        }).execute()
        return result.data[0]["id"]
    
    async def get_historical_data(self, limit: int = 100):
        """Get historical agent data for analysis"""
        return self.supabase.table("agent_results")\
            .select("*")\
            .eq("agent_id", self.agent_id)\
            .order("created_at", desc=True)\
            .limit(limit)\
            .execute()
```

## 📊 **SEMrush Integration with Supabase Example**

### 1. **SEMrush Data Fetcher**
```python
# integrations/semrush_integration.py
import requests
import asyncio
from datetime import datetime

class SEMrushIntegration:
    def __init__(self, api_key: str, supabase_client):
        self.api_key = api_key
        self.base_url = "https://api.semrush.com"
        self.supabase = supabase_client
    
    async def get_domain_overview(self, domain: str, database: str = "us"):
        """Get domain overview data from SEMrush"""
        url = f"{self.base_url}/analytics/v1/?"
        params = {
            "type": "domain_overview",
            "key": self.api_key,
            "display_limit": 10,
            "export_format": "json",
            "domain": domain,
            "database": database
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            
            # Save to Supabase
            await self.save_semrush_data("domain_overview", domain, data)
            return data
        else:
            raise Exception(f"SEMrush API error: {response.status_code}")
    
    async def get_keyword_difficulty(self, keywords: list, database: str = "us"):
        """Get keyword difficulty data"""
        url = f"{self.base_url}/analytics/v1/?"
        params = {
            "type": "phrase_kdi",
            "key": self.api_key,
            "phrase": ";".join(keywords),
            "database": database,
            "export_format": "json"
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            await self.save_semrush_data("keyword_difficulty", keywords, data)
            return data
    
    async def save_semrush_data(self, data_type: str, query: str, data: dict):
        """Save SEMrush data to Supabase"""
        result = self.supabase.table("semrush_data").insert({
            "data_type": data_type,
            "query": str(query),
            "response_data": data,
            "fetched_at": datetime.now().isoformat()
        }).execute()
        return result.data[0]["id"]
```

### 2. **Supabase SEMrush Tables**
```sql
-- Create SEMrush data table
CREATE TABLE semrush_data (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    data_type VARCHAR(50) NOT NULL,
    query TEXT NOT NULL,
    response_data JSONB NOT NULL,
    fetched_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index for performance
CREATE INDEX idx_semrush_data_type ON semrush_data(data_type);
CREATE INDEX idx_semrush_fetched_at ON semrush_data(fetched_at);

-- Create agent results table
CREATE TABLE agent_results (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    agent_id VARCHAR(10) NOT NULL,
    task_type VARCHAR(100) NOT NULL,
    input_data JSONB,
    output_data JSONB,
    status VARCHAR(20) DEFAULT 'completed',
    user_id UUID REFERENCES auth.users(id),
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🔗 **React Frontend to Railway Backend Connection**

### 1. **React API Client**
```javascript
// services/morvoApi.js
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(
  process.env.REACT_APP_SUPABASE_URL,
  process.env.REACT_APP_SUPABASE_ANON_KEY
)

const RAILWAY_API_BASE = 'https://your-app.railway.app/api/v2'

class MorvoApiClient {
  async getAuthToken() {
    const { data: { session } } = await supabase.auth.getSession()
    return session?.access_token
  }

  async callAgent(agentId, taskType, inputData) {
    const token = await this.getAuthToken()
    
    const response = await fetch(`${RAILWAY_API_BASE}/agents/${agentId}/${taskType}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        'X-API-Key': process.env.REACT_APP_MORVO_API_KEY
      },
      body: JSON.stringify(inputData)
    })

    if (!response.ok) {
      throw new Error(`Agent ${agentId} error: ${response.statusText}`)
    }

    return response.json()
  }

  async getAgentResults(agentId, limit = 50) {
    const { data, error } = await supabase
      .from('agent_results')
      .select('*')
      .eq('agent_id', agentId)
      .order('created_at', { ascending: false })
      .limit(limit)

    if (error) throw error
    return data
  }

  async getSemrushData(dataType, limit = 10) {
    const { data, error } = await supabase
      .from('semrush_data')
      .select('*')
      .eq('data_type', dataType)
      .order('fetched_at', { ascending: false })
      .limit(limit)

    if (error) throw error
    return data
  }
}

export const morvoApi = new MorvoApiClient()
```

### 2. **React Component Example**
```jsx
// components/AgentDashboard.jsx
import React, { useState, useEffect } from 'react'
import { morvoApi } from '../services/morvoApi'

export default function AgentDashboard() {
  const [agentResults, setAgentResults] = useState([])
  const [loading, setLoading] = useState(false)

  const runStrategicAnalysis = async () => {
    setLoading(true)
    try {
      const result = await morvoApi.callAgent('m1', 'strategic-analysis', {
        market: 'saudi_arabia',
        budget: 50000,
        goals: ['brand_awareness', 'lead_generation']
      })
      
      // Refresh results
      const results = await morvoApi.getAgentResults('m1')
      setAgentResults(results)
    } catch (error) {
      console.error('Strategic analysis failed:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="agent-dashboard">
      <button 
        onClick={runStrategicAnalysis}
        disabled={loading}
        className="bg-blue-500 text-white px-4 py-2 rounded"
      >
        {loading ? 'Analyzing...' : 'Run M1 Strategic Analysis'}
      </button>
      
      <div className="results mt-4">
        {agentResults.map(result => (
          <div key={result.id} className="border p-4 mb-2">
            <h3>Agent {result.agent_id.toUpperCase()}</h3>
            <p>Task: {result.task_type}</p>
            <p>Status: {result.status}</p>
            <pre>{JSON.stringify(result.output_data, null, 2)}</pre>
          </div>
        ))}
      </div>
    </div>
  )
}
```

## 🤖 **MCP (Model Context Protocol) Implementation**

### 1. **MCP Server for Railway**
```python
# mcp_server.py
from typing import Dict, Any
import json

class MCPContextManager:
    def __init__(self):
        self.context_store = {}
        self.max_context_length = 8000  # tokens
    
    async def store_agent_context(self, agent_id: str, context_data: Dict[str, Any]):
        """Store agent context for cross-agent communication"""
        context_key = f"agent_{agent_id}_context"
        
        # Compress context if too large
        context_str = json.dumps(context_data)
        if len(context_str) > self.max_context_length:
            context_data = self.compress_context(context_data)
        
        self.context_store[context_key] = {
            "data": context_data,
            "timestamp": datetime.now().isoformat(),
            "agent_id": agent_id
        }
        
        # Save to Supabase for persistence
        await self.save_context_to_db(context_key, context_data)
    
    async def get_relevant_context(self, agent_id: str, task_type: str) -> Dict[str, Any]:
        """Get relevant context for agent task"""
        # Get context from other agents
        relevant_contexts = {}
        
        for key, context in self.context_store.items():
            if context["agent_id"] != agent_id:  # Don't include own context
                relevant_contexts[context["agent_id"]] = context["data"]
        
        return relevant_contexts
    
    def compress_context(self, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Compress context data to fit within token limits"""
        # Keep only essential fields
        essential_fields = ["summary", "key_insights", "recommendations", "metrics"]
        compressed = {}
        
        for field in essential_fields:
            if field in context_data:
                compressed[field] = context_data[field]
        
        return compressed

# Initialize MCP manager
mcp_manager = MCPContextManager()
```

### 2. **Agent with MCP Integration**
```python
# agents/m1_strategic_agent.py
from .base_agent import BaseAgent
from ..mcp_server import mcp_manager

class M1StrategicAgent(BaseAgent):
    def __init__(self):
        super().__init__("m1")
    
    async def strategic_analysis(self, market_data: dict) -> dict:
        # Get context from other agents
        context = await mcp_manager.get_relevant_context("m1", "strategic_analysis")
        
        # Include M5 analytics context if available
        m5_context = context.get("m5", {})
        historical_performance = m5_context.get("campaign_performance", {})
        
        # Run strategic analysis with context
        analysis_result = await self.analyze_market(market_data, historical_performance)
        
        # Store context for other agents
        await mcp_manager.store_agent_context("m1", {
            "market_opportunities": analysis_result["opportunities"],
            "recommended_budget": analysis_result["budget_allocation"],
            "target_segments": analysis_result["segments"],
            "competitive_landscape": analysis_result["competitors"]
        })
        
        # Save results to Supabase
        await self.save_results("strategic_analysis", market_data, analysis_result)
        
        return analysis_result
```

## 🚀 **Deployment Configuration**

### 1. **Railway Environment Variables**
```bash
# Core APIs
OPENAI_API_KEY=your_openai_key
SEMRUSH_API_KEY=your_semrush_key

# Supabase (Service Key for backend)
SUPABASE_URL=https://teniefzxdikestahndur.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key  # Not anon key!

# React Frontend URL
REACT_FRONTEND_URL=https://your-react-app.lovable.app

# MCP Configuration
MCP_CONTEXT_STORE=supabase
MCP_MAX_CONTEXT_LENGTH=8000
```

### 2. **Railway Service Health Check**
```python
@app.get("/health")
async def health_check():
    """Health check for Railway deployment"""
    try:
        # Test Supabase connection
        supabase.table("agent_results").select("id").limit(1).execute()
        
        # Test SEMrush API
        semrush = SEMrushIntegration(os.getenv("SEMRUSH_API_KEY"), supabase)
        
        return {
            "status": "healthy",
            "services": {
                "supabase": "connected",
                "semrush": "available",
                "mcp": "active"
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")
```

## 📈 **Data Flow Summary**

1. **User interacts with React dashboard** (Lovable + Supabase auth)
2. **React calls Railway Python API** (authenticated requests)
3. **Python agents process tasks** with MCP context sharing
4. **Agents fetch external data** (SEMrush, social APIs)
5. **Results saved to Supabase** (accessible to React dashboard)
6. **Real-time updates** via Supabase realtime subscriptions

This architecture separates concerns perfectly: React handles UI/auth, Railway handles AI processing, and Supabase handles data persistence and real-time updates! 🚀
