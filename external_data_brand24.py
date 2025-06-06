"""
Brand24 Integration for Morvo AI Marketing Platform
Provides data integration with Brand24 API for social listening and sentiment analysis
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

class Brand24DataSource(ExternalDataSource):
    """
    Brand24 data source integration
    Fetches social mentions, sentiment analysis and brand monitoring data
    """
    
    def source_name(self) -> str:
        """Return the name of this data source"""
        return "brand24"
        
    async def _validate_credentials(self):
        """Validate Brand24 API credentials"""
        # Make a simple API call to verify credentials
        try:
            result = await self._make_request(
                endpoint="/projects",
                method="GET"
            )
            
            if "error" in result:
                raise ValueError(f"Invalid Brand24 API credentials: {result.get('error', 'Unknown error')}")
                
        except Exception as e:
            logger.error(f"Brand24 credential validation failed: {e}")
            raise ValueError(f"Brand24 API credential validation failed: {e}")
    
    async def fetch_data(self, data_type: str, params: Dict[str, Any]) -> ExternalDataResult:
        """
        Fetch data from Brand24 API
        
        Args:
            data_type: Type of data to fetch (mentions, sentiment, analytics, etc.)
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
            
        project_id = params.get("project_id")
        if not project_id:
            raise ValueError("project_id is required")
            
        # Update last refresh timestamp
        self._update_last_refresh(data_type)
        
        try:
            # Call the appropriate method based on data_type
            if data_type == "mentions":
                result = await self._fetch_mentions(project_id, params)
            elif data_type == "sentiment":
                result = await self._fetch_sentiment(project_id, params)
            elif data_type == "analytics":
                result = await self._fetch_analytics(project_id, params)
            elif data_type == "top_influencers":
                result = await self._fetch_top_influencers(project_id, params)
            elif data_type == "trending_hashtags":
                result = await self._fetch_trending_hashtags(project_id, params)
            else:
                raise ValueError(f"Unsupported data type: {data_type}")
                
            return self._create_result(data_type, result)
            
        except Exception as e:
            logger.error(f"Error fetching {data_type} from Brand24: {e}")
            return self._create_result(
                data_type=data_type,
                data={},
                status="error",
                error_message=str(e)
            )
    
    async def _fetch_mentions(self, project_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch social mentions from Brand24"""
        # Set date range
        days = params.get("days", 30)
        to_date = datetime.utcnow()
        from_date = to_date - timedelta(days=days)
        
        # Format dates
        from_date_str = from_date.strftime("%Y-%m-%d")
        to_date_str = to_date.strftime("%Y-%m-%d")
        
        # Optional filters
        sentiment = params.get("sentiment", None)  # positive, negative, neutral, or null for all
        limit = params.get("limit", 100)
        
        # Prepare API request
        api_params = {
            "projectId": project_id,
            "fromDate": from_date_str,
            "toDate": to_date_str,
            "limit": limit,
            "order": "desc"
        }
        
        if sentiment:
            api_params["sentiment"] = sentiment
            
        response = await self._make_request(
            endpoint=f"/mentions",
            method="GET",
            params=api_params
        )
        
        # Process mentions data
        mentions = []
        for item in response.get("results", []):
            mention = {
                "id": item.get("id"),
                "date": item.get("date"),
                "text": item.get("text"),
                "url": item.get("url"),
                "source_type": item.get("sourceType"),
                "sentiment": item.get("sentiment"),
                "author": {
                    "name": item.get("author", {}).get("name"),
                    "url": item.get("author", {}).get("url"),
                    "followers": item.get("author", {}).get("followersCount")
                },
                "likes": item.get("likes"),
                "comments": item.get("comments"),
                "shares": item.get("shares")
            }
            mentions.append(mention)
        
        # Get counts
        positive_count = sum(1 for m in mentions if m["sentiment"] == "positive")
        negative_count = sum(1 for m in mentions if m["sentiment"] == "negative")
        neutral_count = sum(1 for m in mentions if m["sentiment"] == "neutral")
        
        # Group by source type
        source_types = {}
        for mention in mentions:
            source = mention["source_type"]
            if source not in source_types:
                source_types[source] = 0
            source_types[source] += 1
        
        processed_data = {
            "project_id": project_id,
            "from_date": from_date_str,
            "to_date": to_date_str,
            "timestamp": datetime.utcnow().isoformat(),
            "total_mentions": len(mentions),
            "sentiment_summary": {
                "positive": positive_count,
                "negative": negative_count,
                "neutral": neutral_count,
                "positive_percentage": round((positive_count / len(mentions) * 100), 2) if mentions else 0,
                "negative_percentage": round((negative_count / len(mentions) * 100), 2) if mentions else 0,
                "neutral_percentage": round((neutral_count / len(mentions) * 100), 2) if mentions else 0
            },
            "source_types": source_types,
            "mentions": mentions
        }
        
        return processed_data
    
    async def _fetch_sentiment(self, project_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch sentiment analysis data from Brand24"""
        # Set date range
        days = params.get("days", 30)
        to_date = datetime.utcnow()
        from_date = to_date - timedelta(days=days)
        
        # Format dates
        from_date_str = from_date.strftime("%Y-%m-%d")
        to_date_str = to_date.strftime("%Y-%m-%d")
        
        # Prepare API request
        api_params = {
            "projectId": project_id,
            "fromDate": from_date_str,
            "toDate": to_date_str
        }
        
        response = await self._make_request(
            endpoint=f"/analytics/sentiment",
            method="GET",
            params=api_params
        )
        
        # Process sentiment data
        daily_sentiment = []
        
        for item in response.get("data", []):
            date = item.get("date")
            positive = item.get("positive", 0)
            negative = item.get("negative", 0)
            neutral = item.get("neutral", 0)
            total = positive + negative + neutral
            
            sentiment_score = 0
            if total > 0:
                # Calculate a sentiment score from -1 to 1
                sentiment_score = round((positive - negative) / total, 2)
            
            daily_sentiment.append({
                "date": date,
                "positive": positive,
                "negative": negative,
                "neutral": neutral,
                "total": total,
                "sentiment_score": sentiment_score,
                "positive_percentage": round((positive / total * 100), 2) if total else 0,
                "negative_percentage": round((negative / total * 100), 2) if total else 0
            })
        
        # Calculate overall sentiment metrics
        total_positive = sum(day["positive"] for day in daily_sentiment)
        total_negative = sum(day["negative"] for day in daily_sentiment)
        total_neutral = sum(day["neutral"] for day in daily_sentiment)
        total_mentions = total_positive + total_negative + total_neutral
        
        overall_sentiment_score = 0
        if total_mentions > 0:
            overall_sentiment_score = round((total_positive - total_negative) / total_mentions, 2)
        
        # Calculate trend (comparing first half with second half)
        if len(daily_sentiment) >= 4:
            mid_point = len(daily_sentiment) // 2
            first_half = daily_sentiment[:mid_point]
            second_half = daily_sentiment[mid_point:]
            
            first_half_score = sum(day["sentiment_score"] for day in first_half) / len(first_half)
            second_half_score = sum(day["sentiment_score"] for day in second_half) / len(second_half)
            
            sentiment_trend = round(second_half_score - first_half_score, 2)
        else:
            sentiment_trend = 0
        
        processed_data = {
            "project_id": project_id,
            "from_date": from_date_str,
            "to_date": to_date_str,
            "timestamp": datetime.utcnow().isoformat(),
            "overall_sentiment": {
                "positive": total_positive,
                "negative": total_negative,
                "neutral": total_neutral,
                "total_mentions": total_mentions,
                "sentiment_score": overall_sentiment_score,
                "sentiment_trend": sentiment_trend,
                "positive_percentage": round((total_positive / total_mentions * 100), 2) if total_mentions else 0,
                "negative_percentage": round((total_negative / total_mentions * 100), 2) if total_mentions else 0
            },
            "daily_sentiment": daily_sentiment
        }
        
        return processed_data
    
    async def _fetch_analytics(self, project_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch analytics overview from Brand24"""
        # Set date range
        days = params.get("days", 30)
        to_date = datetime.utcnow()
        from_date = to_date - timedelta(days=days)
        
        # Format dates
        from_date_str = from_date.strftime("%Y-%m-%d")
        to_date_str = to_date.strftime("%Y-%m-%d")
        
        # Prepare API request
        api_params = {
            "projectId": project_id,
            "fromDate": from_date_str,
            "toDate": to_date_str
        }
        
        response = await self._make_request(
            endpoint=f"/analytics/summary",
            method="GET",
            params=api_params
        )
        
        # Process analytics data
        summary = response.get("summary", {})
        
        # Get previous period for comparison
        prev_from_date = from_date - timedelta(days=days)
        prev_to_date = to_date - timedelta(days=days)
        prev_from_date_str = prev_from_date.strftime("%Y-%m-%d")
        prev_to_date_str = prev_to_date.strftime("%Y-%m-%d")
        
        prev_api_params = {
            "projectId": project_id,
            "fromDate": prev_from_date_str,
            "toDate": prev_to_date_str
        }
        
        try:
            prev_response = await self._make_request(
                endpoint=f"/analytics/summary",
                method="GET",
                params=prev_api_params
            )
            prev_summary = prev_response.get("summary", {})
        except Exception as e:
            logger.warning(f"Error fetching previous period data: {e}")
            prev_summary = {}
        
        # Calculate period-over-period changes
        mentions_count = summary.get("mentionsCount", 0)
        prev_mentions_count = prev_summary.get("mentionsCount", 0)
        
        mentions_change = 0
        if prev_mentions_count > 0:
            mentions_change = round(((mentions_count - prev_mentions_count) / prev_mentions_count) * 100, 2)
        
        engagement_count = summary.get("engagementCount", 0)
        prev_engagement_count = prev_summary.get("engagementCount", 0)
        
        engagement_change = 0
        if prev_engagement_count > 0:
            engagement_change = round(((engagement_count - prev_engagement_count) / prev_engagement_count) * 100, 2)
        
        # Calculate engagement rate
        engagement_rate = 0
        if mentions_count > 0:
            engagement_rate = round(engagement_count / mentions_count, 2)
        
        processed_data = {
            "project_id": project_id,
            "from_date": from_date_str,
            "to_date": to_date_str,
            "timestamp": datetime.utcnow().isoformat(),
            "mentions": {
                "total": mentions_count,
                "change_percentage": mentions_change,
                "previous_period": prev_mentions_count
            },
            "engagement": {
                "total": engagement_count,
                "change_percentage": engagement_change,
                "previous_period": prev_engagement_count,
                "engagement_rate": engagement_rate
            },
            "reach": {
                "total": summary.get("reachCount", 0),
                "social": summary.get("socialReachCount", 0),
                "non_social": summary.get("nonSocialReachCount", 0)
            },
            "social_media": {
                "total": summary.get("socialMediaCount", 0),
                "facebook": summary.get("facebookCount", 0),
                "twitter": summary.get("twitterCount", 0),
                "instagram": summary.get("instagramCount", 0),
                "youtube": summary.get("youtubeCount", 0)
            },
            "sentiment": {
                "positive": summary.get("positiveCount", 0),
                "negative": summary.get("negativeCount", 0),
                "neutral": summary.get("neutralCount", 0)
            }
        }
        
        return processed_data
    
    async def _fetch_top_influencers(self, project_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch top influencers from Brand24"""
        # Set date range
        days = params.get("days", 30)
        to_date = datetime.utcnow()
        from_date = to_date - timedelta(days=days)
        
        # Format dates
        from_date_str = from_date.strftime("%Y-%m-%d")
        to_date_str = to_date.strftime("%Y-%m-%d")
        
        # Optional parameters
        limit = params.get("limit", 20)
        min_mentions = params.get("min_mentions", 2)
        
        # Prepare API request
        api_params = {
            "projectId": project_id,
            "fromDate": from_date_str,
            "toDate": to_date_str,
            "limit": limit
        }
        
        response = await self._make_request(
            endpoint=f"/analytics/influencers",
            method="GET",
            params=api_params
        )
        
        # Process influencers data
        influencers = []
        
        for item in response.get("influencers", []):
            # Only include influencers with enough mentions
            mentions_count = item.get("mentionsCount", 0)
            if mentions_count >= min_mentions:
                influencer = {
                    "name": item.get("name", ""),
                    "url": item.get("url", ""),
                    "mentions_count": mentions_count,
                    "reach": item.get("reach", 0),
                    "followers": item.get("followersCount", 0),
                    "source_type": item.get("sourceType", ""),
                    "influence_score": item.get("influenceScore", 0),
                    "sentiment": {
                        "positive": item.get("positiveMentionsCount", 0),
                        "negative": item.get("negativeMentionsCount", 0),
                        "neutral": item.get("neutralMentionsCount", 0)
                    }
                }
                influencers.append(influencer)
        
        # Group by source type
        source_breakdown = {}
        for influencer in influencers:
            source = influencer["source_type"]
            if source not in source_breakdown:
                source_breakdown[source] = 0
            source_breakdown[source] += 1
        
        processed_data = {
            "project_id": project_id,
            "from_date": from_date_str,
            "to_date": to_date_str,
            "timestamp": datetime.utcnow().isoformat(),
            "total_influencers": len(influencers),
            "source_breakdown": source_breakdown,
            "influencers": influencers
        }
        
        return processed_data
    
    async def _fetch_trending_hashtags(self, project_id: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch trending hashtags from Brand24"""
        # Set date range
        days = params.get("days", 30)
        to_date = datetime.utcnow()
        from_date = to_date - timedelta(days=days)
        
        # Format dates
        from_date_str = from_date.strftime("%Y-%m-%d")
        to_date_str = to_date.strftime("%Y-%m-%d")
        
        # Optional parameters
        limit = params.get("limit", 30)
        
        # Prepare API request
        api_params = {
            "projectId": project_id,
            "fromDate": from_date_str,
            "toDate": to_date_str,
            "limit": limit
        }
        
        response = await self._make_request(
            endpoint=f"/analytics/hashtags",
            method="GET",
            params=api_params
        )
        
        # Process hashtags data
        hashtags = []
        
        for item in response.get("hashtags", []):
            hashtag = {
                "tag": item.get("tag", "").replace("#", ""),
                "mentions_count": item.get("mentionsCount", 0),
                "reach": item.get("reach", 0),
                "trending_score": item.get("trendingScore", 0),
                "sentiment": {
                    "positive": item.get("positiveMentionsCount", 0),
                    "negative": item.get("negativeMentionsCount", 0),
                    "neutral": item.get("neutralMentionsCount", 0)
                }
            }
            hashtags.append(hashtag)
        
        # Add total counts
        total_mentions = sum(h["mentions_count"] for h in hashtags)
        total_reach = sum(h["reach"] for h in hashtags)
        
        # Calculate percentages
        if total_mentions > 0:
            for hashtag in hashtags:
                hashtag["percentage"] = round((hashtag["mentions_count"] / total_mentions) * 100, 2)
        
        processed_data = {
            "project_id": project_id,
            "from_date": from_date_str,
            "to_date": to_date_str,
            "timestamp": datetime.utcnow().isoformat(),
            "total_hashtags": len(hashtags),
            "total_mentions": total_mentions,
            "total_reach": total_reach,
            "hashtags": hashtags
        }
        
        return processed_data
