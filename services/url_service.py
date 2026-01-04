"""
URL Service for Social Media Posts
Handles URL shortening and pretty URL creation
"""

import os
import re
import requests
import hashlib
import logging
from typing import Optional, Tuple
from urllib.parse import urlparse, quote

logger = logging.getLogger(__name__)


class URLService:
    """URL shortening and management for social media posts"""
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Check if URL is valid"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    @staticmethod
    def shorten_tinyurl(url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Shorten URL using TinyURL (free, no API key required)
        Returns (shortened_url, error)
        """
        try:
            if not URLService.is_valid_url(url):
                return None, "Invalid URL format"
            
            response = requests.get(
                f'https://tinyurl.com/api-create.php?url={quote(url, safe="")}',
                timeout=10
            )
            
            if response.status_code == 200 and response.text.startswith('http'):
                return response.text, None
            else:
                return None, "TinyURL service error"
                
        except Exception as e:
            logger.error(f"TinyURL error: {e}")
            return None, str(e)
    
    @staticmethod
    def shorten_bitly(url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Shorten URL using Bitly (requires BITLY_ACCESS_TOKEN)
        Returns (shortened_url, error)
        """
        try:
            access_token = os.environ.get('BITLY_ACCESS_TOKEN')
            if not access_token:
                return URLService.shorten_tinyurl(url)
            
            if not URLService.is_valid_url(url):
                return None, "Invalid URL format"
            
            response = requests.post(
                'https://api-ssl.bitly.com/v4/shorten',
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                },
                json={'long_url': url},
                timeout=10
            )
            
            if response.status_code == 200 or response.status_code == 201:
                data = response.json()
                return data.get('link'), None
            else:
                error_data = response.json()
                return None, error_data.get('message', f"Bitly API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Bitly error: {e}")
            return None, str(e)
    
    @staticmethod
    def shorten_url(url: str, service: str = 'auto') -> Tuple[Optional[str], Optional[str]]:
        """
        Shorten URL using preferred service
        service: 'auto', 'tinyurl', or 'bitly'
        """
        if service == 'bitly':
            return URLService.shorten_bitly(url)
        elif service == 'tinyurl':
            return URLService.shorten_tinyurl(url)
        else:
            if os.environ.get('BITLY_ACCESS_TOKEN'):
                return URLService.shorten_bitly(url)
            return URLService.shorten_tinyurl(url)
    
    @staticmethod
    def create_pretty_url(url: str, title: Optional[str] = None) -> str:
        """
        Create a pretty/display version of a URL
        Formats long URLs into readable format with optional title
        """
        if not url:
            return ""
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.replace('www.', '')
            
            if title:
                return f"{title} ({domain})"
            
            path = parsed.path.strip('/')
            if len(path) > 30:
                path = path[:27] + '...'
            
            if path:
                return f"{domain}/{path}"
            return domain
            
        except:
            return url[:50] + '...' if len(url) > 50 else url
    
    @staticmethod
    def extract_urls(text: str) -> list:
        """Extract all URLs from text"""
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        return re.findall(url_pattern, text)
    
    @staticmethod
    def replace_urls_with_shortened(text: str, shorten_all: bool = True) -> Tuple[str, list]:
        """
        Replace URLs in text with shortened versions
        Returns (modified_text, list of (original, shortened) tuples)
        """
        urls = URLService.extract_urls(text)
        replacements = []
        
        for url in urls:
            if shorten_all or len(url) > 50:
                shortened, error = URLService.shorten_url(url)
                if shortened:
                    text = text.replace(url, shortened)
                    replacements.append((url, shortened))
        
        return text, replacements
