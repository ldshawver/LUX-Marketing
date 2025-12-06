"""
Facebook OAuth 2.0 Integration for LUX Marketing Platform
Handles Facebook Login and Graph API access for business pages
"""

import os
import secrets
import logging
from datetime import datetime, timedelta
from flask import Blueprint, redirect, url_for, request, jsonify, flash, session
from flask_login import login_required, current_user
from models import db, FacebookOAuth, CompanySecret
from services.secret_vault import SecretVault

logger = logging.getLogger(__name__)

facebook_auth_bp = Blueprint('facebook_auth', __name__, url_prefix='/auth/facebook')

class FacebookService:
    """Facebook OAuth and Graph API service"""
    
    AUTHORIZATION_URL = "https://www.facebook.com/v18.0/dialog/oauth"
    TOKEN_URL = "https://graph.facebook.com/v18.0/oauth/access_token"
    GRAPH_API_URL = "https://graph.facebook.com/v18.0"
    
    SCOPES = [
        'public_profile',
        'email',
        'pages_show_list',
        'pages_read_engagement',
        'pages_manage_posts',
        'pages_manage_metadata',
        'business_management'
    ]
    
    @staticmethod
    def get_credentials(company_id):
        """Get Facebook App credentials from company secrets"""
        app_id = CompanySecret.query.filter_by(
            company_id=company_id, 
            key='facebook_app_id'
        ).first()
        app_secret = CompanySecret.query.filter_by(
            company_id=company_id, 
            key='facebook_app_secret'
        ).first()
        
        return (
            app_id.value if app_id else None,
            app_secret.value if app_secret else None
        )
    
    @staticmethod
    def get_redirect_uri():
        """Get OAuth redirect URI"""
        return "https://lux.lucifercruz.com/auth/facebook/callback"
    
    @staticmethod
    def get_authorization_url(company_id):
        """Generate Facebook OAuth authorization URL"""
        app_id, app_secret = FacebookService.get_credentials(company_id)
        
        if not app_id or not app_secret:
            return None, "Facebook App credentials not configured"
        
        state = secrets.token_urlsafe(32)
        session['facebook_oauth_state'] = state
        session['facebook_oauth_company_id'] = company_id
        
        params = {
            'client_id': app_id,
            'redirect_uri': FacebookService.get_redirect_uri(),
            'state': state,
            'scope': ','.join(FacebookService.SCOPES),
            'response_type': 'code'
        }
        
        query_string = '&'.join(f"{k}={v}" for k, v in params.items())
        auth_url = f"{FacebookService.AUTHORIZATION_URL}?{query_string}"
        
        return auth_url, None
    
    @staticmethod
    def exchange_code_for_token(code, company_id):
        """Exchange authorization code for access token"""
        import requests
        
        app_id, app_secret = FacebookService.get_credentials(company_id)
        
        if not app_id or not app_secret:
            return None, "Facebook App credentials not configured"
        
        try:
            response = requests.get(
                FacebookService.TOKEN_URL,
                params={
                    'client_id': app_id,
                    'client_secret': app_secret,
                    'redirect_uri': FacebookService.get_redirect_uri(),
                    'code': code
                },
                timeout=30
            )
            
            if response.status_code != 200:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                return None, f"Token exchange failed: {error_msg}"
            
            data = response.json()
            return data, None
            
        except Exception as e:
            logger.error(f"Facebook token exchange error: {e}")
            return None, str(e)
    
    @staticmethod
    def get_long_lived_token(short_token, company_id):
        """Exchange short-lived token for long-lived token (60 days)"""
        import requests
        
        app_id, app_secret = FacebookService.get_credentials(company_id)
        
        try:
            response = requests.get(
                FacebookService.TOKEN_URL,
                params={
                    'grant_type': 'fb_exchange_token',
                    'client_id': app_id,
                    'client_secret': app_secret,
                    'fb_exchange_token': short_token
                },
                timeout=30
            )
            
            if response.status_code != 200:
                return None, "Failed to get long-lived token"
            
            return response.json(), None
            
        except Exception as e:
            logger.error(f"Facebook long-lived token error: {e}")
            return None, str(e)
    
    @staticmethod
    def get_user_info(access_token):
        """Get Facebook user info"""
        import requests
        
        try:
            response = requests.get(
                f"{FacebookService.GRAPH_API_URL}/me",
                params={
                    'access_token': access_token,
                    'fields': 'id,name,email,picture'
                },
                timeout=30
            )
            
            if response.status_code != 200:
                return None, "Failed to get user info"
            
            return response.json(), None
            
        except Exception as e:
            logger.error(f"Facebook user info error: {e}")
            return None, str(e)
    
    @staticmethod
    def get_pages(access_token):
        """Get user's Facebook pages"""
        import requests
        
        try:
            response = requests.get(
                f"{FacebookService.GRAPH_API_URL}/me/accounts",
                params={
                    'access_token': access_token,
                    'fields': 'id,name,access_token,category,picture'
                },
                timeout=30
            )
            
            if response.status_code != 200:
                return None, "Failed to get pages"
            
            return response.json().get('data', []), None
            
        except Exception as e:
            logger.error(f"Facebook pages error: {e}")
            return None, str(e)
    
    @staticmethod
    def post_to_page(page_id, page_access_token, message, link=None):
        """Post content to a Facebook page"""
        import requests
        
        try:
            data = {
                'message': message,
                'access_token': page_access_token
            }
            
            if link:
                data['link'] = link
            
            response = requests.post(
                f"{FacebookService.GRAPH_API_URL}/{page_id}/feed",
                data=data,
                timeout=30
            )
            
            if response.status_code != 200:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                return None, f"Post failed: {error_msg}"
            
            return response.json(), None
            
        except Exception as e:
            logger.error(f"Facebook post error: {e}")
            return None, str(e)


@facebook_auth_bp.route('/connect')
@login_required
def connect():
    """Initiate Facebook OAuth flow"""
    company = current_user.get_default_company()
    if not company:
        flash('No company selected', 'error')
        return redirect(url_for('main.settings_integrations'))
    
    auth_url, error = FacebookService.get_authorization_url(company.id)
    
    if error:
        flash(f'Facebook API credentials not configured. Please add your Facebook App ID and App Secret in Settings → API Keys & Secrets.', 'error')
        return redirect(url_for('main.company_settings', id=company.id))
    
    return redirect(auth_url)


@facebook_auth_bp.route('/callback')
def callback():
    """Handle Facebook OAuth callback"""
    error = request.args.get('error')
    error_description = request.args.get('error_description')
    
    if error:
        flash(f'Facebook authorization failed: {error_description or error}', 'error')
        return redirect(url_for('main.settings_integrations'))
    
    code = request.args.get('code')
    state = request.args.get('state')
    
    stored_state = session.pop('facebook_oauth_state', None)
    company_id = session.pop('facebook_oauth_company_id', None)
    
    if not state or state != stored_state:
        flash('Invalid OAuth state. Please try again.', 'error')
        return redirect(url_for('main.settings_integrations'))
    
    if not code:
        flash('No authorization code received', 'error')
        return redirect(url_for('main.settings_integrations'))
    
    if not company_id:
        flash('Session expired. Please try again.', 'error')
        return redirect(url_for('main.settings_integrations'))
    
    token_data, error = FacebookService.exchange_code_for_token(code, company_id)
    
    if error:
        flash(f'Token exchange failed: {error}', 'error')
        return redirect(url_for('main.settings_integrations'))
    
    short_token = token_data.get('access_token')
    
    long_token_data, error = FacebookService.get_long_lived_token(short_token, company_id)
    
    if error:
        access_token = short_token
        expires_in = token_data.get('expires_in', 3600)
    else:
        access_token = long_token_data.get('access_token', short_token)
        expires_in = long_token_data.get('expires_in', 5184000)
    
    user_info, error = FacebookService.get_user_info(access_token)
    
    if error:
        flash(f'Failed to get user info: {error}', 'error')
        return redirect(url_for('main.settings_integrations'))
    
    facebook_user_id = user_info.get('id')
    display_name = user_info.get('name', 'Facebook User')
    email = user_info.get('email')
    picture = user_info.get('picture', {}).get('data', {}).get('url')
    
    expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
    
    oauth_record = FacebookOAuth.query.filter_by(
        user_id=current_user.id,
        company_id=company_id
    ).first()
    
    if oauth_record:
        oauth_record.set_access_token(access_token)
        oauth_record.facebook_user_id = facebook_user_id
        oauth_record.display_name = display_name
        oauth_record.email = email
        oauth_record.avatar_url = picture
        oauth_record.expires_at = expires_at
        oauth_record.updated_at = datetime.utcnow()
    else:
        oauth_record = FacebookOAuth(
            user_id=current_user.id,
            company_id=company_id,
            facebook_user_id=facebook_user_id,
            display_name=display_name,
            email=email,
            avatar_url=picture,
            expires_at=expires_at
        )
        oauth_record.set_access_token(access_token)
        db.session.add(oauth_record)
    
    db.session.commit()
    
    flash('Facebook connected successfully!', 'success')
    return redirect(url_for('main.company_settings', id=company_id))


@facebook_auth_bp.route('/disconnect', methods=['POST'])
@login_required
def disconnect():
    """Disconnect Facebook account"""
    company = current_user.get_default_company()
    if not company:
        return jsonify({'success': False, 'error': 'No company selected'}), 400
    
    oauth_record = FacebookOAuth.query.filter_by(
        user_id=current_user.id,
        company_id=company.id
    ).first()
    
    if oauth_record:
        db.session.delete(oauth_record)
        db.session.commit()
    
    return jsonify({'success': True, 'message': 'Facebook disconnected'})


@facebook_auth_bp.route('/status')
@login_required
def status():
    """Check Facebook connection status"""
    company = current_user.get_default_company()
    if not company:
        return jsonify({'connected': False})
    
    oauth_record = FacebookOAuth.query.filter_by(
        user_id=current_user.id,
        company_id=company.id
    ).first()
    
    if not oauth_record:
        return jsonify({'connected': False})
    
    needs_refresh = oauth_record.expires_at and oauth_record.expires_at < datetime.utcnow()
    
    return jsonify({
        'connected': True,
        'facebook_user_id': oauth_record.facebook_user_id,
        'display_name': oauth_record.display_name,
        'avatar_url': oauth_record.avatar_url,
        'expires_at': oauth_record.expires_at.isoformat() if oauth_record.expires_at else None,
        'needs_refresh': needs_refresh
    })


@facebook_auth_bp.route('/pages')
@login_required
def get_pages():
    """Get user's Facebook pages"""
    company = current_user.get_default_company()
    if not company:
        return jsonify({'success': False, 'error': 'No company selected'}), 400
    
    oauth_record = FacebookOAuth.query.filter_by(
        user_id=current_user.id,
        company_id=company.id
    ).first()
    
    if not oauth_record:
        return jsonify({'success': False, 'error': 'Facebook not connected'}), 401
    
    access_token = oauth_record.get_access_token()
    pages, error = FacebookService.get_pages(access_token)
    
    if error:
        return jsonify({'success': False, 'error': error}), 500
    
    return jsonify({'success': True, 'pages': pages})


@facebook_auth_bp.route('/post', methods=['POST'])
@login_required
def post_to_page():
    """Post content to a Facebook page"""
    company = current_user.get_default_company()
    if not company:
        return jsonify({'success': False, 'error': 'No company selected'}), 400
    
    oauth_record = FacebookOAuth.query.filter_by(
        user_id=current_user.id,
        company_id=company.id
    ).first()
    
    if not oauth_record:
        return jsonify({'success': False, 'error': 'Facebook not connected'}), 401
    
    data = request.get_json()
    page_id = data.get('page_id')
    page_access_token = data.get('page_access_token')
    message = data.get('message')
    link = data.get('link')
    
    if not page_id or not page_access_token or not message:
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    result, error = FacebookService.post_to_page(page_id, page_access_token, message, link)
    
    if error:
        return jsonify({'success': False, 'error': error}), 500
    
    return jsonify({'success': True, 'post_id': result.get('id')})
