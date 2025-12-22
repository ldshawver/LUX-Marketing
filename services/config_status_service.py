"""
Configuration Status Service
Checks which integrations are configured and provides setup instructions
"""
from typing import Dict, List, Any
from models import Company


INTEGRATION_REQUIREMENTS = {
    'ai_content': {
        'name': 'AI Content Generation',
        'icon': '🤖',
        'required_secrets': ['OPENAI_API_KEY'],
        'instructions': 'Add your OpenAI API key in Settings → Integrations to enable AI-powered content generation.',
        'docs_url': 'https://platform.openai.com/api-keys'
    },
    'google_analytics': {
        'name': 'Google Analytics',
        'icon': '📊',
        'required_secrets': ['GA4_PROPERTY_ID', 'GA4_SERVICE_ACCOUNT_JSON'],
        'instructions': 'Add your GA4 Property ID and Service Account JSON in Settings → Integrations to track website analytics.',
        'docs_url': 'https://developers.google.com/analytics'
    },
    'google_ads': {
        'name': 'Google Ads',
        'icon': '📢',
        'required_secrets': ['GOOGLE_ADS_CLIENT_ID', 'GOOGLE_ADS_CLIENT_SECRET', 'GOOGLE_ADS_DEVELOPER_TOKEN'],
        'instructions': 'Add your Google Ads credentials in Settings → Integrations to manage ad campaigns.',
        'docs_url': 'https://developers.google.com/google-ads/api'
    },
    'facebook': {
        'name': 'Facebook',
        'icon': '👍',
        'required_secrets': ['facebook_app_id', 'facebook_app_secret'],
        'instructions': 'Add your Facebook App ID and Secret in Settings → Integrations, then connect via OAuth.',
        'docs_url': 'https://developers.facebook.com/apps'
    },
    'facebook_webhook': {
        'name': 'Facebook Webhook',
        'icon': '🔔',
        'required_secrets': ['fb_webhook_verify_token'],
        'instructions': 'Add a Webhook Verify Token in Settings → Integrations, then configure the webhook URL in Facebook Developer Console.',
        'docs_url': 'https://developers.facebook.com/docs/graph-api/webhooks'
    },
    'instagram': {
        'name': 'Instagram',
        'icon': '📸',
        'required_secrets': ['INSTAGRAM_BUSINESS_ACCOUNT_ID', 'INSTAGRAM_ACCESS_TOKEN'],
        'instructions': 'Connect your Instagram Business account via Facebook OAuth in Settings → Integrations.',
        'docs_url': 'https://developers.facebook.com/docs/instagram-api'
    },
    'tiktok': {
        'name': 'TikTok',
        'icon': '🎵',
        'required_secrets': ['TIKTOK_CLIENT_KEY', 'TIKTOK_CLIENT_SECRET'],
        'instructions': 'Add your TikTok Client Key and Secret in Settings → Integrations, then connect via OAuth.',
        'docs_url': 'https://developers.tiktok.com'
    },
    'twitter': {
        'name': 'X (Twitter)',
        'icon': '🐦',
        'required_secrets': ['TWITTER_API_KEY', 'TWITTER_API_SECRET', 'TWITTER_BEARER_TOKEN'],
        'instructions': 'Add your Twitter/X API credentials in Settings → Integrations.',
        'docs_url': 'https://developer.twitter.com'
    },
    'linkedin': {
        'name': 'LinkedIn',
        'icon': '💼',
        'required_secrets': ['LINKEDIN_CLIENT_ID', 'LINKEDIN_CLIENT_SECRET'],
        'instructions': 'Add your LinkedIn App credentials in Settings → Integrations.',
        'docs_url': 'https://www.linkedin.com/developers'
    },
    'youtube': {
        'name': 'YouTube',
        'icon': '🎬',
        'required_secrets': ['YOUTUBE_API_KEY', 'YOUTUBE_CHANNEL_ID'],
        'instructions': 'Add your YouTube API Key and Channel ID in Settings → Integrations.',
        'docs_url': 'https://developers.google.com/youtube'
    },
    'reddit': {
        'name': 'Reddit',
        'icon': '🤖',
        'required_secrets': ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET'],
        'instructions': 'Add your Reddit App credentials in Settings → Integrations.',
        'docs_url': 'https://www.reddit.com/prefs/apps'
    },
    'snapchat': {
        'name': 'Snapchat',
        'icon': '👻',
        'required_secrets': ['SNAPCHAT_BUSINESS_ACCOUNT_ID', 'SNAPCHAT_ACCESS_TOKEN'],
        'instructions': 'Add your Snapchat Business Account ID and Access Token in Settings → Integrations.',
        'docs_url': 'https://developers.snapchat.com'
    },
    'woocommerce': {
        'name': 'WooCommerce',
        'icon': '🛒',
        'required_secrets': ['WC_STORE_URL', 'WC_CONSUMER_KEY', 'WC_CONSUMER_SECRET'],
        'instructions': 'Add your WooCommerce store URL and API keys in Settings → Integrations.',
        'docs_url': 'https://woocommerce.github.io/woocommerce-rest-api-docs'
    },
    'keyword_research_dataforseo': {
        'name': 'Keyword Research (DataForSEO)',
        'icon': '🔍',
        'required_secrets': ['dataforseo_login', 'dataforseo_password'],
        'instructions': 'Add your DataForSEO login and password in Settings → Integrations for affordable keyword research.',
        'docs_url': 'https://dataforseo.com'
    },
    'keyword_research_semrush': {
        'name': 'Keyword Research (SEMrush)',
        'icon': '🔍',
        'required_secrets': ['semrush_api_key'],
        'instructions': 'Add your SEMrush API key in Settings → Integrations for premium keyword data.',
        'docs_url': 'https://www.semrush.com/api'
    },
    'keyword_research_moz': {
        'name': 'Keyword Research (Moz)',
        'icon': '🔍',
        'required_secrets': ['moz_access_id', 'moz_secret_key'],
        'instructions': 'Add your Moz Access ID and Secret Key in Settings → Integrations for domain authority data.',
        'docs_url': 'https://moz.com/products/api'
    },
    'events_eventbrite': {
        'name': 'Events (Eventbrite)',
        'icon': '🎫',
        'required_secrets': ['eventbrite_api_key'],
        'instructions': 'Add your Eventbrite API key in Settings → Integrations to search local events.',
        'docs_url': 'https://www.eventbrite.com/platform/api'
    },
    'events_ticketmaster': {
        'name': 'Events (Ticketmaster)',
        'icon': '🎫',
        'required_secrets': ['ticketmaster_api_key'],
        'instructions': 'Add your Ticketmaster API key in Settings → Integrations to search concerts, sports, and theater.',
        'docs_url': 'https://developer.ticketmaster.com'
    },
    'twilio_sms': {
        'name': 'SMS Marketing (Twilio)',
        'icon': '📱',
        'required_secrets': ['twilio_account_sid', 'twilio_auth_token', 'twilio_phone_number'],
        'instructions': 'Add your Twilio Account SID, Auth Token, and Phone Number in Settings → Integrations.',
        'docs_url': 'https://www.twilio.com/docs'
    },
    'zapier': {
        'name': 'Zapier Automation',
        'icon': '⚡',
        'required_secrets': ['zapier_webhook_secret'],
        'instructions': 'Add a Zapier Webhook Secret in Settings → Integrations for secure webhook automation.',
        'docs_url': 'https://zapier.com/developer'
    },
    'ms365': {
        'name': 'Microsoft 365',
        'icon': '📧',
        'required_secrets': ['MS365_CLIENT_ID', 'MS365_CLIENT_SECRET', 'MS365_TENANT_ID'],
        'instructions': 'Add your Microsoft 365 App credentials in Settings → Integrations for email marketing.',
        'docs_url': 'https://docs.microsoft.com/en-us/graph'
    }
}


class ConfigStatusService:
    """Service to check configuration status of integrations"""
    
    @staticmethod
    def get_configured_secrets(company: Company) -> set:
        """Get set of configured secret keys for a company"""
        configured = set()
        if not company:
            return configured
            
        for integration_key, config in INTEGRATION_REQUIREMENTS.items():
            for secret_key in config['required_secrets']:
                value = company.get_secret(secret_key)
                if value:
                    configured.add(secret_key)
        return configured
    
    @staticmethod
    def check_integration_status(company: Company, integration_key: str) -> Dict[str, Any]:
        """Check if a specific integration is configured"""
        if integration_key not in INTEGRATION_REQUIREMENTS:
            return {'configured': False, 'error': 'Unknown integration'}
        
        config = INTEGRATION_REQUIREMENTS[integration_key]
        missing_secrets = []
        
        for secret_key in config['required_secrets']:
            value = company.get_secret(secret_key) if company else None
            if not value:
                missing_secrets.append(secret_key)
        
        is_configured = len(missing_secrets) == 0
        
        return {
            'integration_key': integration_key,
            'name': config['name'],
            'icon': config['icon'],
            'configured': is_configured,
            'missing_secrets': missing_secrets,
            'instructions': config['instructions'] if not is_configured else None,
            'docs_url': config['docs_url']
        }
    
    @staticmethod
    def get_all_integration_status(company: Company) -> Dict[str, Dict[str, Any]]:
        """Get status of all integrations for a company"""
        status = {}
        for integration_key in INTEGRATION_REQUIREMENTS:
            status[integration_key] = ConfigStatusService.check_integration_status(company, integration_key)
        return status
    
    @staticmethod
    def get_unconfigured_integrations(company: Company) -> List[Dict[str, Any]]:
        """Get list of integrations that are not configured"""
        unconfigured = []
        for integration_key, config in INTEGRATION_REQUIREMENTS.items():
            status = ConfigStatusService.check_integration_status(company, integration_key)
            if not status['configured']:
                unconfigured.append(status)
        return unconfigured
    
    @staticmethod
    def get_configured_integrations(company: Company) -> List[Dict[str, Any]]:
        """Get list of integrations that are configured"""
        configured = []
        for integration_key, config in INTEGRATION_REQUIREMENTS.items():
            status = ConfigStatusService.check_integration_status(company, integration_key)
            if status['configured']:
                configured.append(status)
        return configured
    
    @staticmethod
    def get_essential_unconfigured(company: Company) -> List[Dict[str, Any]]:
        """Get list of essential integrations that need configuration (limited to most important)"""
        essential_keys = [
            'ai_content',
            'facebook',
            'instagram',
            'tiktok',
            'twitter',
            'google_analytics'
        ]
        
        unconfigured = []
        for key in essential_keys:
            status = ConfigStatusService.check_integration_status(company, key)
            if not status['configured']:
                unconfigured.append(status)
        return unconfigured
    
    @staticmethod
    def check_oauth_connections(company: Company) -> Dict[str, Dict[str, Any]]:
        """Check OAuth connection status for social media platforms"""
        from models import FacebookOAuth, InstagramOAuth, TikTokOAuth
        
        connections = {}
        if not company:
            return connections
        
        facebook_connected = FacebookOAuth.query.filter_by(
            company_id=company.id, status='active'
        ).first() is not None
        connections['facebook'] = {
            'connected': facebook_connected,
            'name': 'Facebook',
            'icon': '📘',
            'instructions': 'Connect your Facebook Page to post content and view insights.',
            'action_url': '/auth/facebook/connect',
            'action_text': 'Connect Facebook'
        }
        
        instagram_connected = InstagramOAuth.query.filter_by(
            company_id=company.id, status='active'
        ).first() is not None
        connections['instagram'] = {
            'connected': instagram_connected,
            'name': 'Instagram',
            'icon': '📸',
            'instructions': 'Connect your Instagram Business account to post content and view insights.',
            'action_url': '/auth/instagram/connect',
            'action_text': 'Connect Instagram'
        }
        
        tiktok_connected = TikTokOAuth.query.filter_by(
            company_id=company.id, status='active'
        ).first() is not None
        connections['tiktok'] = {
            'connected': tiktok_connected,
            'name': 'TikTok',
            'icon': '🎵',
            'instructions': 'Connect your TikTok account to manage videos and view analytics.',
            'action_url': '/auth/tiktok/connect',
            'action_text': 'Connect TikTok'
        }
        
        return connections
    
    @staticmethod
    def get_dashboard_alerts(company: Company) -> List[Dict[str, Any]]:
        """Get configuration alerts to show on dashboard"""
        alerts = []
        
        if not company:
            return alerts
        
        oauth_connections = ConfigStatusService.check_oauth_connections(company)
        for platform, conn_status in oauth_connections.items():
            if not conn_status['connected']:
                has_api_keys = ConfigStatusService.check_integration_status(company, platform).get('configured', False)
                if has_api_keys:
                    alerts.append({
                        'type': 'warning',
                        'icon': conn_status['icon'],
                        'title': f"{conn_status['name']} Not Connected",
                        'message': conn_status['instructions'],
                        'action_url': conn_status['action_url'],
                        'action_text': conn_status['action_text']
                    })
                else:
                    alerts.append({
                        'type': 'error',
                        'icon': conn_status['icon'],
                        'title': f"{conn_status['name']} Needs Setup",
                        'message': f"Add {conn_status['name']} API credentials in Settings, then connect your account.",
                        'action_url': '/company-settings',
                        'action_text': 'Configure Now'
                    })
        
        essential_unconfigured = ConfigStatusService.get_essential_unconfigured(company)
        non_oauth_essential = [i for i in essential_unconfigured 
                              if i['integration_key'] not in ['facebook', 'instagram', 'tiktok']]
        
        for integration in non_oauth_essential[:3]:
            alerts.append({
                'type': 'info',
                'icon': integration['icon'],
                'title': f"{integration['name']} Not Configured",
                'message': integration['instructions'],
                'action_url': '/company-settings',
                'action_text': 'Configure Now'
            })
        
        return alerts[:5]
