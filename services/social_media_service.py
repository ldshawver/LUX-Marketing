"""Social Media API Integration Service for all platforms"""
import requests
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SocialMediaService:
    """Unified social media API handler for all platforms"""
    
    # Platform API configs
    PLATFORMS = {
        'facebook': {
            'api_url': 'https://graph.facebook.com/v18.0',
            'requires': ['access_token']
        },
        'instagram': {
            'api_url': 'https://graph.instagram.com/v18.0',
            'requires': ['access_token']
        },
        'tiktok': {
            'api_url': 'https://open.tiktokapis.com/v1',
            'requires': ['access_token']
        },
        'youtube': {
            'api_url': 'https://www.googleapis.com/youtube/v3',
            'requires': ['access_token']
        },
        'reddit': {
            'api_url': 'https://oauth.reddit.com',
            'requires': ['access_token', 'refresh_token']
        },
        'snapchat': {
            'api_url': 'https://adsapi.snapchat.com/v1',
            'requires': ['access_token']
        }
    }
    
    @staticmethod
    def test_connection(platform, credentials):
        """Test if API credentials are valid"""
        try:
            if platform == 'facebook':
                return SocialMediaService._test_facebook(credentials)
            elif platform == 'instagram':
                return SocialMediaService._test_instagram(credentials)
            elif platform == 'tiktok':
                return SocialMediaService._test_tiktok(credentials)
            elif platform == 'youtube':
                return SocialMediaService._test_youtube(credentials)
            elif platform == 'reddit':
                return SocialMediaService._test_reddit(credentials)
            elif platform == 'snapchat':
                return SocialMediaService._test_snapchat(credentials)
            return {'success': False, 'message': f'Unknown platform: {platform}'}
        except Exception as e:
            logger.error(f"Connection test error for {platform}: {e}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def _test_facebook(credentials):
        """Test Facebook connection"""
        try:
            access_token = credentials.get('access_token')
            if not access_token:
                return {'success': False, 'message': 'Access token required'}
            
            response = requests.get(
                'https://graph.facebook.com/v18.0/me',
                params={'access_token': access_token}
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'account_name': data.get('name'),
                    'account_id': data.get('id'),
                    'message': 'Facebook connection successful'
                }
            else:
                return {'success': False, 'message': f'Facebook API error: {response.json()}'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def _test_instagram(credentials):
        """Test Instagram connection"""
        try:
            access_token = credentials.get('access_token')
            if not access_token:
                return {'success': False, 'message': 'Access token required'}
            
            response = requests.get(
                'https://graph.instagram.com/v18.0/me',
                params={'fields': 'id,username,name', 'access_token': access_token}
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'account_name': data.get('username'),
                    'account_id': data.get('id'),
                    'message': 'Instagram connection successful'
                }
            else:
                return {'success': False, 'message': f'Instagram API error: {response.json()}'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def _test_tiktok(credentials):
        """Test TikTok connection"""
        try:
            access_token = credentials.get('access_token')
            if not access_token:
                return {'success': False, 'message': 'Access token required'}
            
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(
                'https://open.tiktokapis.com/v1/user/info/',
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('data'):
                    user = data['data'].get('user', {})
                    return {
                        'success': True,
                        'account_name': user.get('display_name'),
                        'account_id': user.get('open_id'),
                        'message': 'TikTok connection successful'
                    }
            return {'success': False, 'message': 'TikTok API error'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def _test_youtube(credentials):
        """Test YouTube connection"""
        try:
            access_token = credentials.get('access_token')
            if not access_token:
                return {'success': False, 'message': 'Access token required'}
            
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(
                'https://www.googleapis.com/youtube/v3/channels',
                params={'part': 'snippet', 'mine': 'true'},
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('items'):
                    channel = data['items'][0]
                    return {
                        'success': True,
                        'account_name': channel.get('snippet', {}).get('title'),
                        'account_id': channel.get('id'),
                        'message': 'YouTube connection successful'
                    }
            return {'success': False, 'message': 'YouTube API error'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def _test_reddit(credentials):
        """Test Reddit connection"""
        try:
            access_token = credentials.get('access_token')
            if not access_token:
                return {'success': False, 'message': 'Access token required'}
            
            headers = {'Authorization': f'Bearer {access_token}', 'User-Agent': 'LUX/1.0'}
            response = requests.get(
                'https://oauth.reddit.com/api/v1/me',
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'account_name': data.get('name'),
                    'account_id': data.get('id'),
                    'message': 'Reddit connection successful'
                }
            return {'success': False, 'message': 'Reddit API error'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def _test_snapchat(credentials):
        """Test Snapchat connection"""
        try:
            access_token = credentials.get('access_token')
            if not access_token:
                return {'success': False, 'message': 'Access token required'}
            
            headers = {'Authorization': f'Bearer {access_token}'}
            response = requests.get(
                'https://adsapi.snapchat.com/v1/me',
                headers=headers
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'account_name': 'Snapchat Account',
                    'message': 'Snapchat connection successful'
                }
            return {'success': False, 'message': 'Snapchat API error'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def refresh_account_data(account):
        """Refresh follower count and data for an account"""
        try:
            platform = account.platform.lower()
            credentials = {
                'access_token': account.access_token,
                'refresh_token': account.refresh_token
            }
            
            if platform == 'facebook':
                return SocialMediaService._get_facebook_stats(credentials)
            elif platform == 'instagram':
                return SocialMediaService._get_instagram_stats(credentials)
            elif platform == 'tiktok':
                return SocialMediaService._get_tiktok_stats(credentials)
            elif platform == 'youtube':
                return SocialMediaService._get_youtube_stats(credentials)
            elif platform == 'reddit':
                return SocialMediaService._get_reddit_stats(credentials)
            elif platform == 'snapchat':
                return SocialMediaService._get_snapchat_stats(credentials)
            
            return {'success': False, 'message': f'Unknown platform: {platform}'}
        except Exception as e:
            logger.error(f"Error refreshing {account.platform}: {e}")
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def _get_facebook_stats(credentials):
        """Get Facebook page stats"""
        try:
            response = requests.get(
                'https://graph.facebook.com/v18.0/me',
                params={'fields': 'followers_count', 'access_token': credentials['access_token']}
            )
            if response.status_code == 200:
                return {'success': True, 'follower_count': response.json().get('followers_count', 0)}
            return {'success': False, 'message': 'Failed to get stats'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def _get_instagram_stats(credentials):
        """Get Instagram account stats"""
        try:
            response = requests.get(
                'https://graph.instagram.com/v18.0/me',
                params={'fields': 'followers_count', 'access_token': credentials['access_token']}
            )
            if response.status_code == 200:
                return {'success': True, 'follower_count': response.json().get('followers_count', 0)}
            return {'success': False, 'message': 'Failed to get stats'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def _get_tiktok_stats(credentials):
        """Get TikTok account stats"""
        try:
            headers = {'Authorization': f'Bearer {credentials["access_token"]}'}
            response = requests.get(
                'https://open.tiktokapis.com/v1/user/info/',
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('data', {}).get('user'):
                    follower_count = data['data']['user'].get('follower_count', 0)
                    return {'success': True, 'follower_count': follower_count}
            return {'success': False, 'message': 'Failed to get stats'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def _get_youtube_stats(credentials):
        """Get YouTube channel stats"""
        try:
            headers = {'Authorization': f'Bearer {credentials["access_token"]}'}
            response = requests.get(
                'https://www.googleapis.com/youtube/v3/channels',
                params={'part': 'statistics', 'mine': 'true'},
                headers=headers
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('items'):
                    stats = data['items'][0].get('statistics', {})
                    return {'success': True, 'follower_count': int(stats.get('subscriberCount', 0))}
            return {'success': False, 'message': 'Failed to get stats'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def _get_reddit_stats(credentials):
        """Get Reddit user stats"""
        try:
            headers = {'Authorization': f'Bearer {credentials["access_token"]}', 'User-Agent': 'LUX/1.0'}
            response = requests.get(
                'https://oauth.reddit.com/api/v1/me',
                headers=headers
            )
            if response.status_code == 200:
                return {'success': True, 'follower_count': response.json().get('link_karma', 0)}
            return {'success': False, 'message': 'Failed to get stats'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def _get_snapchat_stats(credentials):
        """Get Snapchat stats"""
        try:
            headers = {'Authorization': f'Bearer {credentials["access_token"]}'}
            response = requests.get(
                'https://adsapi.snapchat.com/v1/me',
                headers=headers
            )
            if response.status_code == 200:
                return {'success': True, 'follower_count': 0}  # Snapchat doesn't expose follower count via API
            return {'success': False, 'message': 'Failed to get stats'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
