"""
External Data Integration Base Module for Morvo AI Marketing Platform
Provides abstract base classes and utilities for external data source integration
"""

from typing import Dict, List, Any, Optional, Union
import asyncio
import logging
from datetime import datetime, timedelta
import json
import os
from abc import ABC, abstractmethod
import aiohttp
from pydantic import BaseModel

# Configure logging
logger = logging.getLogger(__name__)

class DataSourceConfig(BaseModel):
    """Configuration for external data source"""
    api_key: str
    api_endpoint: str
    company_id: str
    enabled: bool = True
    refresh_interval_minutes: int = 60
    max_results_per_request: int = 100
    timeout_seconds: int = 30
    
    class Config:
        extra = "allow"  # Allow extra fields for source-specific config

class ExternalDataResult(BaseModel):
    """Model for external data result"""
    source: str
    data_type: str
    timestamp: datetime
    status: str
    data: Dict[str, Any]
    error_message: Optional[str] = None
    refresh_token: Optional[str] = None
    next_refresh: Optional[datetime] = None

class ExternalDataSource(ABC):
    """Abstract base class for external data sources"""
    
    def __init__(self, config: DataSourceConfig):
        """Initialize data source with configuration"""
        self.config = config
        self.last_refresh = {}
        self.session = None
        self.initialized = False
        
    async def initialize(self):
        """Initialize HTTP session and validate configuration"""
        if self.initialized:
            return
            
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds)
        )
        
        try:
            # Validate credentials
            await self._validate_credentials()
            self.initialized = True
            logger.info(f"{self.source_name()} initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing {self.source_name()}: {e}")
            raise
    
    async def close(self):
        """Close resources"""
        if self.session:
            await self.session.close()
            self.session = None
            
    @abstractmethod
    async def _validate_credentials(self):
        """Validate API credentials"""
        pass
        
    @abstractmethod
    def source_name(self) -> str:
        """Return the name of this data source"""
        pass
        
    @abstractmethod
    async def fetch_data(self, data_type: str, params: Dict[str, Any]) -> ExternalDataResult:
        """Fetch data from external source"""
        pass
        
    async def _make_request(self, 
                          endpoint: str, 
                          method: str = "GET", 
                          params: Optional[Dict[str, Any]] = None,
                          data: Optional[Dict[str, Any]] = None,
                          headers: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make HTTP request to external API"""
        if not self.initialized:
            await self.initialize()
            
        if not self.session:
            raise ValueError("HTTP session not initialized")
            
        full_url = f"{self.config.api_endpoint}{endpoint}"
        
        # Prepare headers
        request_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        # Add API key to headers if available
        if hasattr(self.config, "api_key") and self.config.api_key:
            request_headers["Authorization"] = f"Bearer {self.config.api_key}"
            
        # Add custom headers
        if headers:
            request_headers.update(headers)
            
        try:
            if method.upper() == "GET":
                async with self.session.get(full_url, params=params, headers=request_headers) as response:
                    response.raise_for_status()
                    return await response.json()
            elif method.upper() == "POST":
                async with self.session.post(full_url, params=params, json=data, headers=request_headers) as response:
                    response.raise_for_status()
                    return await response.json()
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
        except aiohttp.ClientResponseError as e:
            logger.error(f"API response error from {self.source_name()}: {e.status} - {e.message}")
            raise
        except aiohttp.ClientError as e:
            logger.error(f"HTTP error from {self.source_name()}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error from {self.source_name()}: {str(e)}")
            raise
            
    def _update_last_refresh(self, data_type: str):
        """Update last refresh timestamp for data type"""
        self.last_refresh[data_type] = datetime.utcnow()
        
    def should_refresh(self, data_type: str) -> bool:
        """Check if data should be refreshed based on refresh interval"""
        if data_type not in self.last_refresh:
            return True
            
        last = self.last_refresh[data_type]
        interval = timedelta(minutes=self.config.refresh_interval_minutes)
        
        return datetime.utcnow() - last > interval
        
    def _create_result(self, 
                     data_type: str, 
                     data: Dict[str, Any],
                     status: str = "success",
                     error_message: Optional[str] = None) -> ExternalDataResult:
        """Create standardized result object"""
        return ExternalDataResult(
            source=self.source_name(),
            data_type=data_type,
            timestamp=datetime.utcnow(),
            status=status,
            data=data,
            error_message=error_message,
            next_refresh=datetime.utcnow() + timedelta(minutes=self.config.refresh_interval_minutes)
        )


class ExternalDataManager:
    """Manager for external data sources"""
    
    def __init__(self):
        """Initialize the manager"""
        self.sources: Dict[str, ExternalDataSource] = {}
        self.data_cache: Dict[str, Dict[str, ExternalDataResult]] = {}
        self.refresh_tasks = {}
        
    def register_source(self, source: ExternalDataSource):
        """Register a data source"""
        source_name = source.source_name()
        self.sources[source_name] = source
        self.data_cache[source_name] = {}
        logger.info(f"Registered data source: {source_name}")
        
    async def initialize_all(self):
        """Initialize all registered data sources"""
        init_tasks = []
        
        for source_name, source in self.sources.items():
            if not source.initialized:
                init_tasks.append(source.initialize())
                
        if init_tasks:
            results = await asyncio.gather(*init_tasks, return_exceptions=True)
            
            # Check for initialization errors
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    source_name = list(self.sources.keys())[i]
                    logger.error(f"Failed to initialize {source_name}: {result}")
                    
    async def close_all(self):
        """Close all data sources"""
        close_tasks = []
        
        for source in self.sources.values():
            close_tasks.append(source.close())
            
        await asyncio.gather(*close_tasks, return_exceptions=True)
        
    async def fetch_data(self, 
                       source_name: str, 
                       data_type: str, 
                       params: Dict[str, Any],
                       force_refresh: bool = False) -> ExternalDataResult:
        """
        Fetch data from a specific source
        
        Args:
            source_name: Name of the data source
            data_type: Type of data to fetch
            params: Parameters for the data fetch
            force_refresh: Whether to force a refresh regardless of cache
            
        Returns:
            ExternalDataResult with the fetched data
        """
        if source_name not in self.sources:
            raise ValueError(f"Unknown data source: {source_name}")
            
        source = self.sources[source_name]
        cache_key = self._make_cache_key(data_type, params)
        
        # Check cache first if not forcing refresh
        if not force_refresh and cache_key in self.data_cache[source_name]:
            cached = self.data_cache[source_name][cache_key]
            
            # Check if cache is still valid
            if not source.should_refresh(data_type):
                return cached
                
        # Fetch fresh data
        try:
            result = await source.fetch_data(data_type, params)
            
            # Update cache
            self.data_cache[source_name][cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching {data_type} from {source_name}: {e}")
            
            # If we have cached data, return it with a warning
            if cache_key in self.data_cache[source_name]:
                cached = self.data_cache[source_name][cache_key]
                return ExternalDataResult(
                    source=source_name,
                    data_type=data_type,
                    timestamp=datetime.utcnow(),
                    status="error_using_cache",
                    data=cached.data,
                    error_message=f"Fetch error, using cached data: {str(e)}",
                    next_refresh=datetime.utcnow() + timedelta(minutes=5)  # Shorter interval for retry
                )
            
            # No cached data available
            return ExternalDataResult(
                source=source_name,
                data_type=data_type,
                timestamp=datetime.utcnow(),
                status="error",
                data={},
                error_message=str(e),
                next_refresh=datetime.utcnow() + timedelta(minutes=5)  # Shorter interval for retry
            )
    
    def _make_cache_key(self, data_type: str, params: Dict[str, Any]) -> str:
        """Create a cache key from data type and params"""
        # Sort params for consistent keys regardless of dict order
        param_str = json.dumps(params, sort_keys=True)
        return f"{data_type}:{param_str}"
        
    async def fetch_multiple(self, 
                           requests: List[Dict[str, Any]],
                           parallel: bool = True) -> Dict[str, ExternalDataResult]:
        """
        Fetch multiple data items, optionally in parallel
        
        Args:
            requests: List of request specs with source_name, data_type, and params
            parallel: Whether to fetch in parallel
            
        Returns:
            Dict mapping request keys to results
        """
        results = {}
        
        if parallel:
            # Create tasks for parallel execution
            tasks = {}
            for i, request in enumerate(requests):
                source_name = request.get("source_name")
                data_type = request.get("data_type")
                params = request.get("params", {})
                force_refresh = request.get("force_refresh", False)
                
                # Generate key for this request
                key = request.get("key", f"{source_name}_{data_type}_{i}")
                
                tasks[key] = self.fetch_data(source_name, data_type, params, force_refresh)
                
            # Execute all tasks in parallel
            completed_tasks = await asyncio.gather(*tasks.values(), return_exceptions=True)
            
            # Map results back to keys
            for key, result in zip(tasks.keys(), completed_tasks):
                if isinstance(result, Exception):
                    # Handle exceptions
                    source_name = next((r["source_name"] for r in requests if r.get("key") == key), "unknown")
                    data_type = next((r["data_type"] for r in requests if r.get("key") == key), "unknown")
                    
                    results[key] = ExternalDataResult(
                        source=source_name,
                        data_type=data_type,
                        timestamp=datetime.utcnow(),
                        status="error",
                        data={},
                        error_message=str(result)
                    )
                else:
                    results[key] = result
        else:
            # Sequential execution
            for i, request in enumerate(requests):
                source_name = request.get("source_name")
                data_type = request.get("data_type")
                params = request.get("params", {})
                force_refresh = request.get("force_refresh", False)
                
                # Generate key for this request
                key = request.get("key", f"{source_name}_{data_type}_{i}")
                
                try:
                    results[key] = await self.fetch_data(source_name, data_type, params, force_refresh)
                except Exception as e:
                    results[key] = ExternalDataResult(
                        source=source_name,
                        data_type=data_type,
                        timestamp=datetime.utcnow(),
                        status="error",
                        data={},
                        error_message=str(e)
                    )
                    
        return results
    
    async def start_background_refresh(self, 
                                    company_id: str,
                                    request_templates: List[Dict[str, Any]],
                                    interval_minutes: int = 60):
        """
        Start background refresh tasks for a set of data
        
        Args:
            company_id: Company identifier
            request_templates: List of request templates to refresh
            interval_minutes: Refresh interval in minutes
        """
        # Stop any existing task for this company
        await self.stop_background_refresh(company_id)
        
        # Create and start new background task
        refresh_task = asyncio.create_task(
            self._background_refresh_loop(company_id, request_templates, interval_minutes)
        )
        
        self.refresh_tasks[company_id] = refresh_task
        logger.info(f"Started background refresh for company {company_id}")
        
    async def stop_background_refresh(self, company_id: str):
        """Stop background refresh for a company"""
        if company_id in self.refresh_tasks:
            task = self.refresh_tasks[company_id]
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                    
            del self.refresh_tasks[company_id]
            logger.info(f"Stopped background refresh for company {company_id}")
            
    async def _background_refresh_loop(self, 
                                    company_id: str,
                                    request_templates: List[Dict[str, Any]],
                                    interval_minutes: int):
        """Background refresh loop for periodic data updates"""
        while True:
            try:
                # Update company_id in all request params
                requests = []
                for template in request_templates:
                    request = template.copy()
                    if "params" not in request:
                        request["params"] = {}
                    
                    request["params"]["company_id"] = company_id
                    requests.append(request)
                
                # Fetch all data
                await self.fetch_multiple(requests, parallel=True)
                
                # Wait for next refresh interval
                await asyncio.sleep(interval_minutes * 60)
                
            except asyncio.CancelledError:
                logger.info(f"Background refresh for company {company_id} cancelled")
                break
            except Exception as e:
                logger.error(f"Error in background refresh for company {company_id}: {e}")
                # Wait a shorter time before retry on error
                await asyncio.sleep(300)  # 5 minutes
