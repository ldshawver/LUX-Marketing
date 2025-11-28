"""WordPress API integration service"""
import requests
import logging
from models import WordPressIntegration

logger = logging.getLogger(__name__)

class WordPressService:
    """Handle WordPress site connections and data sync"""
    
    @staticmethod
    def test_connection(site_url, api_key):
        """Test WordPress API connection"""
        try:
            # Normalize URL
            if not site_url.startswith('http'):
                site_url = 'https://' + site_url
            if site_url.endswith('/'):
                site_url = site_url[:-1]
            
            # Test basic connection
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f'{site_url}/wp-json/wp/v2/posts',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return {'success': True, 'message': 'Connected successfully', 'posts_count': len(response.json())}
            else:
                return {'success': False, 'message': f'Connection failed: {response.status_code}'}
                
        except requests.exceptions.Timeout:
            return {'success': False, 'message': 'Connection timeout - site may be down'}
        except requests.exceptions.ConnectionError:
            return {'success': False, 'message': 'Cannot reach site - check URL'}
        except Exception as e:
            logger.error(f'WordPress connection error: {e}')
            return {'success': False, 'message': f'Error: {str(e)}'}

    @staticmethod
    def get_posts(site_url, api_key):
        """Fetch blog posts from WordPress"""
        try:
            if not site_url.startswith('http'):
                site_url = 'https://' + site_url
            if site_url.endswith('/'):
                site_url = site_url[:-1]
            
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f'{site_url}/wp-json/wp/v2/posts?per_page=100',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return {'success': True, 'posts': response.json()}
            else:
                return {'success': False, 'message': 'Failed to fetch posts'}
                
        except Exception as e:
            logger.error(f'WordPress fetch posts error: {e}')
            return {'success': False, 'message': str(e)}

    @staticmethod
    def get_products(site_url, api_key):
        """Fetch WooCommerce products from WordPress"""
        try:
            if not site_url.startswith('http'):
                site_url = 'https://' + site_url
            if site_url.endswith('/'):
                site_url = site_url[:-1]
            
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                f'{site_url}/wp-json/wc/v3/products?per_page=100',
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return {'success': True, 'products': response.json()}
            else:
                return {'success': False, 'message': 'Failed to fetch products'}
                
        except Exception as e:
            logger.error(f'WordPress fetch products error: {e}')
            return {'success': False, 'message': str(e)}

print("✓ WordPress service loaded")
