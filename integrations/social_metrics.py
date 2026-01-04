"""
Live Social Media Metrics Service
Fetches real-time follower counts and engagement data from Instagram, TikTok, and Facebook
"""

import logging
import requests
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)


class SocialMediaMetrics:
    """Fetch live social media metrics from connected accounts"""
    
    @staticmethod
    def get_instagram_metrics(access_token: str) -> Tuple[Dict, Optional[str]]:
        """Get Instagram account metrics (followers, engagement, etc.)"""
        try:
            if not access_token or len(access_token) < 20:
                return {}, "Invalid or missing access token"
            
            me_response = requests.get(
                'https://graph.instagram.com/v18.0/me',
                params={'fields': 'id,username,name', 'access_token': access_token},
                timeout=10
            )
            
            if me_response.status_code != 200:
                error_data = me_response.json() if me_response.text else {}
                error_msg = error_data.get('error', {}).get('message', f'Status {me_response.status_code}')
                error_type = error_data.get('error', {}).get('type', '')
                
                if 'OAuthException' in error_type or 'Invalid' in error_msg:
                    return {}, f"Token expired or invalid. Please reconnect Instagram in Settings."
                return {}, f"Instagram API error: {error_msg}"
            
            me_data = me_response.json()
            account_id = me_data.get('id')
            
            if not account_id:
                return {}, "Could not get Instagram account ID"
            
            insights_response = requests.get(
                f'https://graph.instagram.com/v18.0/{account_id}',
                params={
                    'fields': 'followers_count,biography,profile_picture_url,website,media_count',
                    'access_token': access_token
                },
                timeout=10
            )
            
            if insights_response.status_code == 200:
                data = insights_response.json()
                return {
                    'platform': 'instagram',
                    'followers': data.get('followers_count', 0),
                    'username': me_data.get('username'),
                    'name': me_data.get('name'),
                    'media_count': data.get('media_count', 0),
                    'bio': data.get('biography', ''),
                    'profile_picture_url': data.get('profile_picture_url'),
                    'website': data.get('website', ''),
                }, None
            else:
                error_data = insights_response.json() if insights_response.text else {}
                error_msg = error_data.get('error', {}).get('message', f'Status {insights_response.status_code}')
                return {}, f"Instagram insights error: {error_msg}"
                
        except Exception as e:
            logger.error(f"Instagram metrics error: {e}")
            return {}, str(e)
    
    @staticmethod
    def get_tiktok_metrics(access_token: str) -> Tuple[Dict, Optional[str]]:
        """Get TikTok account metrics (followers, verified status, bio)"""
        try:
            response = requests.get(
                'https://open.tiktokapis.com/v1/user/info/',
                params={
                    'fields': 'open_id,display_name,avatar_large,follower_count,video_count,heart_count,bio_description,is_verified'
                },
                headers={'Authorization': f'Bearer {access_token}'},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                user_info = data.get('data', {}).get('user', {})
                
                return {
                    'platform': 'tiktok',
                    'followers': user_info.get('follower_count', 0),
                    'username': user_info.get('display_name', ''),
                    'video_count': user_info.get('video_count', 0),
                    'likes': user_info.get('heart_count', 0),
                    'bio': user_info.get('bio_description', ''),
                    'profile_picture_url': user_info.get('avatar_large', ''),
                    'is_verified': user_info.get('is_verified', False),
                }, None
            else:
                return {}, f"TikTok API error: {response.status_code}"
                
        except Exception as e:
            logger.error(f"TikTok metrics error: {e}")
            return {}, str(e)
    
    @staticmethod
    def get_facebook_metrics(access_token: str, page_id: str = None) -> Tuple[Dict, Optional[str]]:
        """Get Facebook page metrics (likes, followers)"""
        try:
            if page_id:
                response = requests.get(
                    f'https://graph.facebook.com/v18.0/{page_id}',
                    params={
                        'fields': 'id,name,fan_count,followers_count,description,picture,category,website',
                        'access_token': access_token
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    followers = data.get('followers_count') or data.get('fan_count') or 0
                    
                    return {
                        'platform': 'facebook',
                        'followers': followers,
                        'page_name': data.get('name', ''),
                        'page_id': data.get('id', ''),
                        'category': data.get('category', ''),
                        'bio': data.get('description', ''),
                        'profile_picture_url': data.get('picture', {}).get('data', {}).get('url', ''),
                        'website': data.get('website', ''),
                    }, None
            
            pages_response = requests.get(
                'https://graph.facebook.com/v18.0/me/accounts',
                params={
                    'fields': 'id,name,fan_count,followers_count,picture,category,access_token',
                    'access_token': access_token
                },
                timeout=10
            )
            
            if pages_response.status_code == 200:
                pages_data = pages_response.json()
                pages = pages_data.get('data', [])
                
                if pages:
                    page = pages[0]
                    followers = page.get('followers_count') or page.get('fan_count') or 0
                    
                    return {
                        'platform': 'facebook',
                        'followers': followers,
                        'page_name': page.get('name', ''),
                        'page_id': page.get('id', ''),
                        'category': page.get('category', ''),
                        'bio': '',
                        'profile_picture_url': page.get('picture', {}).get('data', {}).get('url', ''),
                        'website': '',
                        'all_pages': [{
                            'id': p.get('id'),
                            'name': p.get('name'),
                            'followers': p.get('followers_count') or p.get('fan_count') or 0
                        } for p in pages]
                    }, None
                else:
                    return {}, "No Facebook pages found for this account"
            else:
                error_data = pages_response.json() if pages_response.text else {}
                error_msg = error_data.get('error', {}).get('message', f'Status {pages_response.status_code}')
                return {}, f"Facebook API error: {error_msg}"
                
        except Exception as e:
            logger.error(f"Facebook metrics error: {e}")
            return {}, str(e)
    
    @staticmethod
    def get_all_social_metrics(company_id: int) -> Dict:
        """Get metrics from all connected social media accounts"""
        from models import InstagramOAuth, TikTokOAuth, FacebookOAuth
        
        result = {
            'instagram': [],
            'tiktok': [],
            'facebook': [],
            'total_followers': 0,
            'total_error': None
        }
        
        try:
            # Get Instagram metrics
            instagram_accs = InstagramOAuth.query.filter_by(company_id=company_id, status='active').all()
            for acc in instagram_accs:
                try:
                    access_token = acc.get_access_token()
                    if access_token:
                        metrics, error = SocialMediaMetrics.get_instagram_metrics(access_token)
                        if not error and metrics:
                            result['instagram'].append(metrics)
                            result['total_followers'] += metrics.get('followers', 0)
                except Exception as e:
                    logger.error(f"Error getting Instagram metrics for account {acc.id}: {e}")
            
            # Get TikTok metrics
            tiktok_accs = TikTokOAuth.query.filter_by(company_id=company_id, status='active').all()
            for acc in tiktok_accs:
                try:
                    access_token = acc.get_access_token()
                    if access_token:
                        metrics, error = SocialMediaMetrics.get_tiktok_metrics(access_token)
                        if not error and metrics:
                            result['tiktok'].append(metrics)
                            result['total_followers'] += metrics.get('followers', 0)
                except Exception as e:
                    logger.error(f"Error getting TikTok metrics for account {acc.id}: {e}")
            
            # Get Facebook metrics
            facebook_accs = FacebookOAuth.query.filter_by(company_id=company_id, status='active').all()
            for acc in facebook_accs:
                try:
                    access_token = acc.get_access_token()
                    page_id = getattr(acc, 'page_id', None)
                    if access_token:
                        metrics, error = SocialMediaMetrics.get_facebook_metrics(access_token, page_id)
                        if not error and metrics:
                            result['facebook'].append(metrics)
                            result['total_followers'] += metrics.get('followers', 0)
                        elif error:
                            logger.warning(f"Facebook metrics warning: {error}")
                except Exception as e:
                    logger.error(f"Error getting Facebook metrics for account {acc.id}: {e}")
        
        except Exception as e:
            logger.error(f"Error in get_all_social_metrics: {e}")
            result['total_error'] = str(e)
        
        return result
