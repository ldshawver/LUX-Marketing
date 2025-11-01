"""
Social Media Service - Phase 4
Handles multi-platform posting, scheduling, and cross-posting
"""

from datetime import datetime
from app import db
from models import SocialMediaAccount, SocialMediaSchedule, SocialMediaCrossPost
import logging

logger = logging.getLogger(__name__)

class SocialMediaService:
    @staticmethod
    def connect_account(platform, account_name, access_token, account_id=None):
        """Connect social media account"""
        try:
            account = SocialMediaAccount(
                platform=platform,
                account_name=account_name,
                account_id=account_id,
                access_token=access_token,
                is_verified=True
            )
            db.session.add(account)
            db.session.commit()
            return account
        except Exception as e:
            logger.error(f"Error connecting account: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def schedule_post(account_id, content, scheduled_for, media_urls=None, hashtags=None):
        """Schedule post for specific account"""
        try:
            post = SocialMediaSchedule(
                account_id=account_id,
                content=content,
                scheduled_for=scheduled_for,
                media_urls=media_urls or [],
                hashtags=hashtags
            )
            db.session.add(post)
            db.session.commit()
            return post
        except Exception as e:
            logger.error(f"Error scheduling post: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def create_cross_post(content, platforms, scheduled_for, media_urls=None):
        """Create cross-post for multiple platforms"""
        try:
            cross_post = SocialMediaCrossPost(
                content=content,
                platforms=platforms,
                scheduled_for=scheduled_for,
                media_urls=media_urls or []
            )
            db.session.add(cross_post)
            db.session.commit()
            return cross_post
        except Exception as e:
            logger.error(f"Error creating cross-post: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def publish_post(schedule_id):
        """Publish scheduled post"""
        try:
            post = SocialMediaSchedule.query.get(schedule_id)
            if not post:
                return None
            
            # In production, integrate with actual platform APIs
            # For now, simulate publishing
            post.status = 'published'
            post.posted_at = datetime.utcnow()
            post.post_id = f"post_{schedule_id}"
            post.engagement_metrics = {'likes': 0, 'comments': 0, 'shares': 0}
            
            db.session.commit()
            return post
        except Exception as e:
            logger.error(f"Error publishing post: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def get_upcoming_posts(days=7):
        """Get upcoming scheduled posts"""
        try:
            from datetime import timedelta
            end_date = datetime.utcnow() + timedelta(days=days)
            
            posts = SocialMediaSchedule.query.filter(
                SocialMediaSchedule.scheduled_for.between(datetime.utcnow(), end_date),
                SocialMediaSchedule.status == 'scheduled'
            ).order_by(SocialMediaSchedule.scheduled_for).all()
            
            return posts
        except Exception as e:
            logger.error(f"Error getting upcoming posts: {e}")
            return []
    
    @staticmethod
    def test_connection(account):
        """Test social media account connection"""
        try:
            platform = account.platform.lower()
            
            # Platform-specific connection tests
            if platform == 'twitter':
                return SocialMediaService._test_twitter_connection(account)
            elif platform == 'facebook':
                return SocialMediaService._test_facebook_connection(account)
            elif platform == 'instagram':
                return SocialMediaService._test_instagram_connection(account)
            elif platform == 'telegram':
                return SocialMediaService._test_telegram_connection(account)
            elif platform == 'tiktok':
                return SocialMediaService._test_tiktok_connection(account)
            elif platform == 'reddit':
                return SocialMediaService._test_reddit_connection(account)
            else:
                return {
                    'success': False,
                    'message': f'Platform {platform} not supported for connection testing yet'
                }
                
        except Exception as e:
            logger.error(f"Error testing connection for {account.platform}: {e}")
            return {
                'success': False,
                'message': f'Connection test error: {str(e)}'
            }
    
    @staticmethod
    def _test_twitter_connection(account):
        """Test Twitter/X API connection"""
        try:
            import os
            import requests
            
            # Use environment variable for bearer token if access_token not set
            bearer_token = account.access_token or os.getenv('TWITTER_BEARER_TOKEN')
            
            if not bearer_token:
                return {
                    'success': False,
                    'message': 'Twitter Bearer Token not configured'
                }
            
            # Test API call to verify credentials
            headers = {'Authorization': f'Bearer {bearer_token}'}
            response = requests.get('https://api.twitter.com/2/users/me', headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                user_data = data.get('data', {})
                return {
                    'success': True,
                    'message': 'Twitter connection successful!',
                    'details': f"Connected as @{user_data.get('username', 'unknown')}",
                    'account_info': user_data
                }
            else:
                return {
                    'success': False,
                    'message': f'Twitter API error: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Twitter connection test error: {e}")
            return {
                'success': False,
                'message': f'Twitter connection failed: {str(e)}'
            }
    
    @staticmethod
    def _test_facebook_connection(account):
        """Test Facebook API connection"""
        try:
            import requests
            
            if not account.access_token:
                return {
                    'success': False,
                    'message': 'Facebook Access Token not configured'
                }
            
            # Test API call
            response = requests.get(
                f'https://graph.facebook.com/v18.0/me',
                params={'access_token': account.access_token},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'message': 'Facebook connection successful!',
                    'details': f"Connected as {data.get('name', 'unknown')}",
                    'account_info': data
                }
            else:
                return {
                    'success': False,
                    'message': f'Facebook API error: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Facebook connection failed: {str(e)}'
            }
    
    @staticmethod
    def _test_instagram_connection(account):
        """Test Instagram API connection"""
        # Instagram uses Facebook Graph API
        return SocialMediaService._test_facebook_connection(account)
    
    @staticmethod
    def _test_telegram_connection(account):
        """Test Telegram Bot API connection"""
        try:
            import requests
            
            if not account.access_token:
                return {
                    'success': False,
                    'message': 'Telegram Bot Token not configured'
                }
            
            # Test API call
            response = requests.get(
                f'https://api.telegram.org/bot{account.access_token}/getMe',
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    bot_info = data.get('result', {})
                    return {
                        'success': True,
                        'message': 'Telegram bot connection successful!',
                        'details': f"Connected as @{bot_info.get('username', 'unknown')}",
                        'account_info': bot_info
                    }
            
            return {
                'success': False,
                'message': 'Telegram API returned error'
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'Telegram connection failed: {str(e)}'
            }
    
    @staticmethod
    def _test_tiktok_connection(account):
        """Test TikTok API connection"""
        # TikTok API testing - placeholder for now
        return {
            'success': True,
            'message': 'TikTok connection testing not yet implemented',
            'details': 'API integration coming soon'
        }
    
    @staticmethod
    def _test_reddit_connection(account):
        """Test Reddit API connection"""
        try:
            import requests
            
            if not account.access_token:
                return {
                    'success': False,
                    'message': 'Reddit Access Token not configured'
                }
            
            # Test API call
            headers = {
                'Authorization': f'Bearer {account.access_token}',
                'User-Agent': 'LUXMarketing/1.0'
            }
            response = requests.get(
                'https://oauth.reddit.com/api/v1/me',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'message': 'Reddit connection successful!',
                    'details': f"Connected as u/{data.get('name', 'unknown')}",
                    'account_info': data
                }
            else:
                return {
                    'success': False,
                    'message': f'Reddit API error: {response.status_code}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f'Reddit connection failed: {str(e)}'
            }
    
    @staticmethod
    def refresh_account_data(account):
        """Refresh account data (followers, etc.)"""
        try:
            platform = account.platform.lower()
            
            # Platform-specific data refresh
            if platform == 'twitter':
                return SocialMediaService._refresh_twitter_data(account)
            elif platform == 'facebook':
                return SocialMediaService._refresh_facebook_data(account)
            elif platform == 'instagram':
                return SocialMediaService._refresh_instagram_data(account)
            elif platform == 'telegram':
                return {'success': True, 'message': 'Telegram bots do not have follower counts'}
            else:
                return {
                    'success': False,
                    'message': f'Data refresh not implemented for {platform}'
                }
                
        except Exception as e:
            logger.error(f"Error refreshing data for {account.platform}: {e}")
            return {
                'success': False,
                'message': f'Refresh error: {str(e)}'
            }
    
    @staticmethod
    def _refresh_twitter_data(account):
        """Refresh Twitter follower count"""
        try:
            import os
            import requests
            
            bearer_token = account.access_token or os.getenv('TWITTER_BEARER_TOKEN')
            
            if not bearer_token:
                return {'success': False, 'message': 'Twitter token not configured'}
            
            headers = {'Authorization': f'Bearer {bearer_token}'}
            response = requests.get(
                'https://api.twitter.com/2/users/me?user.fields=public_metrics',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                metrics = data.get('data', {}).get('public_metrics', {})
                follower_count = metrics.get('followers_count', 0)
                
                return {
                    'success': True,
                    'follower_count': follower_count
                }
            else:
                return {'success': False, 'message': 'Failed to fetch Twitter data'}
                
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def _refresh_facebook_data(account):
        """Refresh Facebook follower count"""
        try:
            import requests
            
            if not account.access_token:
                return {'success': False, 'message': 'Facebook token not configured'}
            
            response = requests.get(
                f'https://graph.facebook.com/v18.0/me',
                params={'fields': 'followers_count', 'access_token': account.access_token},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'follower_count': data.get('followers_count', 0)
                }
            else:
                return {'success': False, 'message': 'Failed to fetch Facebook data'}
                
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def _refresh_instagram_data(account):
        """Refresh Instagram follower count"""
        # Instagram uses Facebook Graph API
        return SocialMediaService._refresh_facebook_data(account)
