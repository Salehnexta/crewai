"""
Custom Search Tool for CrewAI agents
Implements additional capabilities beyond the standard SerperDevTool
"""
import os
import json
import requests
from typing import Any, Dict, Optional
from crewai_tools import BaseTool
from pydantic import BaseModel, Field

class CustomSearchToolSchema(BaseModel):
    query: str = Field(..., description="The search query to be executed")
    language: Optional[str] = Field(None, description="The language for the search results")
    region: Optional[str] = Field(None, description="The geographic region to target for results")

class CustomSearchTool(BaseTool):
    """
    Enhanced search tool with additional parameters for language and region
    Great for localized market research and content targeting specific audiences
    """
    name: str = "CustomSearchTool"
    description: str = "Search the web with support for language and region specificity"
    args_schema: type[BaseModel] = CustomSearchToolSchema

    def __init__(self, api_key: Optional[str] = None):
        """Initialize with optional API key"""
        super().__init__()
        self.api_key = api_key or os.getenv("SERPER_API_KEY")
        if not self.api_key:
            raise ValueError("SERPER_API_KEY must be provided or set as environment variable")

    def _run(self, query: str, language: Optional[str] = None, region: Optional[str] = None) -> str:
        """Execute the search with the specified parameters"""
        url = "https://google.serper.dev/search"
        
        payload = {
            "q": query,
            "gl": region or "us",  # Default to US if not specified
            "hl": language or "en"  # Default to English if not specified
        }
        
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            results = response.json()
            
            # Format the results
            formatted_results = self._format_results(results)
            return formatted_results
            
        except requests.exceptions.HTTPError as e:
            return f"Error: API request failed with status code {e.response.status_code}"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def _format_results(self, results: Dict[str, Any]) -> str:
        """Format the search results into a readable string"""
        formatted_output = "Search Results:\n\n"
        
        # Extract organic results
        if "organic" in results:
            for idx, result in enumerate(results["organic"][:5], 1):  # Get top 5 results
                formatted_output += f"{idx}. {result.get('title', 'No Title')}\n"
                formatted_output += f"   URL: {result.get('link', 'No Link')}\n"
                formatted_output += f"   Snippet: {result.get('snippet', 'No Snippet')}\n\n"
        
        # Extract knowledge graph if available
        if "knowledgeGraph" in results:
            kg = results["knowledgeGraph"]
            formatted_output += "Knowledge Graph:\n"
            formatted_output += f"Title: {kg.get('title', 'No Title')}\n"
            formatted_output += f"Description: {kg.get('description', 'No Description')}\n"
            formatted_output += f"URL: {kg.get('link', 'No Link')}\n\n"
        
        return formatted_output
