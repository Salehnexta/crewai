"""
Supabase Integration for SEMrush Data

This module handles syncing mock/real SEMrush data to the Supabase semrush_data table
and retrieving it for use by the M1-M5 marketing agents.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import httpx
from mock_semrush_api import get_mock_semrush_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("semrush_supabase")

class SEMrushSupabaseManager:
    """Manager for SEMrush data in Supabase."""
    
    def __init__(
        self, 
        supabase_url: Optional[str] = None, 
        supabase_key: Optional[str] = None,
        use_mock: Optional[bool] = None
    ):
        """Initialize the SEMrush Supabase manager."""
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_KEY")
        
        # Determine if we should use mock data
        self.use_mock = use_mock if use_mock is not None else (
            os.getenv("USE_MOCK_SEMRUSH", "true").lower() == "true"
        )
        
        if not self.supabase_url or not self.supabase_key:
            logger.warning("Supabase credentials not found, only mock storage will be available")
        
        # Initialize the mock client
        self.mock_client = get_mock_semrush_client()
        
        logger.info(f"Initialized SEMrush Supabase Manager (use_mock={self.use_mock})")
    
    async def store_domain_overview(self, domain: str, data: Optional[Dict] = None) -> Dict:
        """
        Store domain overview data in Supabase.
        
        Args:
            domain: The domain to store data for
            data: Optional pre-fetched data (if None, mock data will be generated)
        
        Returns:
            The stored data record
        """
        # If data not provided, generate from mock client
        if data is None:
            data = self.mock_client.get_domain_overview(domain)["data"]
        
        # Prepare record for Supabase
        record = {
            "domain": domain,
            "data_type": "domain_overview",
            "data": data,
            "source": "mock" if self.use_mock else "semrush_api",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # If we have Supabase credentials, store in DB
        if self.supabase_url and self.supabase_key:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.supabase_url}/rest/v1/semrush_data",
                        headers={
                            "apikey": self.supabase_key,
                            "Authorization": f"Bearer {self.supabase_key}",
                            "Content-Type": "application/json",
                            "Prefer": "return=representation"
                        },
                        json=record
                    )
                    response.raise_for_status()
                    logger.info(f"Stored domain overview data for {domain} in Supabase")
                    return response.json()
            except Exception as e:
                logger.error(f"Error storing domain data in Supabase: {e}")
        
        logger.info(f"Generated mock domain overview for {domain} (not stored in Supabase)")
        return record
    
    async def store_keyword_overview(self, keyword: str, data: Optional[Dict] = None) -> Dict:
        """
        Store keyword overview data in Supabase.
        
        Args:
            keyword: The keyword to store data for
            data: Optional pre-fetched data (if None, mock data will be generated)
        
        Returns:
            The stored data record
        """
        # If data not provided, generate from mock client
        if data is None:
            data = self.mock_client.get_keyword_overview(keyword)["data"]
        
        # Prepare record for Supabase
        record = {
            "keyword": keyword,
            "data_type": "keyword_overview",
            "data": data,
            "source": "mock" if self.use_mock else "semrush_api",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # If we have Supabase credentials, store in DB
        if self.supabase_url and self.supabase_key:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.supabase_url}/rest/v1/semrush_data",
                        headers={
                            "apikey": self.supabase_key,
                            "Authorization": f"Bearer {self.supabase_key}",
                            "Content-Type": "application/json",
                            "Prefer": "return=representation"
                        },
                        json=record
                    )
                    response.raise_for_status()
                    logger.info(f"Stored keyword overview data for '{keyword}' in Supabase")
                    return response.json()
            except Exception as e:
                logger.error(f"Error storing keyword data in Supabase: {e}")
        
        logger.info(f"Generated mock keyword overview for '{keyword}' (not stored in Supabase)")
        return record
    
    async def get_domain_data(self, domain: str, refresh: bool = False) -> Dict:
        """
        Get domain data from Supabase or generate if not available.
        
        Args:
            domain: The domain to get data for
            refresh: Whether to refresh data even if it exists
            
        Returns:
            Domain data
        """
        # Check if we have supabase credentials
        if self.supabase_url and self.supabase_key and not refresh:
            try:
                # Try to get from Supabase first
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.supabase_url}/rest/v1/semrush_data",
                        headers={
                            "apikey": self.supabase_key,
                            "Authorization": f"Bearer {self.supabase_key}"
                        },
                        params={
                            "domain": f"eq.{domain}",
                            "data_type": "eq.domain_overview",
                            "order": "updated_at.desc",
                            "limit": 1
                        }
                    )
                    response.raise_for_status()
                    results = response.json()
                    
                    if results and len(results) > 0:
                        logger.info(f"Retrieved domain data for {domain} from Supabase")
                        return results[0]["data"]
            except Exception as e:
                logger.error(f"Error retrieving domain data from Supabase: {e}")
        
        # If we got here, we need to generate new data
        data = self.mock_client.get_domain_overview(domain)["data"]
        
        # Store for future use if we have Supabase access
        if self.supabase_url and self.supabase_key:
            await self.store_domain_overview(domain, data)
        
        return data
    
    async def get_keyword_data(self, keyword: str, refresh: bool = False) -> Dict:
        """
        Get keyword data from Supabase or generate if not available.
        
        Args:
            keyword: The keyword to get data for
            refresh: Whether to refresh data even if it exists
            
        Returns:
            Keyword data
        """
        # Check if we have supabase credentials
        if self.supabase_url and self.supabase_key and not refresh:
            try:
                # Try to get from Supabase first
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.supabase_url}/rest/v1/semrush_data",
                        headers={
                            "apikey": self.supabase_key,
                            "Authorization": f"Bearer {self.supabase_key}"
                        },
                        params={
                            "keyword": f"eq.{keyword}",
                            "data_type": "eq.keyword_overview",
                            "order": "updated_at.desc",
                            "limit": 1
                        }
                    )
                    response.raise_for_status()
                    results = response.json()
                    
                    if results and len(results) > 0:
                        logger.info(f"Retrieved keyword data for '{keyword}' from Supabase")
                        return results[0]["data"]
            except Exception as e:
                logger.error(f"Error retrieving keyword data from Supabase: {e}")
        
        # If we got here, we need to generate new data
        data = self.mock_client.get_keyword_overview(keyword)["data"]
        
        # Store for future use if we have Supabase access
        if self.supabase_url and self.supabase_key:
            await self.store_keyword_overview(keyword, data)
        
        return data
    
    async def seed_sample_data(self) -> None:
        """Seed the Supabase database with sample SEMrush data for development."""
        # Load all sample data
        base_path = os.path.dirname(os.path.abspath(__file__))
        samples_path = os.path.join(base_path, "data", "semrush_samples.json")
        
        try:
            with open(samples_path, 'r') as f:
                samples = json.load(f)
                
                # Seed domain overviews
                for domain, data in samples.get("domain_overview", {}).items():
                    await self.store_domain_overview(domain, data)
                
                # Seed keyword overviews
                for keyword, data in samples.get("keyword_overview", {}).items():
                    await self.store_keyword_overview(keyword, data)
                
                # Add other data types as needed
                
                logger.info("Successfully seeded sample SEMrush data in Supabase")
        except Exception as e:
            logger.error(f"Error seeding sample data: {e}")

# Helper function to get manager instance
def get_semrush_supabase_manager() -> SEMrushSupabaseManager:
    """Get a configured SEMrush Supabase manager."""
    return SEMrushSupabaseManager(
        supabase_url=os.getenv("SUPABASE_URL"),
        supabase_key=os.getenv("SUPABASE_KEY"),
        use_mock=os.getenv("USE_MOCK_SEMRUSH", "true").lower() == "true"
    )

if __name__ == "__main__":
    # Simple test code to verify the integration
    import asyncio
    
    async def test_integration():
        manager = get_semrush_supabase_manager()
        
        # Seed sample data if Supabase credentials are available
        if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"):
            await manager.seed_sample_data()
        
        # Test retrieving data
        domain_data = await manager.get_domain_data("example.com")
        print(json.dumps(domain_data, indent=2))
        
        keyword_data = await manager.get_keyword_data("digital marketing")
        print(json.dumps(keyword_data, indent=2))
    
    asyncio.run(test_integration())
