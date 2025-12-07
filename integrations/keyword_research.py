"""
Keyword Research Integrations
Supports DataForSEO, SEMrush, and Moz APIs
"""

import os
import logging
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class DataForSEOClient:
    """DataForSEO API Client - Affordable keyword research data"""
    
    BASE_URL = "https://api.dataforseo.com/v3"
    
    def __init__(self, login: str = None, password: str = None):
        self.login = login or os.getenv('DATAFORSEO_LOGIN')
        self.password = password or os.getenv('DATAFORSEO_PASSWORD')
        self.auth = (self.login, self.password) if self.login and self.password else None
    
    def is_configured(self) -> bool:
        return self.auth is not None
    
    def get_keyword_data(self, keywords: List[str], location_code: int = 2840, language_code: str = "en") -> Tuple[List[Dict], Optional[str]]:
        """Get keyword data including search volume, CPC, competition"""
        if not self.is_configured():
            return [], "DataForSEO credentials not configured"
        
        try:
            payload = [{
                "keywords": keywords,
                "location_code": location_code,
                "language_code": language_code
            }]
            
            response = requests.post(
                f"{self.BASE_URL}/keywords_data/google_ads/search_volume/live",
                json=payload,
                auth=self.auth,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('tasks') and data['tasks'][0].get('result'):
                    results = []
                    for item in data['tasks'][0]['result']:
                        results.append({
                            'keyword': item.get('keyword'),
                            'search_volume': item.get('search_volume', 0),
                            'cpc': item.get('cpc', 0),
                            'competition': item.get('competition', 0),
                            'competition_level': item.get('competition_level', 'unknown'),
                            'low_top_of_page_bid': item.get('low_top_of_page_bid'),
                            'high_top_of_page_bid': item.get('high_top_of_page_bid')
                        })
                    return results, None
                return [], "No results found"
            else:
                return [], f"API error: {response.status_code}"
        except Exception as e:
            logger.error(f"DataForSEO error: {e}")
            return [], str(e)
    
    def get_keyword_suggestions(self, seed_keyword: str, location_code: int = 2840) -> Tuple[List[Dict], Optional[str]]:
        """Get related keyword suggestions"""
        if not self.is_configured():
            return [], "DataForSEO credentials not configured"
        
        try:
            payload = [{
                "keyword": seed_keyword,
                "location_code": location_code,
                "language_code": "en",
                "include_seed_keyword": True,
                "limit": 50
            }]
            
            response = requests.post(
                f"{self.BASE_URL}/keywords_data/google_ads/keywords_for_keywords/live",
                json=payload,
                auth=self.auth,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('tasks') and data['tasks'][0].get('result'):
                    results = []
                    for item in data['tasks'][0]['result']:
                        results.append({
                            'keyword': item.get('keyword'),
                            'search_volume': item.get('search_volume', 0),
                            'cpc': item.get('cpc', 0),
                            'competition': item.get('competition', 0)
                        })
                    return results, None
                return [], "No suggestions found"
            else:
                return [], f"API error: {response.status_code}"
        except Exception as e:
            logger.error(f"DataForSEO suggestion error: {e}")
            return [], str(e)


class SEMrushClient:
    """SEMrush API Client - Premium keyword and competitor data"""
    
    BASE_URL = "https://api.semrush.com"
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('SEMRUSH_API_KEY')
    
    def is_configured(self) -> bool:
        return self.api_key is not None
    
    def get_keyword_overview(self, keyword: str, database: str = "us") -> Tuple[Dict, Optional[str]]:
        """Get keyword overview including volume, difficulty, CPC"""
        if not self.is_configured():
            return {}, "SEMrush API key not configured"
        
        try:
            params = {
                'type': 'phrase_this',
                'key': self.api_key,
                'phrase': keyword,
                'database': database,
                'export_columns': 'Ph,Nq,Cp,Co,Nr,Td'
            }
            
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            
            if response.status_code == 200:
                lines = response.text.strip().split('\n')
                if len(lines) >= 2:
                    headers = lines[0].split(';')
                    values = lines[1].split(';')
                    result = dict(zip(headers, values))
                    return {
                        'keyword': result.get('Keyword', keyword),
                        'search_volume': int(result.get('Search Volume', 0)),
                        'cpc': float(result.get('CPC', 0)),
                        'competition': float(result.get('Competition', 0)),
                        'results': int(result.get('Number of Results', 0)),
                        'difficulty': int(result.get('Keyword Difficulty', 0))
                    }, None
                return {}, "No data found"
            else:
                return {}, f"API error: {response.status_code}"
        except Exception as e:
            logger.error(f"SEMrush error: {e}")
            return {}, str(e)
    
    def get_related_keywords(self, keyword: str, database: str = "us", limit: int = 50) -> Tuple[List[Dict], Optional[str]]:
        """Get related keywords"""
        if not self.is_configured():
            return [], "SEMrush API key not configured"
        
        try:
            params = {
                'type': 'phrase_related',
                'key': self.api_key,
                'phrase': keyword,
                'database': database,
                'export_columns': 'Ph,Nq,Cp,Co,Nr,Td',
                'display_limit': limit
            }
            
            response = requests.get(self.BASE_URL, params=params, timeout=30)
            
            if response.status_code == 200:
                lines = response.text.strip().split('\n')
                results = []
                if len(lines) >= 2:
                    headers = lines[0].split(';')
                    for line in lines[1:]:
                        values = line.split(';')
                        if len(values) >= len(headers):
                            data = dict(zip(headers, values))
                            results.append({
                                'keyword': data.get('Keyword', ''),
                                'search_volume': int(data.get('Search Volume', 0)),
                                'cpc': float(data.get('CPC', 0)),
                                'competition': float(data.get('Competition', 0))
                            })
                return results, None
            else:
                return [], f"API error: {response.status_code}"
        except Exception as e:
            logger.error(f"SEMrush related keywords error: {e}")
            return [], str(e)


class MozClient:
    """Moz API Client - Domain authority and keyword difficulty"""
    
    BASE_URL = "https://lsapi.seomoz.com/v2"
    
    def __init__(self, access_id: str = None, secret_key: str = None):
        self.access_id = access_id or os.getenv('MOZ_ACCESS_ID')
        self.secret_key = secret_key or os.getenv('MOZ_SECRET_KEY')
    
    def is_configured(self) -> bool:
        return self.access_id is not None and self.secret_key is not None
    
    def get_url_metrics(self, url: str) -> Tuple[Dict, Optional[str]]:
        """Get domain/URL authority metrics"""
        if not self.is_configured():
            return {}, "Moz credentials not configured"
        
        try:
            payload = {
                "targets": [url]
            }
            
            response = requests.post(
                f"{self.BASE_URL}/url_metrics",
                json=payload,
                auth=(self.access_id, self.secret_key),
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('results'):
                    result = data['results'][0]
                    return {
                        'domain_authority': result.get('domain_authority', 0),
                        'page_authority': result.get('page_authority', 0),
                        'spam_score': result.get('spam_score', 0),
                        'linking_domains': result.get('root_domains_to_root_domain', 0),
                        'inbound_links': result.get('external_links_to_root_domain', 0)
                    }, None
                return {}, "No metrics found"
            else:
                return {}, f"API error: {response.status_code}"
        except Exception as e:
            logger.error(f"Moz error: {e}")
            return {}, str(e)
    
    def get_keyword_difficulty(self, keyword: str) -> Tuple[Dict, Optional[str]]:
        """Get keyword difficulty score"""
        if not self.is_configured():
            return {}, "Moz credentials not configured"
        
        try:
            payload = {
                "keyword": keyword
            }
            
            response = requests.post(
                f"{self.BASE_URL}/keyword_difficulty",
                json=payload,
                auth=(self.access_id, self.secret_key),
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'keyword': keyword,
                    'difficulty': data.get('difficulty', 0),
                    'opportunity': data.get('opportunity', 0),
                    'potential': data.get('potential', 0)
                }, None
            else:
                return {}, f"API error: {response.status_code}"
        except Exception as e:
            logger.error(f"Moz keyword difficulty error: {e}")
            return {}, str(e)


class KeywordResearchService:
    """Unified keyword research service using multiple providers"""
    
    def __init__(self, company_id: int = None):
        self.company_id = company_id
        self.dataforseo = DataForSEOClient()
        self.semrush = SEMrushClient()
        self.moz = MozClient()
        
        if company_id:
            self._load_company_credentials(company_id)
    
    def _load_company_credentials(self, company_id: int):
        """Load API credentials from company secrets"""
        try:
            from models import CompanySecret
            
            secrets = CompanySecret.query.filter_by(company_id=company_id).all()
            creds = {s.key: s.value for s in secrets}
            
            if creds.get('dataforseo_login') and creds.get('dataforseo_password'):
                self.dataforseo = DataForSEOClient(
                    login=creds['dataforseo_login'],
                    password=creds['dataforseo_password']
                )
            
            if creds.get('semrush_api_key'):
                self.semrush = SEMrushClient(api_key=creds['semrush_api_key'])
            
            if creds.get('moz_access_id') and creds.get('moz_secret_key'):
                self.moz = MozClient(
                    access_id=creds['moz_access_id'],
                    secret_key=creds['moz_secret_key']
                )
        except Exception as e:
            logger.error(f"Error loading company credentials: {e}")
    
    def get_available_providers(self) -> List[str]:
        """Get list of configured providers"""
        providers = []
        if self.dataforseo.is_configured():
            providers.append('dataforseo')
        if self.semrush.is_configured():
            providers.append('semrush')
        if self.moz.is_configured():
            providers.append('moz')
        return providers
    
    def research_keyword(self, keyword: str, provider: str = 'auto') -> Dict[str, Any]:
        """Research a keyword using available providers"""
        result = {
            'keyword': keyword,
            'search_volume': None,
            'cpc': None,
            'competition': None,
            'difficulty': None,
            'suggestions': [],
            'provider': None,
            'error': None
        }
        
        if provider == 'auto':
            if self.dataforseo.is_configured():
                provider = 'dataforseo'
            elif self.semrush.is_configured():
                provider = 'semrush'
            else:
                result['error'] = 'No keyword research provider configured'
                return result
        
        if provider == 'dataforseo' and self.dataforseo.is_configured():
            data, error = self.dataforseo.get_keyword_data([keyword])
            if data and not error:
                kw_data = data[0]
                result.update({
                    'search_volume': kw_data.get('search_volume'),
                    'cpc': kw_data.get('cpc'),
                    'competition': kw_data.get('competition'),
                    'provider': 'dataforseo'
                })
            else:
                result['error'] = error
                
        elif provider == 'semrush' and self.semrush.is_configured():
            data, error = self.semrush.get_keyword_overview(keyword)
            if data and not error:
                result.update({
                    'search_volume': data.get('search_volume'),
                    'cpc': data.get('cpc'),
                    'competition': data.get('competition'),
                    'difficulty': data.get('difficulty'),
                    'provider': 'semrush'
                })
            else:
                result['error'] = error
        
        if self.moz.is_configured() and not result.get('difficulty'):
            moz_data, _ = self.moz.get_keyword_difficulty(keyword)
            if moz_data:
                result['difficulty'] = moz_data.get('difficulty')
        
        return result
    
    def get_keyword_suggestions(self, seed_keyword: str, limit: int = 50) -> Tuple[List[Dict], Optional[str]]:
        """Get keyword suggestions from available provider"""
        if self.dataforseo.is_configured():
            return self.dataforseo.get_keyword_suggestions(seed_keyword)
        elif self.semrush.is_configured():
            return self.semrush.get_related_keywords(seed_keyword, limit=limit)
        else:
            return [], "No keyword research provider configured"
