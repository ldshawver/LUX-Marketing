"""
Clickadilla Ad Network Integration
"""

import os
import requests
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ClickadillaService:
    """Service for Clickadilla ad network integration"""
    
    def __init__(self):
        self.api_token = os.getenv('CLICKADILLA_TOKEN')
        self.api_base = 'https://api.clickadilla.com'
        
        if not self.api_token:
            logger.warning("Clickadilla API token not configured")
    
    def _get_headers(self):
        """Get API request headers"""
        return {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json'
        }
    
    def get_campaigns(self):
        """
        Get list of all campaigns.
        
        Returns:
            list: Campaign data
        """
        try:
            url = f"{self.api_base}/campaigns"
            response = requests.get(url, headers=self._get_headers(), timeout=30)
            
            if response.status_code == 200:
                return response.json().get('campaigns', [])
            else:
                logger.error(f"Clickadilla API error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error fetching Clickadilla campaigns: {e}")
            return []
    
    def get_campaign_stats(self, campaign_id, start_date=None, end_date=None):
        """
        Get statistics for a specific campaign.
        
        Args:
            campaign_id: Campaign ID
            start_date: Start date (datetime)
            end_date: End date (datetime)
        
        Returns:
            dict: Campaign statistics
        """
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            url = f"{self.api_base}/campaigns/{campaign_id}/statistics"
            params = {
                'date_from': start_date.strftime('%Y-%m-%d'),
                'date_to': end_date.strftime('%Y-%m-%d')
            }
            
            response = requests.get(
                url,
                headers=self._get_headers(),
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Clickadilla API error: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Error fetching Clickadilla campaign stats: {e}")
            return {}
    
    def get_performance_summary(self, days=30):
        """
        Get performance summary for all campaigns.
        
        Returns:
            dict: Performance metrics
        """
        try:
            campaigns = self.get_campaigns()
            
            total_impressions = 0
            total_clicks = 0
            total_spend = 0
            total_conversions = 0
            
            start_date = datetime.utcnow() - timedelta(days=days)
            end_date = datetime.utcnow()
            
            for campaign in campaigns:
                stats = self.get_campaign_stats(
                    campaign.get('id'),
                    start_date,
                    end_date
                )
                
                total_impressions += stats.get('impressions', 0)
                total_clicks += stats.get('clicks', 0)
                total_spend += stats.get('cost', 0)
                total_conversions += stats.get('conversions', 0)
            
            ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            cpc = (total_spend / total_clicks) if total_clicks > 0 else 0
            conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
            
            return {
                'impressions': total_impressions,
                'clicks': total_clicks,
                'spend': total_spend,
                'conversions': total_conversions,
                'ctr': ctr,
                'cpc': cpc,
                'conversion_rate': conversion_rate,
                'period_days': days
            }
            
        except Exception as e:
            logger.error(f"Error calculating Clickadilla performance: {e}")
            return {
                'impressions': 0,
                'clicks': 0,
                'spend': 0,
                'conversions': 0,
                'ctr': 0,
                'cpc': 0,
                'conversion_rate': 0,
                'period_days': days
            }
    
    def create_campaign(self, campaign_data):
        """
        Create a new campaign.
        
        Args:
            campaign_data: Campaign configuration
        
        Returns:
            dict: Created campaign data
        """
        try:
            url = f"{self.api_base}/campaigns"
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=campaign_data,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                return {'success': True, 'data': response.json()}
            else:
                logger.error(f"Clickadilla campaign creation error: {response.status_code}")
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            logger.error(f"Error creating Clickadilla campaign: {e}")
            return {'success': False, 'error': str(e)}
    
    def update_campaign_status(self, campaign_id, status):
        """
        Update campaign status.
        
        Args:
            campaign_id: Campaign ID
            status: 'active' or 'paused'
        
        Returns:
            bool: Success status
        """
        try:
            url = f"{self.api_base}/campaigns/{campaign_id}"
            response = requests.patch(
                url,
                headers=self._get_headers(),
                json={'status': status},
                timeout=30
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Error updating Clickadilla campaign status: {e}")
            return False
    
    def get_balance(self):
        """
        Get account balance.
        
        Returns:
            float: Account balance
        """
        try:
            url = f"{self.api_base}/account/balance"
            response = requests.get(url, headers=self._get_headers(), timeout=30)
            
            if response.status_code == 200:
                return response.json().get('balance', 0)
            else:
                return 0
                
        except Exception as e:
            logger.error(f"Error fetching Clickadilla balance: {e}")
            return 0
