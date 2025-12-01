from datetime import datetime
from app import db
from flask_login import UserMixin
from sqlalchemy import JSON, Text

user_company = db.Table('user_company',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('company_id', db.Integer, db.ForeignKey('company.id'), primary_key=True),
    db.Column('is_default', db.Boolean, default=False),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    
    # User Profile Fields (like Contact)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    phone = db.Column(db.String(20))
    avatar_path = db.Column(db.String(255))
    tags = db.Column(db.String(255))  # Comma-separated tags including 'admin'
    segment = db.Column(db.String(100), default='user')  # user, admin, moderator, etc.
    custom_fields = db.Column(JSON)  # Additional custom profile data
    engagement_score = db.Column(db.Float, default=0.0)
    last_activity = db.Column(db.DateTime)
    bio = db.Column(db.Text)  # User bio/description
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    companies = db.relationship('Company', secondary=user_company, backref=db.backref('users', lazy='dynamic'))
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or self.username
    
    @property
    def is_admin_user(self):
        """Check if user has admin segment or admin tag"""
        return self.is_admin or self.segment == 'admin' or (self.tags and 'admin' in self.tags.lower())
    
    def add_tag(self, tag):
        """Add a tag to the user"""
        if not self.tags:
            self.tags = tag
        elif tag not in self.tags:
            self.tags += f",{tag}"
    
    def has_tag(self, tag):
        """Check if user has a specific tag"""
        return self.tags and tag.lower() in self.tags.lower()
    
    def get_default_company(self):
        """Get the user's default company"""
        result = db.session.execute(
            db.select(user_company).where(
                user_company.c.user_id == self.id,
                user_company.c.is_default == True
            )
        ).first()
        if result:
            return Company.query.get(result.company_id)
        companies_list = list(self.companies)
        return companies_list[0] if companies_list else None

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    logo_path = db.Column(db.String(255))
    icon_path = db.Column(db.String(255))
    website_url = db.Column(db.String(255))
    
    # Brand Customization
    primary_color = db.Column(db.String(7), default='#bc00ed')  # Purple
    secondary_color = db.Column(db.String(7), default='#00ffb4')  # Teal
    accent_color = db.Column(db.String(7), default='#e4055c')  # Pink
    font_family = db.Column(db.String(100), default='Inter, sans-serif')
    
    # Configuration stored as JSON for flexibility
    env_config = db.Column(JSON)  # Stores environment-specific configs
    social_accounts = db.Column(JSON)  # Social media account details
    email_config = db.Column(JSON)  # Email settings (from, reply-to, etc.)
    api_keys = db.Column(JSON)  # API keys and secrets (encrypted)
    
    # Brand Kit association
    brandkit_id = db.Column(db.Integer, db.ForeignKey('brand_kit.id'))
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Company {self.name}>'
    
    @property
    def user_count(self):
        return db.session.execute(
            db.select(db.func.count(user_company.c.user_id)).where(
                user_company.c.company_id == self.id
            )
        ).scalar()

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    company = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    tags = db.Column(db.String(255))  # Comma-separated tags
    segment = db.Column(db.String(100), default='lead')  # lead, customer, newsletter, vip, etc.
    custom_fields = db.Column(JSON)  # Additional custom data
    engagement_score = db.Column(db.Float, default=0.0)
    last_activity = db.Column(db.DateTime)
    source = db.Column(db.String(50))  # web_form, manual, import, api, forminator
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaign_recipients = db.relationship('CampaignRecipient', backref='contact', lazy='dynamic')
    segment_members = db.relationship('SegmentMember', backref='contact', lazy='dynamic')
    
    def __repr__(self):
        return f'<Contact {self.email}>'
    
    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or self.email

class EmailTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    html_content = db.Column(Text, nullable=False)
    template_type = db.Column(db.String(20), default='custom')  # custom, automation, branded
    brandkit_id = db.Column(db.Integer, db.ForeignKey('brand_kit.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaigns = db.relationship('Campaign', backref='template', lazy='dynamic')
    components = db.relationship('EmailComponent', backref='template', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<EmailTemplate {self.name}>'

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('email_template.id'))
    automation_id = db.Column(db.Integer, db.ForeignKey('automation.id'))
    ab_test_id = db.Column(db.Integer, db.ForeignKey('ab_test.id'))
    status = db.Column(db.String(20), default='draft')  # draft, scheduled, sending, sent, paused
    scheduled_at = db.Column(db.DateTime)
    sent_at = db.Column(db.DateTime)
    revenue_generated = db.Column(db.Float, default=0.0)
    utm_keyword = db.Column(db.String(100))  # UTM tracking keyword
    ai_generated = db.Column(db.Boolean, default=False)  # Track AI-generated campaigns (v4.1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    recipients = db.relationship('CampaignRecipient', backref='campaign', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Campaign {self.name}>'
    
    @property
    def total_recipients(self):
        return self.recipients.count()
    
    @property
    def sent_count(self):
        return self.recipients.filter_by(status='sent').count()
    
    @property
    def failed_count(self):
        return self.recipients.filter_by(status='failed').count()
    
    @property
    def pending_count(self):
        return self.recipients.filter_by(status='pending').count()

class CampaignRecipient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    variant = db.Column(db.String(1))  # For A/B testing: 'A' or 'B'
    status = db.Column(db.String(20), default='pending')  # pending, sent, failed, bounced
    sent_at = db.Column(db.DateTime)
    opened_at = db.Column(db.DateTime)
    clicked_at = db.Column(db.DateTime)
    error_message = db.Column(Text)
    
    def __repr__(self):
        return f'<CampaignRecipient {self.campaign_id}:{self.contact_id}>'

class EmailTracking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    event_type = db.Column(db.String(20), nullable=False)  # sent, delivered, opened, clicked, bounced
    event_data = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<EmailTracking {self.event_type}>'

# BrandKit System
class BrandKit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    logo_url = db.Column(db.String(255))
    primary_color = db.Column(db.String(7))  # Hex color
    secondary_color = db.Column(db.String(7))
    accent_color = db.Column(db.String(7))
    primary_font = db.Column(db.String(50))
    secondary_font = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_default = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<BrandKit {self.name}>'

# Automation Templates & Advanced Features
class AutomationTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(Text)
    category = db.Column(db.String(50))  # welcome, ecommerce, engagement, nurture
    template_data = db.Column(JSON)  # Complete automation workflow template
    is_predefined = db.Column(db.Boolean, default=False)  # System templates vs user-created
    usage_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AutomationTemplate {self.name}>'

class AutomationExecution(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    automation_id = db.Column(db.Integer, db.ForeignKey('automation.id'), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    current_step = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='active')  # active, completed, paused, failed
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    next_action_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<AutomationExecution {self.automation_id}:{self.contact_id}>'

class AutomationAction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    execution_id = db.Column(db.Integer, db.ForeignKey('automation_execution.id'), nullable=False)
    step_id = db.Column(db.Integer, db.ForeignKey('automation_step.id'), nullable=False)
    action_type = db.Column(db.String(50))  # email_sent, sms_sent, wait_completed, condition_met
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed, skipped
    executed_at = db.Column(db.DateTime)
    result_data = db.Column(JSON)
    error_message = db.Column(Text)
    
    def __repr__(self):
        return f'<AutomationAction {self.action_type}>'

# Landing Pages & Enhanced Web Forms  
class LandingPage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(200))
    slug = db.Column(db.String(100), unique=True)  # URL-friendly name
    html_content = db.Column(Text)
    css_styles = db.Column(Text)
    meta_description = db.Column(db.String(160))
    form_id = db.Column(db.Integer, db.ForeignKey('web_form.id'))
    is_published = db.Column(db.Boolean, default=False)
    page_views = db.Column(db.Integer, default=0)
    conversions = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    published_at = db.Column(db.DateTime)
    
    # Relationships
    form = db.relationship('WebForm', backref='landing_pages')
    
    def __repr__(self):
        return f'<LandingPage {self.name}>'

class NewsletterArchive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    title = db.Column(db.String(200))
    slug = db.Column(db.String(100), unique=True)
    html_content = db.Column(Text)
    published_at = db.Column(db.DateTime, default=datetime.utcnow)
    view_count = db.Column(db.Integer, default=0)
    is_public = db.Column(db.Boolean, default=True)
    
    # Relationships
    campaign = db.relationship('Campaign', backref='archive_entry')
    
    def __repr__(self):
        return f'<NewsletterArchive {self.title}>'

# Enhanced Email Automation Features
class NonOpenerResend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    resend_campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'))
    hours_after_original = db.Column(db.Integer, default=24)
    new_subject_line = db.Column(db.String(255))
    status = db.Column(db.String(20), default='scheduled')  # scheduled, sent, cancelled
    scheduled_at = db.Column(db.DateTime)
    sent_at = db.Column(db.DateTime)
    recipient_count = db.Column(db.Integer, default=0)
    
    # Relationships
    original_campaign = db.relationship('Campaign', foreign_keys=[original_campaign_id], backref='non_opener_resends')
    resend_campaign = db.relationship('Campaign', foreign_keys=[resend_campaign_id])
    
    def __repr__(self):
        return f'<NonOpenerResend {self.original_campaign_id}>'

# Drag & Drop Email Builder
class EmailComponent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('email_template.id'))
    component_type = db.Column(db.String(50), nullable=False)  # text, image, button, divider, social
    content = db.Column(JSON)  # Component configuration and content
    position = db.Column(db.Integer, default=0)  # Order in template
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<EmailComponent {self.component_type}>'

# Polls & Surveys
class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'))
    question = db.Column(db.String(500), nullable=False)
    poll_type = db.Column(db.String(20), default='multiple_choice')  # multiple_choice, rating, text
    options = db.Column(JSON)  # Poll options
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    responses = db.relationship('PollResponse', backref='poll', lazy='dynamic')
    
    def __repr__(self):
        return f'<Poll {self.question[:50]}>'

class PollResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    response_data = db.Column(JSON)  # Answer data
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PollResponse {self.poll_id}:{self.contact_id}>'

# A/B Testing
class ABTest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    test_type = db.Column(db.String(20), default='subject_line')  # subject_line, content, send_time
    variant_a = db.Column(Text)  # First variant
    variant_b = db.Column(Text)  # Second variant
    split_ratio = db.Column(db.Float, default=0.5)  # 50/50 split
    winner = db.Column(db.String(1))  # 'A', 'B', or NULL if undecided
    status = db.Column(db.String(20), default='draft')  # draft, running, completed
    started_at = db.Column(db.DateTime)
    ended_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ABTest {self.test_type}>'

# Automation Workflows
class Automation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(Text)
    trigger_type = db.Column(db.String(50))  # signup, purchase, birthday, custom
    trigger_conditions = db.Column(JSON)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    steps = db.relationship('AutomationStep', backref='automation', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Automation {self.name}>'

class AutomationStep(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    automation_id = db.Column(db.Integer, db.ForeignKey('automation.id'), nullable=False)
    step_type = db.Column(db.String(20))  # email, sms, wait, condition
    step_order = db.Column(db.Integer, default=0)
    template_id = db.Column(db.Integer, db.ForeignKey('email_template.id'))
    delay_hours = db.Column(db.Integer, default=0)
    conditions = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AutomationStep {self.step_type}>'

# SMS Marketing
class SMSCampaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    message = db.Column(db.String(160), nullable=False)  # SMS character limit
    status = db.Column(db.String(20), default='draft')
    scheduled_at = db.Column(db.DateTime)
    sent_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    recipients = db.relationship('SMSRecipient', backref='campaign', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<SMSCampaign {self.name}>'

class SMSRecipient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('sms_campaign.id'), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    sent_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    error_message = db.Column(Text)
    
    def __repr__(self):
        return f'<SMSRecipient {self.campaign_id}:{self.contact_id}>'

class SMSTemplate(db.Model):
    """Reusable SMS message templates"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    message = db.Column(db.String(160), nullable=False)
    category = db.Column(db.String(50), default='promotional')
    tone = db.Column(db.String(50), default='professional')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SMSTemplate {self.name}>'

# Social Media Marketing
class SocialPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(Text, nullable=False)
    platforms = db.Column(JSON)  # ['facebook', 'instagram', 'linkedin']
    media_urls = db.Column(JSON)  # Image/video URLs
    status = db.Column(db.String(20), default='draft')  # draft, scheduled, published, failed
    scheduled_at = db.Column(db.DateTime)
    published_at = db.Column(db.DateTime)
    engagement_data = db.Column(JSON)  # Likes, shares, comments
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SocialPost {self.content[:50]}>'

# Contact Segmentation
class Segment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(Text)
    segment_type = db.Column(db.String(20), default='behavioral')  # behavioral, demographic, engagement
    conditions = db.Column(JSON)  # Segmentation rules
    is_dynamic = db.Column(db.Boolean, default=True)  # Auto-update based on conditions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    members = db.relationship('SegmentMember', backref='segment', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Segment {self.name}>'

class SegmentMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    segment_id = db.Column(db.Integer, db.ForeignKey('segment.id'), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SegmentMember {self.segment_id}:{self.contact_id}>'

# Web Signup Forms
class WebForm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(200))
    description = db.Column(Text)
    fields = db.Column(JSON)  # Form field configuration
    success_message = db.Column(Text)
    redirect_url = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    submissions = db.relationship('FormSubmission', backref='form', lazy='dynamic')
    
    def __repr__(self):
        return f'<WebForm {self.name}>'

class FormSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    form_id = db.Column(db.Integer, db.ForeignKey('web_form.id'), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'))
    form_data = db.Column(JSON)  # Submitted form data
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<FormSubmission {self.form_id}>'

# Events & Registration
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(Text)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    location = db.Column(db.String(255))
    max_attendees = db.Column(db.Integer)
    price = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    registrations = db.relationship('EventRegistration', backref='event', lazy='dynamic')
    
    def __repr__(self):
        return f'<Event {self.name}>'

class EventRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    status = db.Column(db.String(20), default='registered')  # registered, attended, cancelled
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, refunded
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<EventRegistration {self.event_id}:{self.contact_id}>'

# Products & Services
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wc_product_id = db.Column(db.Integer, unique=True)  # WooCommerce product ID
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(Text)
    price = db.Column(db.Float, nullable=False)
    sku = db.Column(db.String(50))
    category = db.Column(db.String(100))
    image_url = db.Column(db.String(255))
    product_url = db.Column(db.String(255))  # WooCommerce product permalink
    stock_quantity = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_synced = db.Column(db.DateTime)  # Last WooCommerce sync
    
    # Relationships
    orders = db.relationship('Order', backref='product', lazy='dynamic')
    
    def __repr__(self):
        return f'<Product {self.name}>'

# Revenue Tracking
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'))  # Attribution
    order_number = db.Column(db.String(50), unique=True)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, completed, refunded
    payment_method = db.Column(db.String(50))
    stripe_payment_id = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Order {self.order_number}>'

# Marketing Calendar
class CalendarEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(Text)
    event_type = db.Column(db.String(20))  # campaign, social_post, event, task
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'))
    social_post_id = db.Column(db.Integer, db.ForeignKey('social_post.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CalendarEvent {self.title}>'

# AI Agent System
class AgentTask(db.Model):
    """Tasks for AI agents to execute"""
    id = db.Column(db.Integer, primary_key=True)
    agent_type = db.Column(db.String(50), nullable=False)  # brand_strategy, content_seo, etc.
    agent_name = db.Column(db.String(100), nullable=False)
    task_name = db.Column(db.String(200), nullable=False)
    task_data = db.Column(JSON)  # Task parameters and configuration
    status = db.Column(db.String(20), default='pending')  # pending, running, completed, failed
    result = db.Column(JSON)  # Task execution result
    scheduled_at = db.Column(db.DateTime, nullable=False)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AgentTask {self.agent_name}:{self.task_name}>'

class AgentLog(db.Model):
    """Activity logs for AI agents"""
    id = db.Column(db.Integer, primary_key=True)
    agent_type = db.Column(db.String(50), nullable=False)
    agent_name = db.Column(db.String(100), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)  # content_generation, analysis, optimization, etc.
    details = db.Column(JSON)  # Activity details and metadata
    status = db.Column(db.String(20), default='success')  # success, error, warning
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AgentLog {self.agent_name}:{self.activity_type}>'

class AgentReport(db.Model):
    """Generated reports from AI agents"""
    id = db.Column(db.Integer, primary_key=True)
    agent_type = db.Column(db.String(50), nullable=False)
    agent_name = db.Column(db.String(100), nullable=False)
    report_type = db.Column(db.String(50), nullable=False)  # weekly, monthly, quarterly, campaign
    report_title = db.Column(db.String(200), nullable=False)
    report_data = db.Column(JSON)  # Report content and insights
    insights = db.Column(Text)  # AI-generated insights and recommendations
    period_start = db.Column(db.DateTime)
    period_end = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AgentReport {self.report_title}>'

class AgentSchedule(db.Model):
    """Scheduling configuration for AI agents"""
    id = db.Column(db.Integer, primary_key=True)
    agent_type = db.Column(db.String(50), nullable=False, unique=True)
    agent_name = db.Column(db.String(100), nullable=False)
    is_enabled = db.Column(db.Boolean, default=True)
    schedule_type = db.Column(db.String(20), nullable=False)  # cron, interval, daily, weekly, monthly
    schedule_config = db.Column(JSON)  # Cron expression or interval config
    last_run = db.Column(db.DateTime)
    next_run = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<AgentSchedule {self.agent_name}>'

# SEO & Analytics Module (Phase 2)
class SEOKeyword(db.Model):
    """Track keyword rankings and performance"""
    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(255), nullable=False)
    target_url = db.Column(db.String(500))
    search_volume = db.Column(db.Integer, default=0)
    difficulty = db.Column(db.Integer, default=0)  # 0-100 scale
    current_position = db.Column(db.Integer)
    previous_position = db.Column(db.Integer)
    best_position = db.Column(db.Integer)
    search_engine = db.Column(db.String(20), default='google')  # google, bing, yahoo
    location = db.Column(db.String(100), default='US')
    device = db.Column(db.String(20), default='desktop')  # desktop, mobile
    is_tracking = db.Column(db.Boolean, default=True)
    last_checked = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    rankings = db.relationship('KeywordRanking', backref='keyword', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<SEOKeyword {self.keyword}>'

class KeywordRanking(db.Model):
    """Historical ranking data for keywords"""
    id = db.Column(db.Integer, primary_key=True)
    keyword_id = db.Column(db.Integer, db.ForeignKey('seo_keyword.id'), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    url = db.Column(db.String(500))
    impressions = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)
    ctr = db.Column(db.Float, default=0.0)
    checked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<KeywordRanking {self.keyword_id}:{self.position}>'

class SEOBacklink(db.Model):
    """Monitor backlinks to the site"""
    id = db.Column(db.Integer, primary_key=True)
    source_url = db.Column(db.String(500), nullable=False)
    source_domain = db.Column(db.String(255))
    target_url = db.Column(db.String(500), nullable=False)
    anchor_text = db.Column(db.String(255))
    link_type = db.Column(db.String(20), default='dofollow')  # dofollow, nofollow
    status = db.Column(db.String(20), default='active')  # active, lost, broken
    domain_authority = db.Column(db.Integer, default=0)
    page_authority = db.Column(db.Integer, default=0)
    spam_score = db.Column(db.Integer, default=0)
    first_seen = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    lost_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SEOBacklink {self.source_domain}>'

class SEOCompetitor(db.Model):
    """Track competitor SEO performance"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    domain = db.Column(db.String(255), nullable=False, unique=True)
    organic_traffic = db.Column(db.Integer, default=0)
    organic_keywords = db.Column(db.Integer, default=0)
    backlinks = db.Column(db.Integer, default=0)
    domain_authority = db.Column(db.Integer, default=0)
    page_authority = db.Column(db.Integer, default=0)
    notes = db.Column(Text)
    is_active = db.Column(db.Boolean, default=True)
    last_analyzed = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    snapshots = db.relationship('CompetitorSnapshot', backref='competitor', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<SEOCompetitor {self.name}>'

class CompetitorSnapshot(db.Model):
    """Historical snapshots of competitor metrics"""
    id = db.Column(db.Integer, primary_key=True)
    competitor_id = db.Column(db.Integer, db.ForeignKey('seo_competitor.id'), nullable=False)
    organic_traffic = db.Column(db.Integer, default=0)
    organic_keywords = db.Column(db.Integer, default=0)
    backlinks = db.Column(db.Integer, default=0)
    domain_authority = db.Column(db.Integer, default=0)
    top_keywords = db.Column(JSON)  # List of top performing keywords
    snapshot_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CompetitorSnapshot {self.competitor_id}>'

class SEOAudit(db.Model):
    """Site audit results and recommendations"""
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False)
    audit_type = db.Column(db.String(50), default='full')  # full, quick, technical, content
    overall_score = db.Column(db.Integer, default=0)  # 0-100
    technical_score = db.Column(db.Integer, default=0)
    content_score = db.Column(db.Integer, default=0)
    performance_score = db.Column(db.Integer, default=0)
    mobile_score = db.Column(db.Integer, default=0)
    issues_found = db.Column(JSON)  # List of issues with severity
    recommendations = db.Column(JSON)  # AI-generated recommendations
    audit_data = db.Column(JSON)  # Full audit details
    status = db.Column(db.String(20), default='completed')  # pending, running, completed, failed
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SEOAudit {self.url}:{self.overall_score}>'

class SEOPage(db.Model):
    """Individual page SEO metrics"""
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(500), nullable=False, unique=True)
    title = db.Column(db.String(255))
    meta_description = db.Column(db.String(500))
    h1_tag = db.Column(db.String(255))
    word_count = db.Column(db.Integer, default=0)
    internal_links = db.Column(db.Integer, default=0)
    external_links = db.Column(db.Integer, default=0)
    images_count = db.Column(db.Integer, default=0)
    images_without_alt = db.Column(db.Integer, default=0)
    page_speed = db.Column(db.Integer, default=0)  # Google PageSpeed score
    mobile_friendly = db.Column(db.Boolean, default=True)
    schema_markup = db.Column(JSON)  # Structured data found
    canonical_url = db.Column(db.String(500))
    status_code = db.Column(db.Integer, default=200)
    last_crawled = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SEOPage {self.url}>'

# Event Enhancements (Phase 3)
class EventTicket(db.Model):
    """Ticket types for events"""
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # VIP, General, Early Bird
    description = db.Column(Text)
    price = db.Column(db.Float, nullable=False)
    quantity_total = db.Column(db.Integer, nullable=False)
    quantity_sold = db.Column(db.Integer, default=0)
    sale_start = db.Column(db.DateTime)
    sale_end = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    event = db.relationship('Event', backref='tickets', foreign_keys=[event_id])
    purchases = db.relationship('TicketPurchase', backref='ticket', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def quantity_available(self):
        return self.quantity_total - self.quantity_sold
    
    def __repr__(self):
        return f'<EventTicket {self.name}>'

class TicketPurchase(db.Model):
    """Individual ticket purchases"""
    id = db.Column(db.Integer, primary_key=True)
    ticket_id = db.Column(db.Integer, db.ForeignKey('event_ticket.id'), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    total_amount = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, refunded, failed
    payment_method = db.Column(db.String(50))
    transaction_id = db.Column(db.String(100))
    ticket_codes = db.Column(JSON)  # Array of unique ticket codes
    checked_in = db.Column(db.Boolean, default=False)
    check_in_time = db.Column(db.DateTime)
    purchased_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    contact = db.relationship('Contact', backref='ticket_purchases')
    
    def __repr__(self):
        return f'<TicketPurchase {self.id}>'

class EventCheckIn(db.Model):
    """Track event check-ins"""
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    ticket_purchase_id = db.Column(db.Integer, db.ForeignKey('ticket_purchase.id'))
    check_in_method = db.Column(db.String(50), default='manual')  # manual, qr_code, email
    checked_in_by = db.Column(db.String(100))  # Staff member name
    checked_in_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(Text)
    
    def __repr__(self):
        return f'<EventCheckIn {self.event_id}:{self.contact_id}>'

# Social Media Expansion (Phase 4)
class SocialMediaAccount(db.Model):
    """Connected social media accounts"""
    id = db.Column(db.Integer, primary_key=True)
    platform = db.Column(db.String(50), nullable=False)  # twitter, instagram, facebook, telegram, tiktok, reddit
    account_name = db.Column(db.String(100), nullable=False)
    account_id = db.Column(db.String(100))  # Platform-specific ID
    access_token = db.Column(db.String(500))
    refresh_token = db.Column(db.String(500))
    token_expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    follower_count = db.Column(db.Integer, default=0)
    last_synced = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    scheduled_posts = db.relationship('SocialMediaSchedule', backref='account', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<SocialMediaAccount {self.platform}:{self.account_name}>'

class SocialMediaSchedule(db.Model):
    """Scheduled social media posts"""
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('social_media_account.id'), nullable=False)
    content = db.Column(Text, nullable=False)
    media_urls = db.Column(JSON)  # Array of image/video URLs
    hashtags = db.Column(db.String(500))
    scheduled_for = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, published, failed, cancelled
    post_id = db.Column(db.String(100))  # Platform post ID after publishing
    engagement_metrics = db.Column(JSON)  # Likes, comments, shares, etc.
    posted_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SocialMediaSchedule {self.account_id}:{self.scheduled_for}>'

class SocialMediaCrossPost(db.Model):
    """Cross-posting to multiple platforms"""
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(Text, nullable=False)
    media_urls = db.Column(JSON)
    platforms = db.Column(JSON)  # List of platforms to post to
    scheduled_for = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')
    post_results = db.Column(JSON)  # Results for each platform
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<SocialMediaCrossPost {self.id}>'

# Advanced Automations (Phase 5)
class AutomationTest(db.Model):
    """Test mode for automations"""
    id = db.Column(db.Integer, primary_key=True)
    automation_id = db.Column(db.Integer, db.ForeignKey('automation.id'), nullable=False)
    test_contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'))
    test_data = db.Column(JSON)  # Test parameters
    test_results = db.Column(JSON)  # Step-by-step results
    status = db.Column(db.String(20), default='pending')  # pending, running, completed, failed
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AutomationTest {self.automation_id}>'

class AutomationTriggerLibrary(db.Model):
    """Pre-built automation triggers"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    trigger_type = db.Column(db.String(50), nullable=False)
    description = db.Column(Text)
    category = db.Column(db.String(50))  # ecommerce, engagement, nurture, retention
    trigger_config = db.Column(JSON)  # Pre-configured trigger settings
    steps_template = db.Column(JSON)  # Suggested automation steps
    is_predefined = db.Column(db.Boolean, default=True)
    usage_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AutomationTriggerLibrary {self.name}>'

class AutomationABTest(db.Model):
    """A/B testing within automations"""
    id = db.Column(db.Integer, primary_key=True)
    automation_id = db.Column(db.Integer, db.ForeignKey('automation.id'), nullable=False)
    step_id = db.Column(db.Integer, db.ForeignKey('automation_step.id'), nullable=False)
    variant_a_template_id = db.Column(db.Integer, db.ForeignKey('email_template.id'))
    variant_b_template_id = db.Column(db.Integer, db.ForeignKey('email_template.id'))
    split_percentage = db.Column(db.Integer, default=50)  # % for variant A
    winner_criteria = db.Column(db.String(50), default='open_rate')  # open_rate, click_rate, conversion
    status = db.Column(db.String(20), default='running')  # running, completed, paused
    variant_a_sent = db.Column(db.Integer, default=0)
    variant_b_sent = db.Column(db.Integer, default=0)
    variant_a_opens = db.Column(db.Integer, default=0)
    variant_b_opens = db.Column(db.Integer, default=0)
    variant_a_clicks = db.Column(db.Integer, default=0)
    variant_b_clicks = db.Column(db.Integer, default=0)
    winner_variant = db.Column(db.String(1))  # 'A' or 'B'
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<AutomationABTest {self.automation_id}:{self.step_id}>'

# Revenue & Attribution Tracking (v4.1)
class UTMLink(db.Model):
    """Track UTM campaign links"""
    id = db.Column(db.Integer, primary_key=True)
    campaign_name = db.Column(db.String(200))
    base_url = db.Column(db.String(500), nullable=False)
    full_url = db.Column(Text, nullable=False)
    short_url = db.Column(db.String(100))
    utm_source = db.Column(db.String(100), nullable=False)
    utm_medium = db.Column(db.String(100), nullable=False)
    utm_campaign = db.Column(db.String(200), nullable=False)
    utm_term = db.Column(db.String(200))
    utm_content = db.Column(db.String(200))
    clicks = db.Column(db.Integer, default=0)
    conversions = db.Column(db.Integer, default=0)
    revenue = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __repr__(self):
        return f'<UTMLink {self.utm_campaign}>'

class UTMTemplate(db.Model):
    """Saved UTM parameter templates"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    utm_source = db.Column(db.String(100))
    utm_medium = db.Column(db.String(100))
    utm_campaign = db.Column(db.String(200))
    utm_term = db.Column(db.String(200))
    utm_content = db.Column(db.String(200))
    usage_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __repr__(self):
        return f'<UTMTemplate {self.name}>'

class AttributionTouch(db.Model):
    """Track customer attribution touchpoints"""
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    session_id = db.Column(db.String(100))
    touchpoint_type = db.Column(db.String(50))  # email, social, ad, organic, direct, referral
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'))
    utm_source = db.Column(db.String(100))
    utm_medium = db.Column(db.String(100))
    utm_campaign = db.Column(db.String(200))
    page_url = db.Column(Text)
    referrer_url = db.Column(Text)
    device_type = db.Column(db.String(50))
    occurred_at = db.Column(db.DateTime, default=datetime.utcnow)
    position = db.Column(db.Integer)  # Touch sequence (1 = first, N = last)
    
    # Relationships
    contact = db.relationship('Contact', backref='attribution_touches')
    
    def __repr__(self):
        return f'<AttributionTouch {self.contact_id}:{self.touchpoint_type}>'

class ConversionEvent(db.Model):
    """Track conversion events"""
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)  # purchase, signup, download, etc.
    event_value = db.Column(db.Float, default=0.0)  # Revenue or value
    session_id = db.Column(db.String(100))
    utm_source = db.Column(db.String(100))
    utm_medium = db.Column(db.String(100))
    utm_campaign = db.Column(db.String(200))
    attributed_campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'))
    attribution_model = db.Column(db.String(50))  # first_touch, last_touch, linear, time_decay
    occurred_at = db.Column(db.DateTime, default=datetime.utcnow)
    event_metadata = db.Column(JSON)  # Additional event data
    
    # Relationships
    contact = db.relationship('Contact', backref='conversions')
    
    def __repr__(self):
        return f'<ConversionEvent {self.event_type}:{self.event_value}>'

class CustomerSegment(db.Model):
    """Customer RFM segmentation"""
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False, unique=True)
    rfm_score = db.Column(db.String(3))  # e.g., "555" for R=5, F=5, M=5
    recency_score = db.Column(db.Integer)
    frequency_score = db.Column(db.Integer)
    monetary_score = db.Column(db.Integer)
    segment_name = db.Column(db.String(50))  # Champions, Loyal, At Risk, etc.
    ltv = db.Column(db.Float, default=0.0)
    predicted_ltv = db.Column(db.Float, default=0.0)
    last_calculated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    contact = db.relationship('Contact', backref=db.backref('rfm_segment', uselist=False))
    
    def __repr__(self):
        return f'<CustomerSegment {self.segment_name}:{self.rfm_score}>'

# Affiliate & Influencer Management (v4.1 Stage 4)
class AffiliateLink(db.Model):
    """Store affiliate link metadata for accurate tracking"""
    id = db.Column(db.Integer, primary_key=True)
    tracking_code = db.Column(db.String(50), nullable=False, unique=True, index=True)
    affiliate_id = db.Column(db.Integer, nullable=False, index=True)
    product_url = db.Column(db.Text, nullable=False)
    campaign_name = db.Column(db.String(200))
    commission_rate = db.Column(db.Float, default=10.0)
    commission_type = db.Column(db.String(20), default='percentage')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<AffiliateLink {self.tracking_code}:{self.affiliate_id}>'

class AffiliateClick(db.Model):
    """Track affiliate link clicks"""
    id = db.Column(db.Integer, primary_key=True)
    tracking_code = db.Column(db.String(50), nullable=False, index=True)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))
    referrer = db.Column(db.String(500))
    clicked_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<AffiliateClick {self.tracking_code}>'

class AffiliateConversion(db.Model):
    """Track affiliate conversions and commissions"""
    id = db.Column(db.Integer, primary_key=True)
    tracking_code = db.Column(db.String(50), nullable=False, index=True)
    affiliate_id = db.Column(db.Integer, nullable=False, index=True)
    sale_amount = db.Column(db.Float, default=0.0)
    commission_amount = db.Column(db.Float, default=0.0)
    order_id = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')  # pending, approved, paid, rejected
    converted_at = db.Column(db.DateTime, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<AffiliateConversion {self.tracking_code}:${self.commission_amount}>'

class AffiliatePayout(db.Model):
    """Track affiliate commission payouts"""
    id = db.Column(db.Integer, primary_key=True)
    affiliate_id = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_method = db.Column(db.String(50))  # paypal, bank, crypto
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    notes = db.Column(db.Text)
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<AffiliatePayout {self.affiliate_id}:${self.amount}>'

class Influencer(db.Model):
    """Influencer profiles and contact information"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200))
    instagram_handle = db.Column(db.String(100))
    tiktok_handle = db.Column(db.String(100))
    youtube_channel = db.Column(db.String(200))
    twitter_handle = db.Column(db.String(100))
    niche = db.Column(db.String(100))  # beauty, fitness, tech, lifestyle, etc.
    follower_count = db.Column(db.Integer, default=0)
    engagement_rate = db.Column(db.Float, default=0.0)
    tier = db.Column(db.String(20))  # nano, micro, mid, macro, mega
    status = db.Column(db.String(20), default='prospect')  # prospect, active, inactive, blocked
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Influencer {self.name}>'

class InfluencerContract(db.Model):
    """Influencer contracts and agreements"""
    id = db.Column(db.Integer, primary_key=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False)
    campaign_name = db.Column(db.String(200))
    deliverables = db.Column(JSON)  # List of required content pieces
    compensation_type = db.Column(db.String(20))  # fixed, commission, product, hybrid
    compensation_amount = db.Column(db.Float, default=0.0)
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    content_guidelines = db.Column(db.Text)
    exclusivity_clause = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='draft')  # draft, active, completed, cancelled
    signed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    influencer = db.relationship('Influencer', backref='contracts')
    
    def __repr__(self):
        return f'<InfluencerContract {self.campaign_name}>'

class InfluencerContent(db.Model):
    """Track influencer content performance"""
    id = db.Column(db.Integer, primary_key=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False)
    contract_id = db.Column(db.Integer, db.ForeignKey('influencer_contract.id'))
    platform = db.Column(db.String(50))  # instagram, tiktok, youtube, twitter
    content_type = db.Column(db.String(50))  # post, story, reel, video, tweet
    content_url = db.Column(db.String(500))
    posted_at = db.Column(db.DateTime)
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    comments = db.Column(db.Integer, default=0)
    shares = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)
    conversions = db.Column(db.Integer, default=0)
    engagement_rate = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    influencer = db.relationship('Influencer', backref='content')
    
    def __repr__(self):
        return f'<InfluencerContent {self.platform}:{self.content_type}>'

# Advanced Workflow Builder (v4.1 Stage 5)
class WorkflowAutomation(db.Model):
    """Advanced visual workflow automation"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    trigger_type = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='draft')  # draft, active, paused, archived
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='workflows')
    
    def __repr__(self):
        return f'<WorkflowAutomation {self.name}>'

class WorkflowNode(db.Model):
    """Individual nodes in workflow canvas"""
    id = db.Column(db.Integer, primary_key=True)
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflow_automation.id'), nullable=False)
    node_type = db.Column(db.String(50), nullable=False)  # trigger, action, logic, exit
    action_type = db.Column(db.String(100), nullable=False)  # send_email, wait, if_condition, etc
    position_x = db.Column(db.Integer, default=0)
    position_y = db.Column(db.Integer, default=0)
    config = db.Column(JSON)  # Node-specific configuration
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    workflow = db.relationship('WorkflowAutomation', backref='nodes')
    
    def __repr__(self):
        return f'<WorkflowNode {self.node_type}:{self.action_type}>'

class WorkflowConnection(db.Model):
    """Connections between workflow nodes"""
    id = db.Column(db.Integer, primary_key=True)
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflow_automation.id'), nullable=False)
    source_node_id = db.Column(db.Integer, db.ForeignKey('workflow_node.id'), nullable=False)
    target_node_id = db.Column(db.Integer, db.ForeignKey('workflow_node.id'), nullable=False)
    condition = db.Column(db.String(50))  # For conditional branches: 'true', 'false', or null
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    workflow = db.relationship('WorkflowAutomation', backref='connections')
    source_node = db.relationship('WorkflowNode', foreign_keys=[source_node_id])
    target_node = db.relationship('WorkflowNode', foreign_keys=[target_node_id])
    
    def __repr__(self):
        return f'<WorkflowConnection {self.source_node_id}->{self.target_node_id}>'

class WorkflowExecution(db.Model):
    """Track workflow execution for contacts"""
    id = db.Column(db.Integer, primary_key=True)
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflow_automation.id'), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, running, completed, failed, waiting
    current_node_id = db.Column(db.Integer, db.ForeignKey('workflow_node.id'))
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    
    # Relationships
    workflow = db.relationship('WorkflowAutomation', backref='executions')
    contact = db.relationship('Contact', backref='workflow_executions')
    current_node = db.relationship('WorkflowNode', foreign_keys=[current_node_id])
    
    def __repr__(self):
        return f'<WorkflowExecution {self.workflow_id}:{self.contact_id}:{self.status}>'

# Advanced Configuration (Company Integration Management)
class CompanyIntegrationConfig(db.Model):
    """Store company-specific integration configurations"""
    __tablename__ = 'company_integration_config'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    service_slug = db.Column(db.String(50), nullable=False)  # openai, google_ads, exoclick, etc.
    display_name = db.Column(db.String(100), nullable=False)
    
    # Configuration data
    config_json = db.Column(JSON)  # Non-sensitive config (URLs, usernames, etc.)
    encrypted_secrets_json = db.Column(db.Text)  # Encrypted API keys, tokens, passwords
    
    # Metadata
    is_active = db.Column(db.Boolean, default=True)
    status = db.Column(db.String(20), default='active')  # active, disabled, error
    last_tested_at = db.Column(db.DateTime)
    test_status = db.Column(db.String(20))  # success, failed, pending
    test_message = db.Column(db.Text)
    
    # Audit
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    updated_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = db.relationship('Company', backref='integration_configs')
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    updated_by = db.relationship('User', foreign_keys=[updated_by_id])
    
    # Unique constraint: one config per service per company
    __table_args__ = (
        db.UniqueConstraint('company_id', 'service_slug', name='uq_company_service'),
    )
    
    def __repr__(self):
        return f'<CompanyIntegrationConfig {self.company_id}:{self.service_slug}>'

class IntegrationAuditLog(db.Model):
    """Audit trail for integration configuration changes"""
    __tablename__ = 'integration_audit_log'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    config_id = db.Column(db.Integer, db.ForeignKey('company_integration_config.id'))
    service_slug = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(20), nullable=False)  # created, updated, deleted, tested
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    changes = db.Column(JSON)  # Changed fields (secrets redacted)
    ip_address = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    company = db.relationship('Company', backref='integration_audit_logs')
    config = db.relationship('CompanyIntegrationConfig', backref='audit_logs')
    user = db.relationship('User', backref='integration_audit_logs')
    
    def __repr__(self):
        return f'<IntegrationAuditLog {self.service_slug}:{self.action}>'"""
Models for advanced LUX Marketing features
These extend the main models.py with new features
"""
from datetime import datetime
from app import db
from sqlalchemy import JSON, Text

# ============= WORDPRESS / WOOCOMMERCE INTEGRATION =============
class WordPressIntegration(db.Model):
    """WordPress site integration"""
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    site_url = db.Column(db.String(255), nullable=False)
    api_key = db.Column(db.String(255), nullable=False)  # Encrypted
    is_active = db.Column(db.Boolean, default=True)
    sync_products = db.Column(db.Boolean, default=True)
    sync_blog_posts = db.Column(db.Boolean, default=True)
    last_synced_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    company = db.relationship('Company', backref='wordpress_integrations')

# ============= KEYWORD RESEARCH & SEO =============
class KeywordResearch(db.Model):
    """Keyword research and tracking"""
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    keyword = db.Column(db.String(255), nullable=False)
    search_volume = db.Column(db.Integer)
    difficulty_score = db.Column(db.Float)  # 0-100
    competition = db.Column(db.String(20))  # low, medium, high
    seasonal_trend = db.Column(JSON)  # Monthly data
    intent = db.Column(db.String(50))  # commercial, informational, navigational, transactional
    related_keywords = db.Column(JSON)  # List of related keywords
    status = db.Column(db.String(20), default='tracking')  # tracking, targeting, achieved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    company = db.relationship('Company', backref='keyword_research')

class Deal(db.Model):
    """Sales deals/opportunities"""
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    value = db.Column(db.Float)  # Deal value
    currency = db.Column(db.String(3), default='USD')
    stage = db.Column(db.String(50), default='prospecting')  # prospecting, qualification, proposal, negotiation, won, lost
    probability = db.Column(db.Float, default=0.0)  # 0-1.0
    expected_close_date = db.Column(db.DateTime)
    closed_at = db.Column(db.DateTime)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    company = db.relationship('Company', backref='deals')
    contact = db.relationship('Contact', backref='deals')
    owner = db.relationship('User', backref='deals')

class DealActivity(db.Model):
    """Activities associated with a deal"""
    id = db.Column(db.Integer, primary_key=True)
    deal_id = db.Column(db.Integer, db.ForeignKey('deal.id'), nullable=False)
    activity_type = db.Column(db.String(50))  # email, call, meeting, note
    description = db.Column(db.Text)
    activity_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    deal = db.relationship('Deal', backref='activities')
    user = db.relationship('User', backref='deal_activities')

class CustomerLifecycle(db.Model):
    """Track customer lifecycle stages"""
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    stage = db.Column(db.String(50), default='awareness')  # awareness, consideration, decision, retention, advocacy
    value_score = db.Column(db.Float, default=0.0)  # How valuable this customer is
    risk_score = db.Column(db.Float, default=0.0)  # Risk of churn
    next_action = db.Column(db.String(255))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    contact = db.relationship('Contact', backref='lifecycle')

# ============= LEAD SCORING & NURTURING =============
class LeadScore(db.Model):
    """AI-powered lead scoring"""
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    lead_score = db.Column(db.Float)  # 0-100
    engagement_score = db.Column(db.Float)  # Email opens, clicks, etc.
    behavior_score = db.Column(db.Float)  # Website visits, time on page, etc.
    fit_score = db.Column(db.Float)  # Company fit based on ICP
    last_calculated = db.Column(db.DateTime, default=datetime.utcnow)
    
    contact = db.relationship('Contact', backref='lead_score')

class NurtureCampaign(db.Model):
    """Automated lead nurturing campaigns"""
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    trigger_condition = db.Column(JSON)  # What triggers the campaign
    sequence = db.Column(JSON)  # Array of emails/actions
    is_active = db.Column(db.Boolean, default=True)
    success_rate = db.Column(db.Float)  # Percentage converted
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    company = db.relationship('Company', backref='nurture_campaigns')

# ============= COMPETITOR ANALYSIS =============
class CompetitorProfile(db.Model):
    """Track competitor information"""
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    competitor_name = db.Column(db.String(255), nullable=False)
    website_url = db.Column(db.String(255))
    strengths = db.Column(JSON)  # Array of strengths
    weaknesses = db.Column(JSON)  # Array of weaknesses
    pricing_model = db.Column(db.Text)
    market_share = db.Column(db.Float)  # Percentage
    last_analyzed = db.Column(db.DateTime, default=datetime.utcnow)
    
    company = db.relationship('Company', backref='competitor_profiles')

class CompetitorMetric(db.Model):
    """Track competitor metrics over time"""
    id = db.Column(db.Integer, primary_key=True)
    competitor_id = db.Column(db.Integer, db.ForeignKey('competitor_profile.id'), nullable=False)
    metric_name = db.Column(db.String(100))  # pricing, features, customer_count, etc.
    metric_value = db.Column(db.String(255))
    tracked_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    competitor = db.relationship('CompetitorProfile', backref='metrics')

# ============= PERSONALIZATION & SEGMENTATION =============
class PersonalizationRule(db.Model):
    """Rules for content personalization"""
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    segment_criteria = db.Column(JSON)  # How to identify segment
    personalization_config = db.Column(JSON)  # What to personalize
    priority = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    company = db.relationship('Company', backref='personalization_rules')

# ============= A/B TESTING ENHANCEMENTS =============
class MultivariateTest(db.Model):
    """Multivariate testing with multiple variables"""
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    variables = db.Column(JSON)  # Array of test variables
    variants = db.Column(JSON)  # Array of variant combinations
    sample_size = db.Column(db.Integer)
    confidence_level = db.Column(db.Float, default=0.95)  # 0.90, 0.95, 0.99
    status = db.Column(db.String(20), default='running')  # running, completed, paused
    winner = db.Column(db.String(50))  # Best performing variant
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    campaign = db.relationship('Campaign', backref='multivariate_tests')

# ============= ROI TRACKING & ATTRIBUTION =============
class CampaignCost(db.Model):
    """Track costs associated with campaigns"""
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    cost_type = db.Column(db.String(50))  # ads, content, tools, labor
    amount = db.Column(db.Float)
    currency = db.Column(db.String(3), default='USD')
    cost_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    campaign = db.relationship('Campaign', backref='costs')

class AttributionModel(db.Model):
    """Track revenue attribution to campaigns"""
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    revenue = db.Column(db.Float)  # Revenue attributed to this campaign
    attribution_model = db.Column(db.String(50))  # first_touch, last_touch, linear, time_decay
    confidence_score = db.Column(db.Float)  # 0-1.0
    
    campaign = db.relationship('Campaign', backref='attributions')
    contact = db.relationship('Contact', backref='attributions')

# ============= SURVEYS & FEEDBACK =============
class SurveyResponse(db.Model):
    """Responses to NPS and feedback surveys"""
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    survey_type = db.Column(db.String(50))  # nps, csat, ces, custom
    score = db.Column(db.Integer)  # NPS: 0-10, CSAT: 1-5, etc.
    feedback = db.Column(db.Text)  # Open feedback text
    sentiment = db.Column(db.String(20))  # positive, neutral, negative (AI analyzed)
    sentiment_score = db.Column(db.Float)  # -1.0 to 1.0
    topics = db.Column(JSON)  # Extracted topics from feedback
    responded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    contact = db.relationship('Contact', backref='survey_responses')

# ============= AGENT CONFIGURATION =============
class AgentConfiguration(db.Model):
    """Configuration for individual AI agents"""
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    agent_type = db.Column(db.String(100), nullable=False)  # brand_strategy, analytics, etc.
    is_enabled = db.Column(db.Boolean, default=True)
    schedule_frequency = db.Column(db.String(50))  # hourly, daily, weekly, monthly
    task_priority = db.Column(db.Integer, default=5)  # 1-10, higher = more important
    configuration = db.Column(JSON)  # Agent-specific settings
    last_executed = db.Column(db.DateTime)
    execution_history = db.Column(JSON)  # Array of last executions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    company = db.relationship('Company', backref='agent_configurations')

