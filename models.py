from datetime import datetime
from app import db
from flask_login import UserMixin
from sqlalchemy import JSON, Text

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    company = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    tags = db.Column(db.String(255))  # Comma-separated tags
    custom_fields = db.Column(JSON)  # Additional custom data
    engagement_score = db.Column(db.Float, default=0.0)
    last_activity = db.Column(db.DateTime)
    source = db.Column(db.String(50))  # web_form, manual, import, api
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