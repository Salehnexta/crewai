"""
External Data Integration API Routes for Morvo AI Marketing Platform
Provides FastAPI routes for external data integration and smart alerts
"""

from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, Query, BackgroundTasks
from pydantic import BaseModel
import asyncio
import logging
from datetime import datetime, timedelta
import json
import os

# Import Morvo components
from external_data_base import ExternalDataManager, DataSourceConfig, ExternalDataResult
from external_data_semrush import SEMrushDataSource
from external_data_google_analytics import GoogleAnalyticsDataSource
from external_data_brand24 import Brand24DataSource
from smart_alerts import SmartAlertSystem
from agent_context_manager import AgentContextManager

# Import security components
from fastapi.security.api_key import APIKeyHeader
from fastapi import Security
from starlette.status import HTTP_403_FORBIDDEN

# Configure logging
logger = logging.getLogger(__name__)

# API Key security
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Models for API requests and responses
class DataSourceConfigModel(BaseModel):
    """Model for data source configuration"""
    source_type: str
    api_key: str
    api_endpoint: str
    company_id: str
    refresh_interval_minutes: Optional[int] = 60
    config: Optional[Dict[str, Any]] = {}

class DataFetchRequest(BaseModel):
    """Model for data fetch request"""
    source_name: str
    data_type: str
    params: Dict[str, Any]
    force_refresh: Optional[bool] = False

class AlertConfig(BaseModel):
    """Model for alert configuration"""
    alert_types: List[str]
    company_id: str
    check_interval_minutes: Optional[int] = 60
    threshold_overrides: Optional[Dict[str, Any]] = {}

class IntegrationStatusResponse(BaseModel):
    """Model for integration status response"""
    status: str
    sources: Dict[str, bool]
    last_check: str
    message: Optional[str] = None

# Create router
data_integration_router = APIRouter(prefix="/api/v2/data", tags=["data_integration"])

# Initialize managers
data_manager = ExternalDataManager()
alert_system = SmartAlertSystem()
context_manager = AgentContextManager()

# Background tasks
refresh_tasks = {}
alert_check_tasks = {}

# API Key validation
async def get_api_key(api_key_header: str = Security(api_key_header)):
    """Validate API key"""
    if api_key_header == os.environ.get("MORVO_API_KEY"):
        return api_key_header
    raise HTTPException(
        status_code=HTTP_403_FORBIDDEN, detail="Could not validate API key"
    )

# Helper for initializing sources
async def initialize_sources():
    """Initialize all registered data sources"""
    if not data_manager.sources:
        # Register default sources if not already registered
        try:
            # Initialize SEMrush if configured
            if os.environ.get("SEMRUSH_API_KEY"):
                semrush_config = DataSourceConfig(
                    api_key=os.environ.get("SEMRUSH_API_KEY"),
                    api_endpoint="https://api.semrush.com",
                    company_id="default"
                )
                data_manager.register_source(SEMrushDataSource(semrush_config))
                
            # Initialize Google Analytics if configured
            if os.environ.get("GOOGLE_ANALYTICS_API_KEY"):
                ga_config = DataSourceConfig(
                    api_key=os.environ.get("GOOGLE_ANALYTICS_API_KEY"),
                    api_endpoint="https://analyticsdata.googleapis.com",
                    company_id="default"
                )
                data_manager.register_source(GoogleAnalyticsDataSource(ga_config))
                
            # Initialize Brand24 if configured
            if os.environ.get("BRAND24_API_KEY"):
                brand24_config = DataSourceConfig(
                    api_key=os.environ.get("BRAND24_API_KEY"),
                    api_endpoint="https://api.brand24.com",
                    company_id="default"
                )
                data_manager.register_source(Brand24DataSource(brand24_config))
                
            # Initialize all sources
            await data_manager.initialize_all()
            
        except Exception as e:
            logger.error(f"Error initializing data sources: {e}")
            raise

# Background task for alert checking
async def check_alerts_background(company_id: str, alert_types: List[str], interval_minutes: int):
    """Background task to check for alerts periodically"""
    while True:
        try:
            # Check for opportunities
            opportunities = await alert_system.check_all_opportunities(company_id)
            
            # Filter by alert types if specified
            if alert_types:
                opportunities = [o for o in opportunities if o.get("alert_type") in alert_types]
                
            # Store alerts that were found
            for opportunity in opportunities:
                await alert_system.store_alert(opportunity)
                
            # Wait for next check
            await asyncio.sleep(interval_minutes * 60)
            
        except asyncio.CancelledError:
            logger.info(f"Alert check task for company {company_id} cancelled")
            break
        except Exception as e:
            logger.error(f"Error in alert check task for company {company_id}: {e}")
            await asyncio.sleep(300)  # 5 minutes on error

# Routes
@data_integration_router.get("/status", response_model=IntegrationStatusResponse)
async def get_integration_status(api_key: str = Depends(get_api_key)):
    """Get status of all data integrations"""
    await initialize_sources()
    
    source_status = {}
    for source_name, source in data_manager.sources.items():
        source_status[source_name] = source.initialized
        
    return {
        "status": "active" if any(source_status.values()) else "inactive",
        "sources": source_status,
        "last_check": datetime.utcnow().isoformat(),
        "message": f"Found {len(source_status)} configured data sources"
    }

@data_integration_router.post("/configure")
async def configure_data_source(
    config: DataSourceConfigModel,
    api_key: str = Depends(get_api_key)
):
    """Configure a data source"""
    try:
        # Create data source config
        source_config = DataSourceConfig(
            api_key=config.api_key,
            api_endpoint=config.api_endpoint,
            company_id=config.company_id,
            refresh_interval_minutes=config.refresh_interval_minutes,
            **config.config
        )
        
        # Create and register the data source
        if config.source_type == "semrush":
            source = SEMrushDataSource(source_config)
        elif config.source_type == "google_analytics":
            source = GoogleAnalyticsDataSource(source_config)
        elif config.source_type == "brand24":
            source = Brand24DataSource(source_config)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported data source type: {config.source_type}")
            
        # Register and initialize
        data_manager.register_source(source)
        await source.initialize()
        
        return {
            "status": "success",
            "message": f"Data source {config.source_type} configured successfully",
            "source_name": source.source_name()
        }
        
    except Exception as e:
        logger.error(f"Error configuring data source: {e}")
        raise HTTPException(status_code=500, detail=f"Error configuring data source: {str(e)}")

@data_integration_router.post("/fetch")
async def fetch_data(
    request: DataFetchRequest,
    api_key: str = Depends(get_api_key)
):
    """Fetch data from a specific source"""
    await initialize_sources()
    
    try:
        result = await data_manager.fetch_data(
            source_name=request.source_name,
            data_type=request.data_type,
            params=request.params,
            force_refresh=request.force_refresh
        )
        
        return {
            "status": "success",
            "source": request.source_name,
            "data_type": request.data_type,
            "timestamp": result.timestamp.isoformat(),
            "data": result.data
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")

@data_integration_router.post("/fetch_multiple")
async def fetch_multiple_data(
    requests: List[DataFetchRequest],
    api_key: str = Depends(get_api_key)
):
    """Fetch multiple data items in parallel"""
    await initialize_sources()
    
    try:
        # Convert to format expected by fetch_multiple
        fetch_requests = []
        for i, request in enumerate(requests):
            fetch_requests.append({
                "key": f"{request.source_name}_{request.data_type}_{i}",
                "source_name": request.source_name,
                "data_type": request.data_type,
                "params": request.params,
                "force_refresh": request.force_refresh
            })
            
        results = await data_manager.fetch_multiple(fetch_requests, parallel=True)
        
        # Process results
        processed_results = {}
        for key, result in results.items():
            processed_results[key] = {
                "status": result.status,
                "source": result.source,
                "data_type": result.data_type,
                "timestamp": result.timestamp.isoformat(),
                "data": result.data,
                "error_message": result.error_message
            }
            
        return {
            "status": "success",
            "result_count": len(processed_results),
            "results": processed_results
        }
        
    except Exception as e:
        logger.error(f"Error fetching multiple data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching multiple data: {str(e)}")

@data_integration_router.post("/start_background_refresh")
async def start_background_refresh(
    company_id: str,
    request_templates: List[Dict[str, Any]],
    interval_minutes: int = 60,
    api_key: str = Depends(get_api_key)
):
    """Start background refresh for a company"""
    await initialize_sources()
    
    try:
        # Stop any existing refresh task
        if company_id in refresh_tasks:
            await data_manager.stop_background_refresh(company_id)
            
        # Start new background refresh
        await data_manager.start_background_refresh(
            company_id=company_id,
            request_templates=request_templates,
            interval_minutes=interval_minutes
        )
        
        refresh_tasks[company_id] = {
            "started_at": datetime.utcnow().isoformat(),
            "interval_minutes": interval_minutes,
            "templates": request_templates
        }
        
        return {
            "status": "success",
            "message": f"Background refresh started for company {company_id}",
            "refresh_interval": interval_minutes,
            "data_sources": [t.get("source_name") for t in request_templates]
        }
        
    except Exception as e:
        logger.error(f"Error starting background refresh: {e}")
        raise HTTPException(status_code=500, detail=f"Error starting background refresh: {str(e)}")

@data_integration_router.post("/stop_background_refresh")
async def stop_background_refresh(
    company_id: str,
    api_key: str = Depends(get_api_key)
):
    """Stop background refresh for a company"""
    if company_id in refresh_tasks:
        try:
            await data_manager.stop_background_refresh(company_id)
            del refresh_tasks[company_id]
            
            return {
                "status": "success",
                "message": f"Background refresh stopped for company {company_id}"
            }
            
        except Exception as e:
            logger.error(f"Error stopping background refresh: {e}")
            raise HTTPException(status_code=500, detail=f"Error stopping background refresh: {str(e)}")
    else:
        return {
            "status": "warning",
            "message": f"No active background refresh found for company {company_id}"
        }

@data_integration_router.post("/alerts/start_checking")
async def start_alert_checking(
    config: AlertConfig,
    background_tasks: BackgroundTasks,
    api_key: str = Depends(get_api_key)
):
    """Start background alert checking for a company"""
    try:
        # Stop any existing alert check task
        if config.company_id in alert_check_tasks:
            task = alert_check_tasks[config.company_id]["task"]
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Apply threshold overrides if any
        if config.threshold_overrides:
            for alert_type, thresholds in config.threshold_overrides.items():
                if alert_type in alert_system.alert_thresholds:
                    alert_system.alert_thresholds[alert_type].update(thresholds)
        
        # Start new background task
        task = asyncio.create_task(
            check_alerts_background(
                company_id=config.company_id,
                alert_types=config.alert_types,
                interval_minutes=config.check_interval_minutes
            )
        )
        
        alert_check_tasks[config.company_id] = {
            "task": task,
            "started_at": datetime.utcnow().isoformat(),
            "interval_minutes": config.check_interval_minutes,
            "alert_types": config.alert_types
        }
        
        return {
            "status": "success",
            "message": f"Alert checking started for company {config.company_id}",
            "check_interval": config.check_interval_minutes,
            "alert_types": config.alert_types
        }
        
    except Exception as e:
        logger.error(f"Error starting alert checking: {e}")
        raise HTTPException(status_code=500, detail=f"Error starting alert checking: {str(e)}")

@data_integration_router.post("/alerts/stop_checking")
async def stop_alert_checking(
    company_id: str,
    api_key: str = Depends(get_api_key)
):
    """Stop background alert checking for a company"""
    if company_id in alert_check_tasks:
        try:
            task = alert_check_tasks[company_id]["task"]
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                    
            del alert_check_tasks[company_id]
            
            return {
                "status": "success",
                "message": f"Alert checking stopped for company {company_id}"
            }
            
        except Exception as e:
            logger.error(f"Error stopping alert checking: {e}")
            raise HTTPException(status_code=500, detail=f"Error stopping alert checking: {str(e)}")
    else:
        return {
            "status": "warning",
            "message": f"No active alert checking found for company {company_id}"
        }

@data_integration_router.get("/alerts/active")
async def get_active_alerts(
    company_id: str,
    api_key: str = Depends(get_api_key)
):
    """Get active alerts for a company"""
    try:
        alerts = await alert_system.get_active_alerts(company_id)
        
        return {
            "status": "success",
            "company_id": company_id,
            "timestamp": datetime.utcnow().isoformat(),
            "alert_count": len(alerts),
            "alerts": alerts
        }
        
    except Exception as e:
        logger.error(f"Error getting active alerts: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting active alerts: {str(e)}")

@data_integration_router.post("/alerts/check_now")
async def check_alerts_now(
    company_id: str,
    alert_types: Optional[List[str]] = None,
    api_key: str = Depends(get_api_key)
):
    """Check for alerts immediately"""
    try:
        # Check all opportunities
        opportunities = await alert_system.check_all_opportunities(company_id)
        
        # Filter by alert types if specified
        if alert_types:
            opportunities = [o for o in opportunities if o.get("alert_type") in alert_types]
            
        # Store alerts
        stored_results = []
        for opportunity in opportunities:
            result = await alert_system.store_alert(opportunity)
            stored_results.append(result)
            
        return {
            "status": "success",
            "company_id": company_id,
            "timestamp": datetime.utcnow().isoformat(),
            "opportunities_found": len(opportunities),
            "alert_types_found": list(set(o.get("alert_type") for o in opportunities)),
            "results": stored_results
        }
        
    except Exception as e:
        logger.error(f"Error checking alerts: {e}")
        raise HTTPException(status_code=500, detail=f"Error checking alerts: {str(e)}")

@data_integration_router.post("/context/sync")
async def synchronize_context(
    company_id: str,
    context_data: Dict[str, Any],
    api_key: str = Depends(get_api_key)
):
    """Synchronize context across all agents"""
    try:
        result = await context_manager.synchronize_context(
            company_id=company_id,
            context_data=context_data
        )
        
        return {
            "status": "success",
            "company_id": company_id,
            "timestamp": datetime.utcnow().isoformat(),
            "message": result.get("message", "Context synchronized"),
            "results": result.get("results", {})
        }
        
    except Exception as e:
        logger.error(f"Error synchronizing context: {e}")
        raise HTTPException(status_code=500, detail=f"Error synchronizing context: {str(e)}")

@data_integration_router.post("/context/push")
async def push_context_update(
    from_agent_id: str,
    to_agent_ids: List[str],
    company_id: str,
    context_data: Dict[str, Any],
    api_key: str = Depends(get_api_key)
):
    """Push context update from one agent to others"""
    try:
        result = await context_manager.push_context_update(
            from_agent_id=from_agent_id,
            to_agent_ids=to_agent_ids,
            company_id=company_id,
            context_data=context_data
        )
        
        return {
            "status": "success",
            "company_id": company_id,
            "timestamp": datetime.utcnow().isoformat(),
            "message": result.get("message", "Context pushed"),
            "from_agent": from_agent_id,
            "to_agents": to_agent_ids,
            "results": result.get("results", {})
        }
        
    except Exception as e:
        logger.error(f"Error pushing context: {e}")
        raise HTTPException(status_code=500, detail=f"Error pushing context: {str(e)}")

@data_integration_router.post("/context/broadcast")
async def broadcast_critical_update(
    company_id: str,
    update_type: str,
    update_data: Dict[str, Any],
    api_key: str = Depends(get_api_key)
):
    """Broadcast critical update to all agents"""
    try:
        result = await context_manager.broadcast_critical_update(
            company_id=company_id,
            update_type=update_type,
            update_data=update_data
        )
        
        return {
            "status": "success",
            "company_id": company_id,
            "timestamp": datetime.utcnow().isoformat(),
            "message": result.get("message", "Critical update broadcast"),
            "update_type": update_type,
            "priority_order": result.get("priority_order", []),
            "results": result.get("results", {})
        }
        
    except Exception as e:
        logger.error(f"Error broadcasting update: {e}")
        raise HTTPException(status_code=500, detail=f"Error broadcasting update: {str(e)}")

@data_integration_router.get("/context/get")
async def get_agent_context(
    company_id: str,
    agent_id: str,
    context_keys: Optional[List[str]] = None,
    api_key: str = Depends(get_api_key)
):
    """Get synchronized context for an agent"""
    try:
        result = await context_manager.get_synchronized_context(
            company_id=company_id,
            agent_id=agent_id,
            context_keys=context_keys
        )
        
        return {
            "status": "success",
            "company_id": company_id,
            "agent_id": agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "message": result.get("message", "Context retrieved"),
            "memory_count": result.get("memory_count", 0),
            "shared_context_count": result.get("shared_context_count", 0),
            "data": result.get("data", {})
        }
        
    except Exception as e:
        logger.error(f"Error getting context: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting context: {str(e)}")

# Function to register the router with the main API
def register_data_integration_routes(app):
    """Register data integration routes with the main FastAPI app"""
    app.include_router(data_integration_router)
    logger.info("Data integration routes registered")
