"""
Google Analytics 4 Integration Client
Fetches real-time analytics data from GA4
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

try:
    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import (
        DateRange,
        Dimension,
        Metric,
        RunReportRequest,
    )
    GA4_AVAILABLE = True
except ImportError:
    GA4_AVAILABLE = False
    logger.warning("google-analytics-data not installed. GA4 integration unavailable.")


class GA4Client:
    """Google Analytics 4 API Client"""
    
    def __init__(self):
        self.property_id = os.getenv('GA4_PROPERTY_ID')
        self.credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        self.client = None
        
        if GA4_AVAILABLE and self.property_id:
            try:
                self.client = BetaAnalyticsDataClient()
                logger.info(f"GA4 Client initialized for property: {self.property_id}")
            except Exception as e:
                logger.error(f"Failed to initialize GA4 client: {e}")
    
    def is_configured(self) -> bool:
        """Check if GA4 is properly configured"""
        return self.client is not None and self.property_id is not None
    
    def get_metrics(self, days: int = 30) -> Dict[str, Any]:
        """
        Fetch key metrics from GA4
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dictionary of GA4 metrics
        """
        if not self.is_configured():
            logger.warning("GA4 not configured, returning empty metrics")
            return {}
        
        try:
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
                metrics=[
                    Metric(name="sessions"),
                    Metric(name="totalUsers"),
                    Metric(name="newUsers"),
                    Metric(name="screenPageViews"),
                    Metric(name="averageSessionDuration"),
                    Metric(name="engagementRate"),
                    Metric(name="bounceRate"),
                ],
            )
            
            response = self.client.run_report(request)
            
            if response.rows:
                row = response.rows[0]
                metrics = {
                    'sessions': int(row.metric_values[0].value),
                    'total_users': int(row.metric_values[1].value),
                    'new_users': int(row.metric_values[2].value),
                    'page_views': int(row.metric_values[3].value),
                    'avg_session_duration': float(row.metric_values[4].value),
                    'engagement_rate': float(row.metric_values[5].value) * 100,
                    'bounce_rate': float(row.metric_values[6].value) * 100,
                }
                
                logger.info(f"Retrieved GA4 metrics: {metrics}")
                return metrics
            else:
                logger.warning("No GA4 data available")
                return {}
                
        except Exception as e:
            logger.error(f"Error fetching GA4 metrics: {e}")
            return {}
    
    def get_traffic_sources(self, days: int = 30) -> Dict[str, int]:
        """Get traffic by source/medium"""
        if not self.is_configured():
            return {}
        
        try:
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
                dimensions=[Dimension(name="sessionDefaultChannelGroup")],
                metrics=[Metric(name="sessions")],
            )
            
            response = self.client.run_report(request)
            
            sources = {}
            for row in response.rows:
                channel = row.dimension_values[0].value
                sessions = int(row.metric_values[0].value)
                sources[channel] = sessions
            
            return sources
            
        except Exception as e:
            logger.error(f"Error fetching traffic sources: {e}")
            return {}
    
    def get_top_pages(self, days: int = 30, limit: int = 10) -> list:
        """Get top pages by views"""
        if not self.is_configured():
            return []
        
        try:
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
                dimensions=[Dimension(name="pagePath")],
                metrics=[Metric(name="screenPageViews")],
                limit=limit,
            )
            
            response = self.client.run_report(request)
            
            pages = []
            for row in response.rows:
                pages.append({
                    'page': row.dimension_values[0].value,
                    'views': int(row.metric_values[0].value)
                })
            
            return pages
            
        except Exception as e:
            logger.error(f"Error fetching top pages: {e}")
            return []
    
    def get_engagement_metrics(self, days: int = 30) -> Dict[str, Any]:
        """Get detailed engagement metrics"""
        if not self.is_configured():
            return {}
        
        try:
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                date_ranges=[DateRange(start_date=f"{days}daysAgo", end_date="today")],
                metrics=[
                    Metric(name="userEngagementDuration"),
                    Metric(name="engagedSessions"),
                    Metric(name="eventCount"),
                ],
            )
            
            response = self.client.run_report(request)
            
            if response.rows:
                row = response.rows[0]
                return {
                    'total_engagement_duration': float(row.metric_values[0].value),
                    'engaged_sessions': int(row.metric_values[1].value),
                    'total_events': int(row.metric_values[2].value),
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"Error fetching engagement metrics: {e}")
            return {}


# Global instance
_ga4_client = None

def get_ga4_client() -> GA4Client:
    """Get or create GA4 client singleton"""
    global _ga4_client
    if _ga4_client is None:
        _ga4_client = GA4Client()
    return _ga4_client
