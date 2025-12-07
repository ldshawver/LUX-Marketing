"""
Event Integrations
Supports Eventbrite and Ticketmaster APIs
"""

import os
import logging
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class EventbriteClient:
    """Eventbrite API Client - Local events and ticketing"""
    
    BASE_URL = "https://www.eventbriteapi.com/v3"
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('EVENTBRITE_API_KEY')
    
    def is_configured(self) -> bool:
        return self.api_key is not None
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Tuple[Dict, Optional[str]]:
        """Make authenticated request to Eventbrite API"""
        if not self.is_configured():
            return {}, "Eventbrite API key not configured"
        
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}'
            }
            response = requests.get(
                f"{self.BASE_URL}{endpoint}",
                headers=headers,
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json(), None
            else:
                return {}, f"API error: {response.status_code} - {response.text}"
        except Exception as e:
            logger.error(f"Eventbrite request error: {e}")
            return {}, str(e)
    
    def search_events(self, query: str = None, location: str = None, 
                      category_id: str = None, start_date: str = None,
                      page: int = 1) -> Tuple[List[Dict], Optional[str]]:
        """Search for events"""
        params = {
            'page': page,
            'expand': 'venue,organizer,category'
        }
        
        if query:
            params['q'] = query
        if location:
            params['location.address'] = location
        if category_id:
            params['categories'] = category_id
        if start_date:
            params['start_date.range_start'] = start_date
        
        data, error = self._make_request('/events/search/', params)
        
        if error:
            return [], error
        
        events = []
        for event in data.get('events', []):
            events.append({
                'id': event.get('id'),
                'name': event.get('name', {}).get('text'),
                'description': event.get('description', {}).get('text', '')[:500],
                'url': event.get('url'),
                'start': event.get('start', {}).get('local'),
                'end': event.get('end', {}).get('local'),
                'venue': event.get('venue', {}).get('name') if event.get('venue') else None,
                'address': event.get('venue', {}).get('address', {}).get('localized_address_display') if event.get('venue') else None,
                'category': event.get('category', {}).get('name') if event.get('category') else None,
                'is_free': event.get('is_free', False),
                'logo_url': event.get('logo', {}).get('url') if event.get('logo') else None,
                'organizer': event.get('organizer', {}).get('name') if event.get('organizer') else None,
                'source': 'eventbrite'
            })
        
        return events, None
    
    def get_event_details(self, event_id: str) -> Tuple[Dict, Optional[str]]:
        """Get detailed event information"""
        data, error = self._make_request(f'/events/{event_id}/', {'expand': 'venue,organizer,ticket_classes'})
        
        if error:
            return {}, error
        
        return {
            'id': data.get('id'),
            'name': data.get('name', {}).get('text'),
            'description': data.get('description', {}).get('html'),
            'url': data.get('url'),
            'start': data.get('start', {}).get('local'),
            'end': data.get('end', {}).get('local'),
            'venue': data.get('venue'),
            'organizer': data.get('organizer'),
            'ticket_classes': data.get('ticket_classes', []),
            'capacity': data.get('capacity'),
            'is_free': data.get('is_free', False),
            'source': 'eventbrite'
        }, None
    
    def get_categories(self) -> Tuple[List[Dict], Optional[str]]:
        """Get event categories"""
        data, error = self._make_request('/categories/')
        
        if error:
            return [], error
        
        categories = []
        for cat in data.get('categories', []):
            categories.append({
                'id': cat.get('id'),
                'name': cat.get('name'),
                'short_name': cat.get('short_name')
            })
        
        return categories, None


class TicketmasterClient:
    """Ticketmaster Discovery API Client - Concerts, sports, theater"""
    
    BASE_URL = "https://app.ticketmaster.com/discovery/v2"
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('TICKETMASTER_API_KEY')
    
    def is_configured(self) -> bool:
        return self.api_key is not None
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Tuple[Dict, Optional[str]]:
        """Make authenticated request to Ticketmaster API"""
        if not self.is_configured():
            return {}, "Ticketmaster API key not configured"
        
        try:
            params = params or {}
            params['apikey'] = self.api_key
            
            response = requests.get(
                f"{self.BASE_URL}{endpoint}",
                params=params,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json(), None
            else:
                return {}, f"API error: {response.status_code}"
        except Exception as e:
            logger.error(f"Ticketmaster request error: {e}")
            return {}, str(e)
    
    def search_events(self, keyword: str = None, city: str = None,
                      state_code: str = None, country_code: str = "US",
                      classification_name: str = None, 
                      start_datetime: str = None, page: int = 0,
                      size: int = 20) -> Tuple[List[Dict], Optional[str]]:
        """Search for events"""
        params = {
            'countryCode': country_code,
            'page': page,
            'size': size
        }
        
        if keyword:
            params['keyword'] = keyword
        if city:
            params['city'] = city
        if state_code:
            params['stateCode'] = state_code
        if classification_name:
            params['classificationName'] = classification_name
        if start_datetime:
            params['startDateTime'] = start_datetime
        
        data, error = self._make_request('/events.json', params)
        
        if error:
            return [], error
        
        events = []
        embedded = data.get('_embedded', {})
        for event in embedded.get('events', []):
            venue = event.get('_embedded', {}).get('venues', [{}])[0]
            
            events.append({
                'id': event.get('id'),
                'name': event.get('name'),
                'url': event.get('url'),
                'start': event.get('dates', {}).get('start', {}).get('localDate'),
                'start_time': event.get('dates', {}).get('start', {}).get('localTime'),
                'venue': venue.get('name'),
                'city': venue.get('city', {}).get('name'),
                'state': venue.get('state', {}).get('stateCode'),
                'address': venue.get('address', {}).get('line1'),
                'genre': event.get('classifications', [{}])[0].get('genre', {}).get('name') if event.get('classifications') else None,
                'segment': event.get('classifications', [{}])[0].get('segment', {}).get('name') if event.get('classifications') else None,
                'image_url': event.get('images', [{}])[0].get('url') if event.get('images') else None,
                'price_range': event.get('priceRanges', [{}])[0] if event.get('priceRanges') else None,
                'source': 'ticketmaster'
            })
        
        return events, None
    
    def get_event_details(self, event_id: str) -> Tuple[Dict, Optional[str]]:
        """Get detailed event information"""
        data, error = self._make_request(f'/events/{event_id}.json')
        
        if error:
            return {}, error
        
        venues = data.get('_embedded', {}).get('venues', [])
        venue = venues[0] if venues else {}
        
        return {
            'id': data.get('id'),
            'name': data.get('name'),
            'description': data.get('info'),
            'url': data.get('url'),
            'dates': data.get('dates'),
            'venue': venue,
            'price_ranges': data.get('priceRanges', []),
            'images': data.get('images', []),
            'classifications': data.get('classifications', []),
            'seatmap': data.get('seatmap'),
            'source': 'ticketmaster'
        }, None
    
    def get_attractions(self, keyword: str = None, classification_name: str = None,
                        page: int = 0, size: int = 20) -> Tuple[List[Dict], Optional[str]]:
        """Search for attractions (artists, teams, etc.)"""
        params = {
            'page': page,
            'size': size
        }
        
        if keyword:
            params['keyword'] = keyword
        if classification_name:
            params['classificationName'] = classification_name
        
        data, error = self._make_request('/attractions.json', params)
        
        if error:
            return [], error
        
        attractions = []
        embedded = data.get('_embedded', {})
        for attraction in embedded.get('attractions', []):
            attractions.append({
                'id': attraction.get('id'),
                'name': attraction.get('name'),
                'url': attraction.get('url'),
                'image_url': attraction.get('images', [{}])[0].get('url') if attraction.get('images') else None,
                'classifications': attraction.get('classifications', []),
                'upcoming_events': attraction.get('upcomingEvents', {}).get('_total', 0)
            })
        
        return attractions, None
    
    def get_venues(self, keyword: str = None, city: str = None,
                   state_code: str = None, page: int = 0,
                   size: int = 20) -> Tuple[List[Dict], Optional[str]]:
        """Search for venues"""
        params = {
            'page': page,
            'size': size
        }
        
        if keyword:
            params['keyword'] = keyword
        if city:
            params['city'] = city
        if state_code:
            params['stateCode'] = state_code
        
        data, error = self._make_request('/venues.json', params)
        
        if error:
            return [], error
        
        venues = []
        embedded = data.get('_embedded', {})
        for venue in embedded.get('venues', []):
            venues.append({
                'id': venue.get('id'),
                'name': venue.get('name'),
                'url': venue.get('url'),
                'city': venue.get('city', {}).get('name'),
                'state': venue.get('state', {}).get('stateCode'),
                'address': venue.get('address', {}).get('line1'),
                'postal_code': venue.get('postalCode'),
                'image_url': venue.get('images', [{}])[0].get('url') if venue.get('images') else None,
                'upcoming_events': venue.get('upcomingEvents', {}).get('_total', 0)
            })
        
        return venues, None


class EventService:
    """Unified event service using multiple providers"""
    
    def __init__(self, company_id: int = None):
        self.company_id = company_id
        self.eventbrite = EventbriteClient()
        self.ticketmaster = TicketmasterClient()
        
        if company_id:
            self._load_company_credentials(company_id)
    
    def _load_company_credentials(self, company_id: int):
        """Load API credentials from company secrets"""
        try:
            from models import CompanySecret
            
            secrets = CompanySecret.query.filter_by(company_id=company_id).all()
            creds = {s.key: s.value for s in secrets}
            
            if creds.get('eventbrite_api_key'):
                self.eventbrite = EventbriteClient(api_key=creds['eventbrite_api_key'])
            
            if creds.get('ticketmaster_api_key'):
                self.ticketmaster = TicketmasterClient(api_key=creds['ticketmaster_api_key'])
        except Exception as e:
            logger.error(f"Error loading company credentials: {e}")
    
    def get_available_providers(self) -> List[str]:
        """Get list of configured providers"""
        providers = []
        if self.eventbrite.is_configured():
            providers.append('eventbrite')
        if self.ticketmaster.is_configured():
            providers.append('ticketmaster')
        return providers
    
    def search_all_events(self, query: str = None, location: str = None,
                          city: str = None, state: str = None) -> Dict[str, Any]:
        """Search events from all configured providers"""
        results = {
            'events': [],
            'providers_used': [],
            'errors': []
        }
        
        if self.eventbrite.is_configured():
            events, error = self.eventbrite.search_events(
                query=query,
                location=location or city
            )
            if events:
                results['events'].extend(events)
                results['providers_used'].append('eventbrite')
            if error:
                results['errors'].append({'provider': 'eventbrite', 'error': error})
        
        if self.ticketmaster.is_configured():
            events, error = self.ticketmaster.search_events(
                keyword=query,
                city=city,
                state_code=state
            )
            if events:
                results['events'].extend(events)
                results['providers_used'].append('ticketmaster')
            if error:
                results['errors'].append({'provider': 'ticketmaster', 'error': error})
        
        results['events'].sort(key=lambda x: x.get('start') or '', reverse=False)
        
        return results
    
    def get_local_events(self, city: str, state: str = None, 
                         category: str = None) -> List[Dict]:
        """Get local events for a specific city"""
        all_events = []
        
        if self.eventbrite.is_configured():
            events, _ = self.eventbrite.search_events(location=f"{city}, {state}" if state else city)
            all_events.extend(events)
        
        if self.ticketmaster.is_configured():
            events, _ = self.ticketmaster.search_events(
                city=city,
                state_code=state,
                classification_name=category
            )
            all_events.extend(events)
        
        return all_events
