"""
Google Analytics Integration for Morvo AI Marketing Platform
Provides data integration with Google Analytics 4 for web and app analytics
"""

from typing import Dict, List, Any, Optional
import asyncio
import logging
from datetime import datetime, timedelta
import json
import os
import re

from external_data_base import ExternalDataSource, ExternalDataResult, DataSourceConfig

# Configure logging
logger = logging.getLogger(__name__)

class GoogleAnalyticsDataSource(ExternalDataSource):
    """
    Google Analytics data source integration
    Fetches web and app analytics data from Google Analytics 4 API
    """
    
    def source_name(self) -> str:
        """Return the name of this data source"""
        return "google_analytics"
        
    async def _validate_credentials(self):
        """Validate Google Analytics API credentials"""
        # Make a simple API call to verify credentials
        try:
            result = await self._make_request(
                endpoint="/v1beta/properties",
                method="GET",
                params={"pageSize": 1}
            )
            
            if "properties" not in result:
                raise ValueError(f"Invalid Google Analytics API credentials: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Google Analytics credential validation failed: {e}")
            raise ValueError(f"Google Analytics API credential validation failed: {e}")
    
    async def fetch_data(self, data_type: str, params: Dict[str, Any]) -> ExternalDataResult:
        """
        Fetch data from Google Analytics API
        
        Args:
            data_type: Type of data to fetch (visitors, page_views, events, etc.)
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
            
        property_id = params.get("property_id")
        if not property_id:
            raise ValueError("property_id is required")
            
        # Update last refresh timestamp
        self._update_last_refresh(data_type)
        
        try:
            # Call the appropriate method based on data_type
            if data_type == "visitors":
                result = await self._fetch_visitors(property_id, params)
            elif data_type == "page_views":
                result = await self._fetch_page_views(property_id, params)
            elif data_type == "events":
                result = await self._fetch_events(property_id, params)
            elif data_type == "conversions":
                result = await self._fetch_conversions(property_id, params)
            elif data_type == "traffic_sources":
                result = await self._fetch_traffic_sources(property_id, params)
            elif data_type == "user_demographics":
                result = await self._fetch_user_demographics(property_id, params)
            else:
                raise ValueError(f"Unsupported data type: {data_type}")
                
            return self._create_result(data_type, result)
            
        except Exception as e:
            logger.error(f"Error fetching {data_type} from Google Analytics: {e}")
            return self._create_result(
                data_type=data_type,
                data={},
                status="error",
                error_message=str(e)
            )
    
    async def _fetch_visitors(self, property_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch visitor data from Google Analytics"""
        # Set date range
        start_date = params.get("start_date", (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d"))
        end_date = params.get("end_date", datetime.utcnow().strftime("%Y-%m-%d"))
        
        # Prepare request body for the GA4 API
        request_body = {
            "dateRanges": [
                {
                    "startDate": start_date,
                    "endDate": end_date
                }
            ],
            "dimensions": [
                {"name": "date"}
            ],
            "metrics": [
                {"name": "activeUsers"},
                {"name": "newUsers"},
                {"name": "sessions"},
                {"name": "engagementRate"},
                {"name": "averageSessionDuration"}
            ]
        }
        
        # Add comparison date range if requested
        if params.get("compare_previous_period", False):
            days_diff = (datetime.strptime(end_date, "%Y-%m-%d") - datetime.strptime(start_date, "%Y-%m-%d")).days
            prev_start_date = (datetime.strptime(start_date, "%Y-%m-%d") - timedelta(days=days_diff)).strftime("%Y-%m-%d")
            prev_end_date = (datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=days_diff)).strftime("%Y-%m-%d")
            
            request_body["dateRanges"].append({
                "startDate": prev_start_date,
                "endDate": prev_end_date
            })
        
        response = await self._make_request(
            endpoint=f"/v1beta/properties/{property_id}:runReport",
            method="POST",
            data=request_body
        )
        
        # Process response into a more usable format
        rows = response.get("rows", [])
        dimension_headers = [d.get("name") for d in response.get("dimensionHeaders", [])]
        metric_headers = [m.get("name") for m in response.get("metricHeaders", [])]
        
        # Daily data points
        daily_data = []
        current_period_totals = {metric: 0 for metric in metric_headers}
        
        for row in rows:
            # Only process current period rows (index 0)
            if row.get("dimensionValues")[0].get("value"):
                date_str = row.get("dimensionValues")[0].get("value")
                metrics = {}
                
                for i, metric_value in enumerate(row.get("metricValues", [])):
                    metric_name = metric_headers[i]
                    value = float(metric_value.get("value", 0))
                    metrics[metric_name] = value
                    current_period_totals[metric_name] += value
                
                daily_data.append({
                    "date": date_str,
                    "metrics": metrics
                })
        
        # Previous period data if available
        previous_period_totals = None
        if params.get("compare_previous_period", False) and len(response.get("rows", [])) > len(daily_data):
            previous_period_totals = {metric: 0 for metric in metric_headers}
            for row in rows[len(daily_data):]:
                for i, metric_value in enumerate(row.get("metricValues", [])):
                    metric_name = metric_headers[i]
                    value = float(metric_value.get("value", 0))
                    previous_period_totals[metric_name] += value
        
        # Calculate period comparison percentages if previous data available
        period_comparison = None
        if previous_period_totals:
            period_comparison = {}
            for metric, current_value in current_period_totals.items():
                previous_value = previous_period_totals.get(metric, 0)
                if previous_value > 0:
                    percentage_change = ((current_value - previous_value) / previous_value) * 100
                    period_comparison[metric] = {
                        "current": current_value,
                        "previous": previous_value,
                        "percentage_change": round(percentage_change, 2)
                    }
        
        processed_data = {
            "property_id": property_id,
            "start_date": start_date,
            "end_date": end_date,
            "timestamp": datetime.utcnow().isoformat(),
            "totals": current_period_totals,
            "daily_data": daily_data
        }
        
        if period_comparison:
            processed_data["period_comparison"] = period_comparison
            
        return processed_data
    
    async def _fetch_page_views(self, property_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch page view data from Google Analytics"""
        # Set date range
        start_date = params.get("start_date", (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d"))
        end_date = params.get("end_date", datetime.utcnow().strftime("%Y-%m-%d"))
        limit = params.get("limit", 50)
        
        # Prepare request body for the GA4 API
        request_body = {
            "dateRanges": [
                {
                    "startDate": start_date,
                    "endDate": end_date
                }
            ],
            "dimensions": [
                {"name": "pagePath"}
            ],
            "metrics": [
                {"name": "screenPageViews"},
                {"name": "averageSessionDuration"},
                {"name": "bounceRate"},
                {"name": "engagementRate"}
            ],
            "limit": limit,
            "orderBys": [
                {
                    "metric": {"metricName": "screenPageViews"},
                    "desc": True
                }
            ]
        }
        
        response = await self._make_request(
            endpoint=f"/v1beta/properties/{property_id}:runReport",
            method="POST",
            data=request_body
        )
        
        # Process response
        rows = response.get("rows", [])
        dimension_headers = [d.get("name") for d in response.get("dimensionHeaders", [])]
        metric_headers = [m.get("name") for m in response.get("metricHeaders", [])]
        
        # Page data
        pages = []
        total_page_views = 0
        
        for row in rows:
            page_path = row.get("dimensionValues")[0].get("value", "")
            metrics = {}
            
            for i, metric_value in enumerate(row.get("metricValues", [])):
                metric_name = metric_headers[i]
                value = float(metric_value.get("value", 0))
                metrics[metric_name] = value
                
                if metric_name == "screenPageViews":
                    total_page_views += value
            
            pages.append({
                "page_path": page_path,
                "page_title": self._extract_page_title(page_path),
                "metrics": metrics
            })
        
        # Calculate page view percentages
        if total_page_views > 0:
            for page in pages:
                page_views = page["metrics"].get("screenPageViews", 0)
                page["percentage_of_total"] = round((page_views / total_page_views) * 100, 2)
        
        processed_data = {
            "property_id": property_id,
            "start_date": start_date,
            "end_date": end_date,
            "timestamp": datetime.utcnow().isoformat(),
            "total_page_views": total_page_views,
            "pages": pages
        }
            
        return processed_data
    
    def _extract_page_title(self, page_path: str) -> str:
        """Extract a readable page title from a URL path"""
        # Remove query parameters
        path = page_path.split("?")[0]
        
        # Remove trailing slash
        path = path.rstrip("/")
        
        # Get the last segment
        segments = path.split("/")
        last_segment = segments[-1] if segments[-1] else (segments[-2] if len(segments) > 1 else "Home")
        
        # Replace dashes and underscores with spaces
        title = last_segment.replace("-", " ").replace("_", " ")
        
        # Capitalize words
        title = " ".join(word.capitalize() for word in title.split())
        
        return title if title else "Home"
    
    async def _fetch_events(self, property_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch event data from Google Analytics"""
        # Set date range
        start_date = params.get("start_date", (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d"))
        end_date = params.get("end_date", datetime.utcnow().strftime("%Y-%m-%d"))
        limit = params.get("limit", 50)
        
        # Prepare request body for the GA4 API
        request_body = {
            "dateRanges": [
                {
                    "startDate": start_date,
                    "endDate": end_date
                }
            ],
            "dimensions": [
                {"name": "eventName"}
            ],
            "metrics": [
                {"name": "eventCount"},
                {"name": "eventCountPerUser"}
            ],
            "limit": limit,
            "orderBys": [
                {
                    "metric": {"metricName": "eventCount"},
                    "desc": True
                }
            ]
        }
        
        response = await self._make_request(
            endpoint=f"/v1beta/properties/{property_id}:runReport",
            method="POST",
            data=request_body
        )
        
        # Process response
        rows = response.get("rows", [])
        dimension_headers = [d.get("name") for d in response.get("dimensionHeaders", [])]
        metric_headers = [m.get("name") for m in response.get("metricHeaders", [])]
        
        # Event data
        events = []
        total_events = 0
        
        for row in rows:
            event_name = row.get("dimensionValues")[0].get("value", "")
            metrics = {}
            
            for i, metric_value in enumerate(row.get("metricValues", [])):
                metric_name = metric_headers[i]
                value = float(metric_value.get("value", 0))
                metrics[metric_name] = value
                
                if metric_name == "eventCount":
                    total_events += value
            
            events.append({
                "event_name": event_name,
                "metrics": metrics
            })
        
        # Calculate event percentages
        if total_events > 0:
            for event in events:
                event_count = event["metrics"].get("eventCount", 0)
                event["percentage_of_total"] = round((event_count / total_events) * 100, 2)
        
        processed_data = {
            "property_id": property_id,
            "start_date": start_date,
            "end_date": end_date,
            "timestamp": datetime.utcnow().isoformat(),
            "total_events": total_events,
            "events": events
        }
            
        return processed_data
    
    async def _fetch_conversions(self, property_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch conversion data from Google Analytics"""
        # Set date range
        start_date = params.get("start_date", (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d"))
        end_date = params.get("end_date", datetime.utcnow().strftime("%Y-%m-%d"))
        
        # Prepare request body for conversion events
        # We need to first fetch all conversion events for this property
        events_request = {
            "pageSize": 100
        }
        
        events_response = await self._make_request(
            endpoint=f"/v1beta/properties/{property_id}/conversionEvents",
            method="GET",
            params=events_request
        )
        
        conversion_events = []
        for event in events_response.get("conversionEvents", []):
            conversion_events.append(event.get("eventName"))
        
        if not conversion_events:
            # No conversion events defined
            return {
                "property_id": property_id,
                "start_date": start_date,
                "end_date": end_date,
                "timestamp": datetime.utcnow().isoformat(),
                "total_conversions": 0,
                "message": "No conversion events defined for this property",
                "conversions": []
            }
        
        # Now fetch data for these conversion events
        request_body = {
            "dateRanges": [
                {
                    "startDate": start_date,
                    "endDate": end_date
                }
            ],
            "dimensions": [
                {"name": "eventName"},
                {"name": "date"}
            ],
            "metrics": [
                {"name": "eventCount"},
                {"name": "eventCountPerUser"},
                {"name": "conversions"},
                {"name": "conversionRate"}
            ],
            "dimensionFilter": {
                "filter": {
                    "fieldName": "eventName",
                    "inListFilter": {
                        "values": conversion_events
                    }
                }
            }
        }
        
        response = await self._make_request(
            endpoint=f"/v1beta/properties/{property_id}:runReport",
            method="POST",
            data=request_body
        )
        
        # Process response
        rows = response.get("rows", [])
        
        # Reorganize data by conversion event
        conversion_data = {}
        total_conversions = 0
        
        for row in rows:
            event_name = row.get("dimensionValues")[0].get("value", "")
            date = row.get("dimensionValues")[1].get("value", "")
            
            if event_name not in conversion_data:
                conversion_data[event_name] = {
                    "event_name": event_name,
                    "total_count": 0,
                    "average_per_user": 0,
                    "conversion_rate": 0,
                    "daily_data": []
                }
            
            event_count = float(row.get("metricValues")[0].get("value", 0))
            count_per_user = float(row.get("metricValues")[1].get("value", 0))
            conversion_count = float(row.get("metricValues")[2].get("value", 0))
            conversion_rate = float(row.get("metricValues")[3].get("value", 0))
            
            conversion_data[event_name]["total_count"] += event_count
            total_conversions += conversion_count
            
            # Use the latest values for these metrics
            conversion_data[event_name]["average_per_user"] = count_per_user
            conversion_data[event_name]["conversion_rate"] = conversion_rate
            
            conversion_data[event_name]["daily_data"].append({
                "date": date,
                "count": event_count,
                "conversion_rate": conversion_rate
            })
        
        # Convert to list and sort by total count
        conversions = list(conversion_data.values())
        conversions.sort(key=lambda x: x["total_count"], reverse=True)
        
        processed_data = {
            "property_id": property_id,
            "start_date": start_date,
            "end_date": end_date,
            "timestamp": datetime.utcnow().isoformat(),
            "total_conversions": total_conversions,
            "conversions": conversions
        }
            
        return processed_data
    
    async def _fetch_traffic_sources(self, property_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch traffic source data from Google Analytics"""
        # Set date range
        start_date = params.get("start_date", (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d"))
        end_date = params.get("end_date", datetime.utcnow().strftime("%Y-%m-%d"))
        
        # Prepare request body for the GA4 API
        request_body = {
            "dateRanges": [
                {
                    "startDate": start_date,
                    "endDate": end_date
                }
            ],
            "dimensions": [
                {"name": "sessionSource"},
                {"name": "sessionMedium"}
            ],
            "metrics": [
                {"name": "sessions"},
                {"name": "activeUsers"},
                {"name": "engagementRate"},
                {"name": "conversions"}
            ],
            "orderBys": [
                {
                    "metric": {"metricName": "sessions"},
                    "desc": True
                }
            ]
        }
        
        response = await self._make_request(
            endpoint=f"/v1beta/properties/{property_id}:runReport",
            method="POST",
            data=request_body
        )
        
        # Process response
        rows = response.get("rows", [])
        
        # Group by source and medium
        sources_data = {}
        total_sessions = 0
        
        for row in rows:
            source = row.get("dimensionValues")[0].get("value", "(none)")
            medium = row.get("dimensionValues")[1].get("value", "(none)")
            
            # Clean up values
            source = source if source else "(direct)"
            medium = medium if medium else "(none)"
            
            source_medium = f"{source} / {medium}"
            
            sessions = float(row.get("metricValues")[0].get("value", 0))
            users = float(row.get("metricValues")[1].get("value", 0))
            engagement_rate = float(row.get("metricValues")[2].get("value", 0))
            conversions = float(row.get("metricValues")[3].get("value", 0))
            
            # Group into common marketing channels
            channel = self._categorize_traffic_source(source, medium)
            
            if channel not in sources_data:
                sources_data[channel] = {
                    "channel": channel,
                    "sources": [],
                    "total_sessions": 0,
                    "total_users": 0,
                    "total_conversions": 0
                }
            
            sources_data[channel]["sources"].append({
                "source": source,
                "medium": medium,
                "source_medium": source_medium,
                "sessions": sessions,
                "users": users,
                "engagement_rate": engagement_rate,
                "conversions": conversions
            })
            
            sources_data[channel]["total_sessions"] += sessions
            sources_data[channel]["total_users"] += users
            sources_data[channel]["total_conversions"] += conversions
            total_sessions += sessions
        
        # Convert to list and calculate percentages
        channels = []
        for channel, data in sources_data.items():
            if total_sessions > 0:
                data["percentage"] = round((data["total_sessions"] / total_sessions) * 100, 2)
            else:
                data["percentage"] = 0
                
            # Sort sources within channel
            data["sources"].sort(key=lambda x: x["sessions"], reverse=True)
            channels.append(data)
        
        # Sort channels by total sessions
        channels.sort(key=lambda x: x["total_sessions"], reverse=True)
        
        processed_data = {
            "property_id": property_id,
            "start_date": start_date,
            "end_date": end_date,
            "timestamp": datetime.utcnow().isoformat(),
            "total_sessions": total_sessions,
            "channels": channels
        }
            
        return processed_data
    
    def _categorize_traffic_source(self, source: str, medium: str) -> str:
        """Categorize traffic source and medium into common marketing channels"""
        source = source.lower()
        medium = medium.lower()
        
        if source == "(direct)" or source == "direct" or medium == "(none)":
            return "Direct"
        elif "google" in source and medium == "organic":
            return "Organic Search"
        elif medium == "organic" or medium == "search":
            return "Organic Search"
        elif medium == "cpc" or medium == "ppc" or medium == "paid":
            return "Paid Search"
        elif medium == "social" or medium == "social-network" or source in ["facebook", "twitter", "linkedin", "instagram", "pinterest"]:
            return "Social"
        elif medium == "email":
            return "Email"
        elif medium == "referral":
            return "Referral"
        elif medium == "affiliate":
            return "Affiliate"
        elif "display" in medium:
            return "Display"
        else:
            return "Other"
    
    async def _fetch_user_demographics(self, property_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch user demographic data from Google Analytics"""
        # Set date range
        start_date = params.get("start_date", (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d"))
        end_date = params.get("end_date", datetime.utcnow().strftime("%Y-%m-%d"))
        
        # We need to make multiple requests for different demographics
        
        # 1. Country
        country_request = {
            "dateRanges": [
                {
                    "startDate": start_date,
                    "endDate": end_date
                }
            ],
            "dimensions": [
                {"name": "country"}
            ],
            "metrics": [
                {"name": "activeUsers"}
            ],
            "orderBys": [
                {
                    "metric": {"metricName": "activeUsers"},
                    "desc": True
                }
            ],
            "limit": 25
        }
        
        country_response = await self._make_request(
            endpoint=f"/v1beta/properties/{property_id}:runReport",
            method="POST",
            data=country_request
        )
        
        # 2. Device
        device_request = {
            "dateRanges": [
                {
                    "startDate": start_date,
                    "endDate": end_date
                }
            ],
            "dimensions": [
                {"name": "deviceCategory"}
            ],
            "metrics": [
                {"name": "activeUsers"}
            ],
            "orderBys": [
                {
                    "metric": {"metricName": "activeUsers"},
                    "desc": True
                }
            ]
        }
        
        device_response = await self._make_request(
            endpoint=f"/v1beta/properties/{property_id}:runReport",
            method="POST",
            data=device_request
        )
        
        # 3. Browser
        browser_request = {
            "dateRanges": [
                {
                    "startDate": start_date,
                    "endDate": end_date
                }
            ],
            "dimensions": [
                {"name": "browser"}
            ],
            "metrics": [
                {"name": "activeUsers"}
            ],
            "orderBys": [
                {
                    "metric": {"metricName": "activeUsers"},
                    "desc": True
                }
            ],
            "limit": 10
        }
        
        browser_response = await self._make_request(
            endpoint=f"/v1beta/properties/{property_id}:runReport",
            method="POST",
            data=browser_request
        )
        
        # Process country data
        countries = []
        total_users = 0
        
        for row in country_response.get("rows", []):
            country = row.get("dimensionValues")[0].get("value", "")
            users = float(row.get("metricValues")[0].get("value", 0))
            
            countries.append({
                "country": country,
                "users": users
            })
            
            total_users += users
        
        # Process device data
        devices = []
        
        for row in device_response.get("rows", []):
            device = row.get("dimensionValues")[0].get("value", "")
            users = float(row.get("metricValues")[0].get("value", 0))
            
            devices.append({
                "device": device,
                "users": users,
                "percentage": 0  # Will calculate below
            })
        
        # Process browser data
        browsers = []
        
        for row in browser_response.get("rows", []):
            browser = row.get("dimensionValues")[0].get("value", "")
            users = float(row.get("metricValues")[0].get("value", 0))
            
            browsers.append({
                "browser": browser,
                "users": users,
                "percentage": 0  # Will calculate below
            })
        
        # Calculate percentages
        if total_users > 0:
            for country in countries:
                country["percentage"] = round((country["users"] / total_users) * 100, 2)
                
            for device in devices:
                device["percentage"] = round((device["users"] / total_users) * 100, 2)
                
            for browser in browsers:
                browser["percentage"] = round((browser["users"] / total_users) * 100, 2)
        
        processed_data = {
            "property_id": property_id,
            "start_date": start_date,
            "end_date": end_date,
            "timestamp": datetime.utcnow().isoformat(),
            "total_users": total_users,
            "countries": countries,
            "devices": devices,
            "browsers": browsers
        }
            
        return processed_data
