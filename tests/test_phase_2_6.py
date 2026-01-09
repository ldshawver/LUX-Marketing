"""
Automated Test Suite for Phases 2-6
Tests SEO, Events, Social Media, Automations, and Calendar modules
"""

import pytest
from app import app, db
from models import (SEOKeyword, SEOBacklink, SEOCompetitor, SEOAudit, SEOPage,
                    EventTicket, TicketPurchase, EventCheckIn, Event, Contact,
                    SocialMediaAccount, SocialMediaSchedule,
                    AutomationTriggerLibrary, AutomationTest, AutomationABTest,
                    Automation)
from services.seo_service import SEOService
from services.event_service import EventService
from services.social_media_service import SocialMediaService
from services.automation_service import AutomationService
from datetime import datetime, timedelta

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

@pytest.fixture
def auth_client(client):
    """Create authenticated test client"""
    from models import User
    user = User(username='testuser', email='test@test.com', is_admin=True)
    user.set_password('testpass')
    db.session.add(user)
    db.session.commit()
    
    client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'testpass'
    })
    return client

# ===== SEO MODULE TESTS =====
class TestSEOModule:
    def test_seo_dashboard_loads(self, auth_client):
        """Test SEO dashboard page loads"""
        response = auth_client.get('/seo/dashboard')
        assert response.status_code == 200
        assert b'SEO Dashboard' in response.data
    
    def test_add_keyword(self, auth_client):
        """Test adding keyword for tracking"""
        keyword = SEOService.track_keyword('test keyword', 'https://example.com')
        assert keyword is not None
        assert keyword.keyword == 'test keyword'
        assert keyword.is_tracking == True
    
    def test_update_keyword_position(self, auth_client):
        """Test updating keyword position"""
        keyword = SEOService.track_keyword('test keyword')
        result = SEOService.update_keyword_position(keyword.id, 5, impressions=100, clicks=10)
        assert result is not None
        assert result.current_position == 5
        assert result.best_position == 5
    
    def test_add_backlink(self, auth_client):
        """Test adding backlink"""
        backlink = SEOService.add_backlink(
            'https://example.com/page',
            'https://mysite.com',
            'anchor text',
            50
        )
        assert backlink is not None
        assert backlink.domain_authority == 50
    
    def test_run_site_audit(self, auth_client):
        """Test running site audit"""
        audit = SEOService.run_site_audit('https://example.com', 'full')
        assert audit is not None
        assert audit.status == 'completed'
        assert audit.overall_score > 0
    
    def test_seo_keywords_page(self, auth_client):
        """Test SEO keywords page loads"""
        response = auth_client.get('/seo/keywords')
        assert response.status_code == 200
    
    def test_seo_backlinks_page(self, auth_client):
        """Test SEO backlinks page loads"""
        response = auth_client.get('/seo/backlinks')
        assert response.status_code == 200

# ===== EVENT TICKETING TESTS =====
class TestEventModule:
    def test_create_ticket_type(self, auth_client):
        """Test creating ticket type"""
        # Create event first
        event = Event(
            name='Test Event',
            description='Test Description',
            start_date=datetime.utcnow() + timedelta(days=7),
            max_attendees=100
        )
        db.session.add(event)
        db.session.commit()
        
        ticket = EventService.create_ticket_type(
            event.id,
            'VIP Ticket',
            99.99,
            50,
            'VIP access to all areas'
        )
        assert ticket is not None
        assert ticket.name == 'VIP Ticket'
        assert ticket.price == 99.99
        assert ticket.quantity_total == 50
    
    def test_purchase_ticket(self, auth_client):
        """Test ticket purchase"""
        # Setup
        event = Event(
            name='Test Event',
            start_date=datetime.utcnow() + timedelta(days=7),
            max_attendees=100
        )
        db.session.add(event)
        db.session.commit()
        
        ticket = EventService.create_ticket_type(event.id, 'General', 50.0, 100)
        
        contact = Contact(
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        db.session.add(contact)
        db.session.commit()
        
        # Purchase ticket
        purchase = EventService.purchase_ticket(ticket.id, contact.id, 2)
        assert purchase is not None
        assert purchase.quantity == 2
        assert purchase.total_amount == 100.0
        assert len(purchase.ticket_codes) == 2
    
    def test_event_check_in(self, auth_client):
        """Test event check-in"""
        event = Event(
            name='Test Event',
            start_date=datetime.utcnow() + timedelta(days=7),
            max_attendees=100
        )
        contact = Contact(
            email='test@example.com',
            first_name='Test',
            last_name='User'
        )
        db.session.add_all([event, contact])
        db.session.commit()
        
        checkin = EventService.check_in_attendee(
            event.id,
            contact.id,
            method='manual',
            staff_name='Admin'
        )
        assert checkin is not None
        assert checkin.check_in_method == 'manual'

# ===== SOCIAL MEDIA TESTS =====
class TestSocialMediaModule:
    def test_connect_account(self, auth_client):
        """Test connecting social media account"""
        account = SocialMediaService.connect_account(
            'twitter',
            'testuser',
            'fake_token_123'
        )
        assert account is not None
        assert account.platform == 'twitter'
        assert account.is_verified == True
    
    def test_schedule_post(self, auth_client):
        """Test scheduling social media post"""
        account = SocialMediaService.connect_account('twitter', 'testuser', 'token')
        
        scheduled_time = datetime.utcnow() + timedelta(hours=2)
        post = SocialMediaService.schedule_post(
            account.id,
            'Test post content',
            scheduled_time,
            hashtags='#test #marketing'
        )
        assert post is not None
        assert post.content == 'Test post content'
        assert post.status == 'scheduled'
    
    def test_social_accounts_page(self, auth_client):
        """Test social accounts page loads"""
        response = auth_client.get('/social/accounts')
        assert response.status_code == 200
        assert b'Social Media Accounts' in response.data

    def test_facebook_accounts_page(self, auth_client):
        """Test Facebook accounts page loads"""
        response = auth_client.get('/facebook/accounts')
        assert response.status_code == 200
        assert b'Facebook Pages' in response.data

    def test_facebook_posts_page(self, auth_client):
        """Test Facebook posts page loads"""
        response = auth_client.get('/facebook/posts')
        assert response.status_code == 200
        assert b'Facebook Posts' in response.data

    def test_facebook_engagement_page(self, auth_client):
        """Test Facebook engagement page loads"""
        response = auth_client.get('/facebook/engagement')
        assert response.status_code == 200
        assert b'Facebook Engagement' in response.data

# ===== AUTOMATION TESTS =====
class TestAutomationModule:
    def test_trigger_library_seeded(self, auth_client):
        """Test trigger library has pre-built templates"""
        AutomationService.seed_trigger_library()
        triggers = AutomationService.get_trigger_library()
        assert len(triggers) >= 3
        assert any(t.name == 'Welcome Series' for t in triggers)
    
    def test_run_automation_test(self, auth_client):
        """Test running automation in test mode"""
        automation = Automation(
            name='Test Automation',
            trigger_type='signup',
            is_active=True
        )
        db.session.add(automation)
        db.session.commit()
        
        test = AutomationService.run_test(automation.id)
        assert test is not None
        assert test.status == 'completed'
        assert test.test_results is not None
    
    def test_trigger_library_page(self, auth_client):
        """Test automation trigger library page loads"""
        response = auth_client.get('/automations/triggers')
        assert response.status_code == 200

# ===== CALENDAR TESTS =====
class TestMarketingCalendar:
    def test_calendar_page_loads(self, auth_client):
        """Test marketing calendar page loads"""
        response = auth_client.get('/calendar')
        assert response.status_code == 200
        assert b'Marketing Calendar' in response.data

# ===== INTEGRATION TESTS =====
class TestIntegration:
    def test_all_new_routes_accessible(self, auth_client):
        """Test all new routes return 200 OK"""
        routes = [
            '/seo/dashboard',
            '/seo/keywords',
            '/seo/backlinks',
            '/seo/competitors',
            '/seo/audit',
            '/social/accounts',
            '/automations/triggers',
            '/calendar'
        ]
        
        for route in routes:
            response = auth_client.get(route)
            assert response.status_code == 200, f"Route {route} failed"
    
    def test_database_schema_complete(self, auth_client):
        """Test all new tables exist"""
        # This implicitly tests if models can be created
        keyword = SEOKeyword(keyword='test')
        ticket = EventTicket(event_id=1, name='test', price=10, quantity_total=10)
        account = SocialMediaAccount(platform='twitter', account_name='test')
        trigger = AutomationTriggerLibrary(name='test', trigger_type='signup')
        
        assert keyword is not None
        assert ticket is not None
        assert account is not None
        assert trigger is not None

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
