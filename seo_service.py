"""
SEO Analysis Service
Provides website crawling, meta analysis, and SEO recommendations.
"""

import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import re
import ipaddress
import socket

logger = logging.getLogger(__name__)


class SEOService:
    """Service to handle SEO analysis and recommendations."""
    
    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (compatible; LUX-SEO-Bot/1.0)'
    
    def _is_safe_url(self, url):
        """
        Validate that the URL doesn't point to private/internal networks.
        Prevents SSRF attacks.
        """
        try:
            parsed = urlparse(url)
            
            # Ensure scheme is http or https only
            if parsed.scheme not in ['http', 'https']:
                logger.warning(f"Rejected non-HTTP(S) URL: {url}")
                return False
            
            # Get hostname
            hostname = parsed.hostname
            if not hostname:
                return False
            
            # Block localhost variations
            if hostname.lower() in ['localhost', '127.0.0.1', '::1', '0.0.0.0']:
                logger.warning(f"Rejected localhost URL: {url}")
                return False
            
            # Resolve hostname to IP and check if it's private
            try:
                ip = socket.gethostbyname(hostname)
                ip_obj = ipaddress.ip_address(ip)
                
                # Block private, loopback, link-local, and multicast addresses
                if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_multicast:
                    logger.warning(f"Rejected private/internal IP {ip} for URL: {url}")
                    return False
            except (socket.gaierror, ValueError) as e:
                logger.warning(f"DNS resolution failed for {hostname}: {e}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"URL validation error: {e}")
            return False
    
    def analyze_page(self, url):
        """
        Analyze a single page for SEO factors.
        
        Args:
            url: The URL to analyze
            
        Returns:
            Dictionary containing SEO analysis results
        """
        try:
            # Validate URL for security
            if not self._is_safe_url(url):
                return {
                    'success': False,
                    'error': 'Invalid or unsafe URL. Cannot analyze internal/private network addresses.'
                }
            
            response = requests.get(url, headers={'User-Agent': self.user_agent}, timeout=10, allow_redirects=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            analysis = {
                'url': url,
                'status_code': response.status_code,
                'title': self._get_title(soup),
                'meta_description': self._get_meta_description(soup),
                'headings': self._get_headings(soup),
                'images': self._get_images(soup),
                'links': self._get_links(soup, url),
                'word_count': self._get_word_count(soup),
                'recommendations': []
            }
            
            # Generate recommendations
            analysis['recommendations'] = self._generate_recommendations(analysis)
            
            return {
                'success': True,
                'data': analysis
            }
            
        except requests.RequestException as e:
            logger.error(f"Error analyzing page {url}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_title(self, soup):
        """Extract page title."""
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
            return {
                'text': title,
                'length': len(title),
                'optimal': 50 <= len(title) <= 60
            }
        return None
    
    def _get_meta_description(self, soup):
        """Extract meta description."""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            desc = meta_desc.get('content').strip()
            return {
                'text': desc,
                'length': len(desc),
                'optimal': 150 <= len(desc) <= 160
            }
        return None
    
    def _get_headings(self, soup):
        """Extract all heading tags."""
        headings = {
            'h1': [],
            'h2': [],
            'h3': [],
            'h4': [],
            'h5': [],
            'h6': []
        }
        
        for level in range(1, 7):
            tags = soup.find_all(f'h{level}')
            headings[f'h{level}'] = [tag.get_text().strip() for tag in tags]
        
        return headings
    
    def _get_images(self, soup):
        """Analyze images for SEO."""
        images = soup.find_all('img')
        total = len(images)
        missing_alt = len([img for img in images if not img.get('alt')])
        
        return {
            'total': total,
            'missing_alt': missing_alt,
            'alt_coverage': ((total - missing_alt) / total * 100) if total > 0 else 0
        }
    
    def _get_links(self, soup, base_url):
        """Analyze links."""
        links = soup.find_all('a', href=True)
        internal = 0
        external = 0
        
        parsed_base = urlparse(base_url)
        
        for link in links:
            href = link.get('href')
            parsed_href = urlparse(urljoin(base_url, href))
            
            if parsed_href.netloc == parsed_base.netloc or not parsed_href.netloc:
                internal += 1
            else:
                external += 1
        
        return {
            'total': len(links),
            'internal': internal,
            'external': external
        }
    
    def _get_word_count(self, soup):
        """Count words in main content."""
        # Remove script and style elements
        for script in soup(['script', 'style', 'nav', 'footer', 'header']):
            script.decompose()
        
        text = soup.get_text()
        words = re.findall(r'\b\w+\b', text)
        return len(words)
    
    def _generate_recommendations(self, analysis):
        """Generate SEO recommendations based on analysis."""
        recommendations = []
        
        # Title recommendations
        if not analysis['title']:
            recommendations.append({
                'type': 'error',
                'category': 'Title',
                'message': 'Missing page title. Add a unique, descriptive title tag.'
            })
        elif not analysis['title']['optimal']:
            if analysis['title']['length'] < 50:
                recommendations.append({
                    'type': 'warning',
                    'category': 'Title',
                    'message': f"Title is too short ({analysis['title']['length']} chars). Aim for 50-60 characters."
                })
            elif analysis['title']['length'] > 60:
                recommendations.append({
                    'type': 'warning',
                    'category': 'Title',
                    'message': f"Title is too long ({analysis['title']['length']} chars). Keep it under 60 characters."
                })
        
        # Meta description recommendations
        if not analysis['meta_description']:
            recommendations.append({
                'type': 'error',
                'category': 'Meta Description',
                'message': 'Missing meta description. Add a compelling description (150-160 chars).'
            })
        elif not analysis['meta_description']['optimal']:
            recommendations.append({
                'type': 'warning',
                'category': 'Meta Description',
                'message': f"Meta description length is {analysis['meta_description']['length']} chars. Aim for 150-160."
            })
        
        # Heading recommendations
        h1_count = len(analysis['headings']['h1'])
        if h1_count == 0:
            recommendations.append({
                'type': 'error',
                'category': 'Headings',
                'message': 'No H1 heading found. Every page should have exactly one H1.'
            })
        elif h1_count > 1:
            recommendations.append({
                'type': 'warning',
                'category': 'Headings',
                'message': f'Multiple H1 headings found ({h1_count}). Use only one H1 per page.'
            })
        
        # Image recommendations
        if analysis['images']['missing_alt'] > 0:
            recommendations.append({
                'type': 'warning',
                'category': 'Images',
                'message': f"{analysis['images']['missing_alt']} images missing alt text. Add descriptive alt attributes."
            })
        
        # Content recommendations
        if analysis['word_count'] < 300:
            recommendations.append({
                'type': 'warning',
                'category': 'Content',
                'message': f"Low word count ({analysis['word_count']} words). Aim for at least 300 words."
            })
        
        # Link recommendations
        if analysis['links']['external'] == 0:
            recommendations.append({
                'type': 'info',
                'category': 'Links',
                'message': 'No external links found. Consider linking to authoritative sources.'
            })
        
        if not recommendations:
            recommendations.append({
                'type': 'success',
                'category': 'Overall',
                'message': 'Great job! No critical SEO issues found.'
            })
        
        return recommendations


# Create global instance
seo_service = SEOService()
