from datetime import datetime
from app import db
from flask_login import UserMixin
from sqlalchemy import JSON

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
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaign_recipients = db.relationship('CampaignRecipient', backref='contact', lazy='dynamic')
    
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
    html_content = db.Column(db.Text, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaigns = db.relationship('Campaign', backref='template', lazy='dynamic')
    
    def __repr__(self):
        return f'<EmailTemplate {self.name}>'

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('email_template.id'))
    status = db.Column(db.String(20), default='draft')  # draft, scheduled, sending, sent, paused
    scheduled_at = db.Column(db.DateTime)
    sent_at = db.Column(db.DateTime)
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
    status = db.Column(db.String(20), default='pending')  # pending, sent, failed, bounced
    sent_at = db.Column(db.DateTime)
    opened_at = db.Column(db.DateTime)
    clicked_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    
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
