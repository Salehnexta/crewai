"""
SEMrush API Integration for Morvo AI Marketing Platform
Provides data integration with SEMrush for SEO and keyword analytics
"""

from typing import Dict, List, Any, Optional
import asyncio
import logging
from datetime import datetime, timedelta
import json
import os

from external_data_base import ExternalDataSource, ExternalDataResult, DataSourceConfig

# Configure logging
logger = logging.getLogger(__name__)

class SEMrushDataSource(ExternalDataSource):
    """
    SEMrush data source integration
    Fetches SEO and keyword data from SEMrush API
    """
    
    def source_name(self) -> str:
        """Return the name of this data source"""
        return "semrush"
        
    async def _validate_credentials(self):
        """Validate SEMrush API credentials"""
        # Make a simple API call to verify credentials
        try:
            result = await self._make_request(
                endpoint="/api/v1/auth/status",
                method="GET"
            )
            
            if not result.get("success", False):
                raise ValueError(f"Invalid SEMrush API credentials: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"SEMrush credential validation failed: {e}")
            raise ValueError(f"SEMrush API credential validation failed: {e}")
    
    async def fetch_data(self, data_type: str, params: Dict[str, Any]) -> ExternalDataResult:
        """
        Fetch data from SEMrush API
        
        Args:
            data_type: Type of data to fetch (domain_overview, keywords, competitors, etc.)
            params: Parameters for the API request
            
        Returns:
            ExternalDataResult with the fetched data
        """
        if not self.initialized:
            await self.initialize()
            
        # Make sure we have the required parameters
        company_id = params.get("company_id")
        if not company_id:
            raise ValueError("company_id is required")
            
        domain = params.get("domain")
        if not domain:
            raise ValueError("domain is required")
            
        # Update last refresh timestamp
        self._update_last_refresh(data_type)
        
        try:
            # Call the appropriate method based on data_type
            if data_type == "domain_overview":
                result = await self._fetch_domain_overview(domain, params)
            elif data_type == "keywords":
                result = await self._fetch_keywords(domain, params)
            elif data_type == "competitors":
                result = await self._fetch_competitors(domain, params)
            elif data_type == "backlinks":
                result = await self._fetch_backlinks(domain, params)
            elif data_type == "position_changes":
                result = await self._fetch_position_changes(domain, params)
            else:
                raise ValueError(f"Unsupported data type: {data_type}")
                
            return self._create_result(data_type, result)
            
        except Exception as e:
            logger.error(f"Error fetching {data_type} from SEMrush: {e}")
            return self._create_result(
                data_type=data_type,
                data={},
                status="error",
                error_message=str(e)
            )
    
    async def _fetch_domain_overview(self, domain: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch domain overview data"""
        database = params.get("database", "us")
        display_limit = params.get("limit", 10)
        display_offset = params.get("offset", 0)
        
        api_params = {
            "domain": domain,
            "database": database,
            "display_limit": display_limit,
            "display_offset": display_offset,
            "export_columns": "Dn,Rk,Or,Ot,Oc,Ad,At,Ac,Sh,Sv,Sc"
        }
        
        response = await self._make_request(
            endpoint="/api/v1/analytics/domain_overview",
            method="GET",
            params=api_params
        )
        
        # Process and transform the data for our needs
        processed_data = {
            "domain": domain,
            "database": database,
            "timestamp": datetime.utcnow().isoformat(),
            "organic": {
                "traffic": response.get("organic", {}).get("traffic", 0),
                "keywords": response.get("organic", {}).get("keywords", 0),
                "cost": response.get("organic", {}).get("cost", 0)
            },
            "paid": {
                "traffic": response.get("paid", {}).get("traffic", 0),
                "keywords": response.get("paid", {}).get("keywords", 0),
                "cost": response.get("paid", {}).get("cost", 0)
            },
            "backlinks": {
                "total": response.get("backlinks", {}).get("total", 0),
                "domains": response.get("backlinks", {}).get("domains", 0)
            },
            "rank": response.get("rank", 0),
            "main_competitors": response.get("main_competitors", [])
        }
        
        return processed_data
    
    async def _fetch_keywords(self, domain: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch domain organic keywords"""
        database = params.get("database", "us")
        display_limit = params.get("limit", 100)
        display_offset = params.get("offset", 0)
        
        api_params = {
            "domain": domain,
            "database": database,
            "display_limit": display_limit,
            "display_offset": display_offset,
            "export_columns": "Ph,Po,Nq,Cp,Co,Kd,Tr,Tg,Tc,Nr,Td"
        }
        
        response = await self._make_request(
            endpoint="/api/v1/analytics/domain_organic",
            method="GET",
            params=api_params
        )
        
        # Process keywords data
        keywords = []
        for item in response.get("items", []):
            keywords.append({
                "keyword": item.get("keyword", ""),
                "position": item.get("position", 0),
                "search_volume": item.get("search_volume", 0),
                "cpc": item.get("cpc", 0),
                "competition": item.get("competition", 0),
                "keyword_difficulty": item.get("keyword_difficulty", 0),
                "traffic": item.get("traffic", 0),
                "traffic_cost": item.get("traffic_cost", 0)
            })
        
        processed_data = {
            "domain": domain,
            "database": database,
            "timestamp": datetime.utcnow().isoformat(),
            "total_keywords": response.get("total_count", 0),
            "keywords": keywords
        }
        
        return processed_data
    
    async def _fetch_competitors(self, domain: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch domain competitors"""
        database = params.get("database", "us")
        display_limit = params.get("limit", 20)
        display_offset = params.get("offset", 0)
        
        api_params = {
            "domain": domain,
            "database": database,
            "display_limit": display_limit,
            "display_offset": display_offset,
            "export_columns": "Dn,Cr,Np,Or,Ot,Oc,Ad,At,Ac"
        }
        
        response = await self._make_request(
            endpoint="/api/v1/analytics/domain_competitors",
            method="GET",
            params=api_params
        )
        
        # Process competitors data
        competitors = []
        for item in response.get("items", []):
            competitors.append({
                "domain": item.get("domain", ""),
                "competition_level": item.get("competition_level", 0),
                "common_keywords": item.get("common_keywords", 0),
                "organic": {
                    "keywords": item.get("organic_keywords", 0),
                    "traffic": item.get("organic_traffic", 0),
                    "cost": item.get("organic_cost", 0)
                },
                "paid": {
                    "keywords": item.get("paid_keywords", 0),
                    "traffic": item.get("paid_traffic", 0),
                    "cost": item.get("paid_cost", 0)
                }
            })
        
        processed_data = {
            "domain": domain,
            "database": database,
            "timestamp": datetime.utcnow().isoformat(),
            "total_competitors": response.get("total_count", 0),
            "competitors": competitors
        }
        
        return processed_data
    
    async def _fetch_backlinks(self, domain: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch domain backlinks"""
        display_limit = params.get("limit", 50)
        display_offset = params.get("offset", 0)
        
        api_params = {
            "target": domain,
            "display_limit": display_limit,
            "display_offset": display_offset,
            "export_columns": "source_url,target_url,source_title,source_size,external_num,internal_num,source_trust_score,source_citation_flow,source_domain_score,first_seen,last_seen"
        }
        
        response = await self._make_request(
            endpoint="/api/v1/backlinks/backlinks",
            method="GET",
            params=api_params
        )
        
        # Process backlinks data
        backlinks = []
        for item in response.get("items", []):
            backlinks.append({
                "source_url": item.get("source_url", ""),
                "target_url": item.get("target_url", ""),
                "source_title": item.get("source_title", ""),
                "source_trust_score": item.get("source_trust_score", 0),
                "source_domain_score": item.get("source_domain_score", 0),
                "first_seen": item.get("first_seen", ""),
                "last_seen": item.get("last_seen", "")
            })
        
        processed_data = {
            "domain": domain,
            "timestamp": datetime.utcnow().isoformat(),
            "total_backlinks": response.get("total_count", 0),
            "backlinks": backlinks
        }
        
        return processed_data
    
    async def _fetch_position_changes(self, domain: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch position changes for a domain"""
        database = params.get("database", "us")
        date = params.get("date", datetime.utcnow().strftime("%Y%m%d"))
        display_limit = params.get("limit", 50)
        display_offset = params.get("offset", 0)
        
        api_params = {
            "domain": domain,
            "database": database,
            "date": date,
            "display_limit": display_limit,
            "display_offset": display_offset,
            "export_columns": "Ph,Po,Pp,Nq,Cp,Co,Tr,Tc,Ur"
        }
        
        response = await self._make_request(
            endpoint="/api/v1/analytics/domain_position_changes",
            method="GET",
            params=api_params
        )
        
        # Process position changes data
        position_changes = []
        for item in response.get("items", []):
            position_changes.append({
                "keyword": item.get("keyword", ""),
                "current_position": item.get("position", 0),
                "previous_position": item.get("previous_position", 0),
                "position_change": item.get("position", 0) - item.get("previous_position", 0),
                "search_volume": item.get("search_volume", 0),
                "cpc": item.get("cpc", 0),
                "competition": item.get("competition", 0),
                "traffic": item.get("traffic", 0),
                "traffic_cost": item.get("traffic_cost", 0),
                "url": item.get("url", "")
            })
        
        # Calculate some summary statistics
        improved = len([pc for pc in position_changes if pc["position_change"] < 0])
        declined = len([pc for pc in position_changes if pc["position_change"] > 0])
        new = len([pc for pc in position_changes if pc["previous_position"] == 0 and pc["current_position"] > 0])
        
        processed_data = {
            "domain": domain,
            "database": database,
            "date": date,
            "timestamp": datetime.utcnow().isoformat(),
            "total_changes": response.get("total_count", 0),
            "summary": {
                "improved": improved,
                "declined": declined,
                "new": new,
                "unchanged": len(position_changes) - improved - declined - new
            },
            "position_changes": position_changes
        }
        
        return processed_data
