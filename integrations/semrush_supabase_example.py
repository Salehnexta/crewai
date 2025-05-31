"""
SEMrush Integration with Supabase - Complete Example
For Morvo AI Marketing Platform M1-M5 Agents
"""

import asyncio
import requests
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from supabase import create_client, Client
import json

class SEMrushSupabaseIntegration:
    def __init__(self, semrush_api_key: str, supabase_url: str, supabase_key: str):
        self.api_key = semrush_api_key
        self.base_url = "https://api.semrush.com"
        self.supabase: Client = create_client(supabase_url, supabase_key)
        
        # SEMrush rate limits: 1000 requests per day
        self.daily_request_limit = 1000
        self.requests_made = 0
    
    async def get_domain_overview(self, domain: str, database: str = "us") -> Dict[str, Any]:
        """
        Get comprehensive domain overview from SEMrush
        Includes organic traffic, paid traffic, backlinks, etc.
        """
        # Check cache first
        cached_data = await self.get_cached_data(domain, "domain_overview", max_age_hours=6)
        if cached_data:
            return {
                "domain": domain,
                "overview": self._process_domain_overview(cached_data["response_data"]),
                "source": "cache",
                "fetched_at": cached_data["fetched_at"]
            }
        
        url = f"{self.base_url}/analytics/v1/"
        params = {
            "type": "domain_overview",
            "key": self.api_key,
            "domain": domain,
            "database": database,
            "export_format": "json"
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            self.requests_made += 1
            
            # Save to Supabase
            saved_id = await self._save_semrush_data(
                domain=domain,
                data_type="domain_overview",
                database_region=database,
                query_params=params,
                response_data=data
            )
            
            # Process and structure the data
            processed_data = self._process_domain_overview(data)
            
            return {
                "id": saved_id,
                "domain": domain,
                "overview": processed_data,
                "source": "api",
                "fetched_at": datetime.now().isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"SEMrush API error for domain {domain}: {str(e)}")

    async def get_keyword_difficulty(self, keywords: List[str], database: str = "us") -> Dict[str, Any]:
        """Get keyword difficulty and metrics for multiple keywords"""
        keyword_chunks = [keywords[i:i+100] for i in range(0, len(keywords), 100)]
        all_results = []
        
        for chunk in keyword_chunks:
            url = f"{self.base_url}/analytics/v1/"
            params = {
                "type": "phrase_kdi",
                "key": self.api_key,
                "phrase": ";".join(chunk),
                "database": database,
                "export_format": "json"
            }
            
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                self.requests_made += 1
                
                # Save each keyword to database
                for keyword_data in data:
                    await self._save_keyword_data(keyword_data, database)
                
                all_results.extend(data)
                await asyncio.sleep(0.1)  # Rate limiting
                
            except requests.exceptions.RequestException as e:
                print(f"Error fetching keywords {chunk}: {str(e)}")
                continue
        
        return {
            "keywords_analyzed": len(keywords),
            "results": all_results,
            "database": database,
            "fetched_at": datetime.now().isoformat()
        }

    async def _save_semrush_data(self, domain: str, data_type: str, database_region: str, 
                                query_params: Dict, response_data: Any) -> str:
        """Save SEMrush response data to Supabase"""
        try:
            result = self.supabase.table("semrush_data").insert({
                "domain": domain,
                "data_type": data_type,
                "database_region": database_region,
                "query_params": query_params,
                "response_data": response_data,
                "api_cost": 1,
                "fetched_at": datetime.now().isoformat()
            }).execute()
            
            return result.data[0]["id"]
            
        except Exception as e:
            print(f"Error saving SEMrush data to Supabase: {str(e)}")
            raise

    async def _save_keyword_data(self, keyword_data: Dict, database: str):
        """Save individual keyword data to keywords table"""
        try:
            self.supabase.table("semrush_keywords").upsert({
                "keyword": keyword_data.get("keyword", ""),
                "domain": keyword_data.get("domain", ""),
                "difficulty_score": keyword_data.get("kd", 0),
                "search_volume": keyword_data.get("vol", 0),
                "cpc": float(keyword_data.get("cpc", 0)),
                "competition": float(keyword_data.get("competition", 0)),
                "trends": keyword_data.get("trends", {}),
                "last_updated": datetime.now().isoformat()
            }, on_conflict="keyword,domain").execute()
            
        except Exception as e:
            print(f"Error saving keyword data: {str(e)}")

    def _process_domain_overview(self, raw_data: Dict) -> Dict[str, Any]:
        """Process and structure domain overview data"""
        if not raw_data:
            return {}
        
        overview = raw_data[0] if isinstance(raw_data, list) else raw_data
        
        return {
            "organic_traffic": overview.get("organic_traffic", 0),
            "organic_keywords": overview.get("organic_keywords", 0),
            "organic_cost": overview.get("organic_cost", 0),
            "paid_traffic": overview.get("paid_traffic", 0),
            "paid_keywords": overview.get("paid_keywords", 0),
            "backlinks": overview.get("backlinks", 0),
            "authority_score": overview.get("authority_score", 0)
        }

    async def get_cached_data(self, domain: str, data_type: str, 
                            max_age_hours: int = 24) -> Optional[Dict[str, Any]]:
        """Get cached SEMrush data from Supabase if fresh enough"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        try:
            result = self.supabase.table("semrush_data")\
                .select("*")\
                .eq("domain", domain)\
                .eq("data_type", data_type)\
                .gte("fetched_at", cutoff_time.isoformat())\
                .order("fetched_at", desc=True)\
                .limit(1)\
                .execute()
            
            if result.data:
                return result.data[0]
            
            return None
            
        except Exception as e:
            print(f"Error fetching cached data: {str(e)}")
            return None
