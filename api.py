"""
FastAPI backend for CrewAI agents
Designed for Railway deployment
"""
import os
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, Depends, Security, status
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import json
from dotenv import load_dotenv

# Import our CrewAI components
from agents.agent_factory import AgentFactory
from tasks.task_factory import TaskFactory
from crews.crew_factory import CrewFactory

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="CrewAI Agent API",
    description="API for CrewAI-based AI agents",
    version="1.0.0"
)

# Setup CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Specify your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Key security
API_KEY = os.getenv("API_KEY", "default-development-key")
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )
    return api_key

# Request and Response models
class CrewRequest(BaseModel):
    crew_type: str
    inputs: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None

class CrewResponse(BaseModel):
    result: str
    metadata: Optional[Dict[str, Any]] = None

# Health check endpoint
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "version": "1.0.0"}

# Main endpoint to run a crew
@app.post("/crew", response_model=CrewResponse, tags=["Crews"])
def run_crew(request: CrewRequest, api_key: str = Depends(verify_api_key)):
    try:
        # Initialize crew factory
        crew_factory = CrewFactory()
        
        # Get the appropriate crew based on request type
        crew = crew_factory.get_crew(request.crew_type)
        
        # Run the crew with the provided inputs
        result = crew.kickoff(inputs=request.inputs)
        
        # Return the result
        return CrewResponse(
            result=result,
            metadata=request.metadata
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error running crew: {str(e)}"
        )

# Run the server directly if executed as script
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=True)
