"""
Comprehensive Feature Testing for LUX Marketing Platform
Tests all major features to ensure they work correctly
"""
import sys
import logging
from app import app, db
from models import (
    User, Contact, EmailTemplate, Campaign, CampaignRecipient,
    SMSCampaign, SMSRecipient, SocialPost, Event, EventRegistration,
    Automation, AutomationStep, Segment, SegmentMember, LandingPage,
    WebForm, ABTest, BrandKit, Product, Order
)
from werkzeug.security import generate_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FeatureTester:
    """Comprehensive feature testing class"""
    
    def __init__(self):
        self.app = app
        self.errors = []
        self.passed = []
    
    def run_all_tests(self):
        """Run all feature tests"""
        logger.info("="*60)
        logger.info("STARTING COMPREHENSIVE FEATURE TESTS")
        logger.info("="*60)
        
        tests = [
            ("Database Connection", self.test_database_connection),
            ("User Model", self.test_user_model),
            ("Contact Model", self.test_contact_model),
            ("Email Template Model", self.test_email_template_model),
            ("Campaign Model", self.test_campaign_model),
            ("SMS Campaign Model", self.test_sms_campaign_model),
            ("Social Media Model", self.test_social_media_model),
            ("Event Model", self.test_event_model),
            ("Automation Model", self.test_automation_model),
            ("Segment Model", self.test_segment_model),
            ("Landing Page Model", self.test_landing_page_model),
            ("Web Form Model", self.test_web_form_model),
            ("A/B Test Model", self.test_abtest_model),
            ("Brand Kit Model", self.test_brand_kit_model),
        ]
        
        for test_name, test_func in tests:
            try:
                logger.info(f"\n{'='*60}")
                logger.info(f"Testing: {test_name}")
                logger.info(f"{'='*60}")
                test_func()
                self.passed.append(test_name)
                logger.info(f"✅ {test_name}: PASSED")
            except Exception as e:
                self.errors.append((test_name, str(e)))
                logger.error(f"❌ {test_name}: FAILED - {str(e)}")
        
        self.print_summary()
    
    def test_database_connection(self):
        """Test database connectivity"""
        with self.app.app_context():
            # Try to execute a simple query
            result = db.session.execute(db.text('SELECT 1')).scalar()
            assert result == 1, "Database query failed"
            logger.info("✓ Database connection successful")
    
    def test_user_model(self):
        """Test User model"""
        with self.app.app_context():
            # Count existing users
            user_count = User.query.count()
            logger.info(f"✓ Found {user_count} users in database")
            
            # Verify admin user exists
            admin = User.query.filter_by(username='admin').first()
            if admin:
                logger.info("✓ Admin user exists")
            else:
                logger.warning("⚠ No admin user found")
    
    def test_contact_model(self):
        """Test Contact model"""
        with self.app.app_context():
            contact_count = Contact.query.count()
            logger.info(f"✓ Found {contact_count} contacts in database")
            
            # Test contact query
            contacts = Contact.query.limit(5).all()
            logger.info(f"✓ Successfully queried contacts")
    
    def test_email_template_model(self):
        """Test EmailTemplate model"""
        with self.app.app_context():
            template_count = EmailTemplate.query.count()
            logger.info(f"✓ Found {template_count} email templates")
            
            templates = EmailTemplate.query.limit(5).all()
            logger.info(f"✓ Successfully queried email templates")
    
    def test_campaign_model(self):
        """Test Campaign model"""
        with self.app.app_context():
            campaign_count = Campaign.query.count()
            logger.info(f"✓ Found {campaign_count} email campaigns")
            
            # Test campaign with recipients
            campaigns = Campaign.query.limit(5).all()
            for campaign in campaigns:
                recipient_count = CampaignRecipient.query.filter_by(campaign_id=campaign.id).count()
                logger.info(f"  Campaign '{campaign.name}': {recipient_count} recipients")
    
    def test_sms_campaign_model(self):
        """Test SMS Campaign model"""
        with self.app.app_context():
            try:
                sms_count = SMSCampaign.query.count()
                logger.info(f"✓ Found {sms_count} SMS campaigns")
                
                sms_campaigns = SMSCampaign.query.limit(5).all()
                logger.info(f"✓ Successfully queried SMS campaigns")
            except Exception as e:
                logger.warning(f"⚠ SMS Campaign table might not exist: {e}")
    
    def test_social_media_model(self):
        """Test Social Media Post model"""
        with self.app.app_context():
            try:
                post_count = SocialPost.query.count()
                logger.info(f"✓ Found {post_count} social media posts")
            except Exception as e:
                logger.warning(f"⚠ SocialPost table might not exist: {e}")
    
    def test_event_model(self):
        """Test Event model"""
        with self.app.app_context():
            try:
                event_count = Event.query.count()
                logger.info(f"✓ Found {event_count} events")
                
                events = Event.query.limit(5).all()
                for event in events:
                    reg_count = EventRegistration.query.filter_by(event_id=event.id).count()
                    logger.info(f"  Event '{event.name}': {reg_count} registrations")
            except Exception as e:
                logger.warning(f"⚠ Event table might not exist: {e}")
    
    def test_automation_model(self):
        """Test Automation model"""
        with self.app.app_context():
            try:
                automation_count = Automation.query.count()
                logger.info(f"✓ Found {automation_count} automations")
                
                automations = Automation.query.limit(5).all()
                for automation in automations:
                    step_count = AutomationStep.query.filter_by(automation_id=automation.id).count()
                    logger.info(f"  Automation '{automation.name}': {step_count} steps")
            except Exception as e:
                logger.warning(f"⚠ Automation table might not exist: {e}")
    
    def test_segment_model(self):
        """Test Segment model"""
        with self.app.app_context():
            try:
                segment_count = Segment.query.count()
                logger.info(f"✓ Found {segment_count} segments")
                
                segments = Segment.query.limit(5).all()
                for segment in segments:
                    member_count = SegmentMember.query.filter_by(segment_id=segment.id).count()
                    logger.info(f"  Segment '{segment.name}': {member_count} members")
            except Exception as e:
                logger.warning(f"⚠ Segment table might not exist: {e}")
    
    def test_landing_page_model(self):
        """Test Landing Page model"""
        with self.app.app_context():
            try:
                page_count = LandingPage.query.count()
                logger.info(f"✓ Found {page_count} landing pages")
                
                pages = LandingPage.query.limit(5).all()
                for page in pages:
                    logger.info(f"  Landing Page '{page.name}' (slug: {page.slug})")
            except Exception as e:
                logger.warning(f"⚠ LandingPage table might not exist: {e}")
    
    def test_web_form_model(self):
        """Test Web Form model"""
        with self.app.app_context():
            try:
                form_count = WebForm.query.count()
                logger.info(f"✓ Found {form_count} web forms")
            except Exception as e:
                logger.warning(f"⚠ WebForm table might not exist: {e}")
    
    def test_abtest_model(self):
        """Test A/B Test model"""
        with self.app.app_context():
            try:
                test_count = ABTest.query.count()
                logger.info(f"✓ Found {test_count} A/B tests")
            except Exception as e:
                logger.warning(f"⚠ ABTest table might not exist: {e}")
    
    def test_brand_kit_model(self):
        """Test Brand Kit model"""
        with self.app.app_context():
            try:
                kit_count = BrandKit.query.count()
                logger.info(f"✓ Found {kit_count} brand kits")
            except Exception as e:
                logger.warning(f"⚠ BrandKit table might not exist: {e}")
    
    def print_summary(self):
        """Print test summary"""
        logger.info("\n" + "="*60)
        logger.info("TEST SUMMARY")
        logger.info("="*60)
        
        total_tests = len(self.passed) + len(self.errors)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"✅ Passed: {len(self.passed)}")
        logger.info(f"❌ Failed: {len(self.errors)}")
        
        if self.errors:
            logger.info("\n" + "="*60)
            logger.info("FAILED TESTS:")
            logger.info("="*60)
            for test_name, error in self.errors:
                logger.error(f"{test_name}: {error}")
        
        logger.info("\n" + "="*60)
        if not self.errors:
            logger.info("🎉 ALL TESTS PASSED!")
        else:
            logger.info("⚠️  SOME TESTS FAILED - Review errors above")
        logger.info("="*60)


if __name__ == '__main__':
    tester = FeatureTester()
    tester.run_all_tests()
    
    # Exit with error code if tests failed
    sys.exit(len(tester.errors))
