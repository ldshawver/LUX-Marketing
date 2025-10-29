import csv
import io
import base64
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, make_response
from flask_login import login_required, current_user
from sqlalchemy import or_
from app import db
from models import (Contact, Campaign, EmailTemplate, CampaignRecipient, EmailTracking, 
                    BrandKit, EmailComponent, Poll, PollResponse, ABTest, Automation, 
                    AutomationStep, SMSCampaign, SMSRecipient, SocialPost, Segment, 
                    SegmentMember, WebForm, FormSubmission, Event, EventRegistration, 
                    Product, Order, CalendarEvent, AutomationTemplate, AutomationExecution,
                    AutomationAction, LandingPage, NewsletterArchive, NonOpenerResend)
from email_service import EmailService
from utils import validate_email
from tracking import decode_tracking_data, record_email_event
import logging
import json
from ai_agent import lux_agent
from seo_service import seo_service

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def dashboard():
    """Dashboard with overview statistics"""
    total_contacts = Contact.query.filter_by(is_active=True).count()
    total_campaigns = Campaign.query.count()
    active_campaigns = Campaign.query.filter_by(status='sending').count()
    recent_campaigns = Campaign.query.order_by(Campaign.created_at.desc()).limit(5).all()
    
    # Email statistics
    total_sent = db.session.query(CampaignRecipient).filter_by(status='sent').count()
    total_failed = db.session.query(CampaignRecipient).filter_by(status='failed').count()
    
    return render_template('dashboard.html',
                         total_contacts=total_contacts,
                         total_campaigns=total_campaigns,
                         active_campaigns=active_campaigns,
                         recent_campaigns=recent_campaigns,
                         total_sent=total_sent,
                         total_failed=total_failed)

@main_bp.route('/contacts')
@login_required
def contacts():
    """Contact management page"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    query = Contact.query.filter_by(is_active=True)
    
    if search:
        query = query.filter(or_(
            Contact.email.contains(search),
            Contact.first_name.contains(search),
            Contact.last_name.contains(search),
            Contact.company.contains(search)
        ))
    
    contacts = query.order_by(Contact.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('contacts.html', contacts=contacts, search=search)

@main_bp.route('/contacts/add', methods=['POST'])
@login_required
def add_contact():
    """Add a new contact"""
    email = request.form.get('email', '').strip()
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    company = request.form.get('company', '').strip()
    phone = request.form.get('phone', '').strip()
    tags = request.form.get('tags', '').strip()
    
    if not email:
        flash('Email is required', 'error')
        return redirect(url_for('main.contacts'))
    
    if not validate_email(email):
        flash('Invalid email format', 'error')
        return redirect(url_for('main.contacts'))
    
    # Check if contact already exists
    existing = Contact.query.filter_by(email=email).first()
    if existing:
        flash('Contact with this email already exists', 'error')
        return redirect(url_for('main.contacts'))
    
    contact = Contact()
    contact.email = email
    contact.first_name = first_name
    contact.last_name = last_name
    contact.company = company
    contact.phone = phone
    contact.tags = tags
    
    db.session.add(contact)
    db.session.commit()
    
    flash('Contact added successfully', 'success')
    return redirect(url_for('main.contacts'))

@main_bp.route('/contacts/import', methods=['POST'])
@login_required
def import_contacts():
    """Import contacts from CSV file"""
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('main.contacts'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('main.contacts'))
    
    if not file.filename or not file.filename.endswith('.csv'):
        flash('Please upload a CSV file', 'error')
        return redirect(url_for('main.contacts'))
    
    try:
        # Read CSV file with better error handling
        try:
            content = file.stream.read()
            # Try different encodings
            for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
                try:
                    decoded_content = content.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue
            else:
                flash('Unable to decode file. Please ensure it is saved in UTF-8 format.', 'error')
                return redirect(url_for('main.contacts'))
            
            stream = io.StringIO(decoded_content, newline=None)
            csv_input = csv.DictReader(stream)
        except Exception as e:
            flash(f'Error reading CSV file: {str(e)}', 'error')
            return redirect(url_for('main.contacts'))
        
        imported_count = 0
        error_count = 0
        
        for row in csv_input:
            email = row.get('email', '').strip()
            if not email or not validate_email(email):
                error_count += 1
                continue
            
            # Check if contact already exists
            existing = Contact.query.filter_by(email=email).first()
            if existing:
                continue
            
            contact = Contact()
            contact.email = email
            contact.first_name = row.get('first_name', '').strip()
            contact.last_name = row.get('last_name', '').strip()
            contact.company = row.get('company', '').strip()
            contact.phone = row.get('phone', '').strip()
            contact.tags = row.get('tags', '').strip()
            
            db.session.add(contact)
            imported_count += 1
        
        db.session.commit()
        
        flash(f'Successfully imported {imported_count} contacts. {error_count} errors.', 'success')
        
    except Exception as e:
        logging.error(f"Error importing contacts: {str(e)}")
        flash('Error importing contacts. Please check file format.', 'error')
    
    return redirect(url_for('main.contacts'))

@main_bp.route('/contacts/export')
@login_required
def export_contacts():
    """Export contacts to CSV"""
    contacts = Contact.query.filter_by(is_active=True).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(['email', 'first_name', 'last_name', 'company', 'phone', 'tags', 'created_at'])
    
    # Write contacts
    for contact in contacts:
        writer.writerow([
            contact.email,
            contact.first_name or '',
            contact.last_name or '',
            contact.company or '',
            contact.phone or '',
            contact.tags or '',
            contact.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    # Create response
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename=contacts_{datetime.now().strftime("%Y%m%d")}.csv'
    
    return response

@main_bp.route('/contacts/<int:contact_id>/delete', methods=['POST'])
@login_required
def delete_contact(contact_id):
    """Delete a contact"""
    contact = Contact.query.get_or_404(contact_id)
    contact.is_active = False
    db.session.commit()
    
    flash('Contact deleted successfully', 'success')
    return redirect(url_for('main.contacts'))

@main_bp.route('/campaigns')
@login_required
def campaigns():
    """Campaign management page"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '')
    
    query = Campaign.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    campaigns = query.order_by(Campaign.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    return render_template('campaigns.html', campaigns=campaigns, status_filter=status_filter)

@main_bp.route('/campaigns/create', methods=['GET', 'POST'])
@login_required
def create_campaign():
    """Create a new campaign"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        subject = request.form.get('subject', '').strip()
        template_id = request.form.get('template_id', type=int)
        scheduled_at = request.form.get('scheduled_at')
        recipient_tags = request.form.get('recipient_tags', '').strip()
        
        if not name or not subject or not template_id:
            flash('Name, subject, and template are required', 'error')
            return redirect(url_for('main.create_campaign'))
        
        # Create campaign
        campaign = Campaign()
        campaign.name = name
        campaign.subject = subject
        campaign.template_id = template_id
        campaign.status = 'draft'
        
        if scheduled_at:
            try:
                campaign.scheduled_at = datetime.fromisoformat(scheduled_at.replace('T', ' '))
                campaign.status = 'scheduled'
            except ValueError:
                flash('Invalid scheduled time format', 'error')
                return redirect(url_for('main.create_campaign'))
        
        db.session.add(campaign)
        db.session.flush()  # Get campaign ID
        
        # Add recipients
        contacts_query = Contact.query.filter_by(is_active=True)
        
        if recipient_tags:
            # Filter by tags
            tag_list = [tag.strip() for tag in recipient_tags.split(',')]
            tag_conditions = []
            for tag in tag_list:
                tag_conditions.append(Contact.tags.contains(tag))
            contacts_query = contacts_query.filter(or_(*tag_conditions))
        
        contacts = contacts_query.all()
        
        for contact in contacts:
            recipient = CampaignRecipient()
            recipient.campaign_id = campaign.id
            recipient.contact_id = contact.id
            db.session.add(recipient)
        
        db.session.commit()
        
        flash(f'Campaign created successfully with {len(contacts)} recipients', 'success')
        return redirect(url_for('main.campaigns'))
    
    # GET request - show form
    templates = EmailTemplate.query.filter_by(is_active=True).all()
    return render_template('campaign_create.html', templates=templates)

@main_bp.route('/campaigns/<int:campaign_id>/send', methods=['POST'])
@login_required
def send_campaign(campaign_id):
    """Send a campaign immediately"""
    campaign = Campaign.query.get_or_404(campaign_id)
    
    if campaign.status not in ['draft', 'scheduled']:
        flash('Campaign cannot be sent in current status', 'error')
        return redirect(url_for('main.campaigns'))
    
    try:
        email_service = EmailService()
        email_service.send_campaign(campaign)
        
        campaign.status = 'sending'
        campaign.sent_at = datetime.utcnow()
        db.session.commit()
        
        flash('Campaign is being sent', 'success')
    except Exception as e:
        logging.error(f"Error sending campaign: {str(e)}")
        flash('Error sending campaign. Please check configuration.', 'error')
    
    return redirect(url_for('main.campaigns'))

@main_bp.route('/campaigns/<int:campaign_id>/preview')
@login_required
def preview_campaign(campaign_id):
    """Preview campaign email"""
    campaign = Campaign.query.get_or_404(campaign_id)
    template = campaign.template
    
    # Get sample contact for preview
    sample_contact = Contact.query.filter_by(is_active=True).first()
    
    return render_template('preview_email.html', 
                         campaign=campaign, 
                         template=template,
                         sample_contact=sample_contact)

@main_bp.route('/templates')
@login_required
def templates():
    """Email template management"""
    templates = EmailTemplate.query.filter_by(is_active=True).order_by(EmailTemplate.created_at.desc()).all()
    return render_template('templates_manage.html', templates=templates)

@main_bp.route('/templates/gallery')
@login_required
def template_gallery():
    """Branded template gallery"""
    # Define branded template options
    branded_templates = [
        {
            'id': 'modern_newsletter',
            'name': 'Modern Newsletter',
            'description': 'Clean, modern design perfect for newsletters and announcements',
            'preview_image': '/static/images/templates/modern_newsletter.png',
            'category': 'Newsletter',
            'features': ['Responsive Design', 'Hero Image', 'Call-to-Action Button', 'Social Links']
        },
        {
            'id': 'promotional_sale',
            'name': 'Promotional Sale',
            'description': 'Eye-catching design for sales promotions and special offers',
            'preview_image': '/static/images/templates/promotional_sale.png',
            'category': 'Promotional',
            'features': ['Bold Headlines', 'Product Showcase', 'Urgency Elements', 'Discount Highlights']
        },
        {
            'id': 'welcome_series',
            'name': 'Welcome Email',
            'description': 'Professional welcome email for new subscribers',
            'preview_image': '/static/images/templates/welcome_series.png',
            'category': 'Welcome',
            'features': ['Personal Touch', 'Brand Introduction', 'Next Steps', 'Contact Information']
        },
        {
            'id': 'event_invitation',
            'name': 'Event Invitation',
            'description': 'Elegant design for event invitations and announcements',
            'preview_image': '/static/images/templates/event_invitation.png',
            'category': 'Events',
            'features': ['Event Details', 'RSVP Button', 'Location Map', 'Calendar Integration']
        },
        {
            'id': 'product_update',
            'name': 'Product Update',
            'description': 'Professional layout for product announcements and updates',
            'preview_image': '/static/images/templates/product_update.png',
            'category': 'Product',
            'features': ['Feature Highlights', 'Screenshots', 'Learn More Links', 'Feedback Request']
        },
        {
            'id': 'minimal_corporate',
            'name': 'Minimal Corporate',
            'description': 'Clean, minimalist design for corporate communications',
            'preview_image': '/static/images/templates/minimal_corporate.png',
            'category': 'Corporate',
            'features': ['Professional Layout', 'Typography Focus', 'Brand Colors', 'Simple CTA']
        }
    ]
    
    return render_template('template_gallery.html', branded_templates=branded_templates)

@main_bp.route('/templates/use-branded/<template_id>')
@login_required
def use_branded_template(template_id):
    """Use a branded template to create a new custom template"""
    # Get the branded template HTML
    template_html = get_branded_template_html(template_id)
    
    if not template_html:
        flash('Template not found', 'error')
        return redirect(url_for('main.template_gallery'))
    
    # Get template info
    template_info = get_branded_template_info(template_id)
    
    return render_template('template_create.html', 
                         branded_template=template_info,
                         default_html=template_html['html'],
                         default_subject=template_html['subject'])

@main_bp.route('/templates/create', methods=['GET', 'POST'])
@login_required
def create_template():
    """Create a new email template"""
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            subject = request.form.get('subject', '').strip()
            html_content = request.form.get('html_content', '').strip()
            
            logging.debug(f"Template creation attempt: name='{name}', subject='{subject}', content_length={len(html_content)}")
            
            if not name or not subject or not html_content:
                flash('All fields are required', 'error')
                return redirect(url_for('main.create_template'))
            
            template = EmailTemplate()
            template.name = name
            template.subject = subject
            template.html_content = html_content
            
            db.session.add(template)
            db.session.commit()
            
            logging.info(f"Template '{name}' created successfully")
            flash('Template created successfully', 'success')
            return redirect(url_for('main.templates'))
            
        except Exception as e:
            logging.error(f"Error creating template: {str(e)}")
            db.session.rollback()
            flash('Error creating template. Please try again.', 'error')
            return redirect(url_for('main.create_template'))
    
    return render_template('template_create.html')

@main_bp.route('/templates/<int:template_id>/preview')
@login_required
def preview_template(template_id):
    """Preview email template"""
    template = EmailTemplate.query.get_or_404(template_id)
    
    # Get sample contact for preview
    sample_contact = Contact.query.filter_by(is_active=True).first()
    
    if not sample_contact:
        # Create a sample contact for preview if none exists
        sample_contact = type('SampleContact', (), {
            'first_name': 'John',
            'last_name': 'Doe',
            'full_name': 'John Doe',
            'email': 'john.doe@example.com',
            'company': 'Example Company',
            'phone': '+1 (555) 123-4567'
        })()
    
    # Create a sample campaign for preview
    sample_campaign = type('SampleCampaign', (), {
        'name': 'Sample Campaign',
        'subject': template.subject,
        'id': 0
    })()
    
    try:
        from email_service import EmailService
        email_service = EmailService()
        
        # Render the template with sample data
        rendered_html = email_service.render_template(
            template.html_content,
            sample_contact,
            sample_campaign
        )
        
        return render_template('preview_template.html', 
                             template=template, 
                             rendered_html=rendered_html,
                             sample_contact=sample_contact)
                             
    except Exception as e:
        flash(f'Error rendering template preview: {str(e)}', 'error')
        return redirect(url_for('main.templates'))

@main_bp.route('/templates/preview-live', methods=['POST'])
@login_required
def preview_template_live():
    """Live preview of template during creation/editing"""
    try:
        html_content = request.form.get('html_content', '')
        subject = request.form.get('subject', 'Preview Subject')
        
        if not html_content:
            return jsonify({'error': 'No HTML content provided'}), 400
        
        # Create sample data for preview
        sample_contact = type('SampleContact', (), {
            'first_name': 'John',
            'last_name': 'Doe',
            'full_name': 'John Doe',
            'email': 'john.doe@example.com',
            'company': 'Example Company',
            'phone': '+1 (555) 123-4567'
        })()
        
        sample_campaign = type('SampleCampaign', (), {
            'name': 'Sample Campaign',
            'subject': subject,
            'id': 0
        })()
        
        # Render the template
        from email_service import EmailService
        email_service = EmailService()
        
        rendered_html = email_service.render_template(
            html_content,
            sample_contact,
            sample_campaign
        )
        
        return jsonify({
            'success': True,
            'rendered_html': rendered_html,
            'subject': subject
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_branded_template_html(template_id):
    """Get HTML content for branded templates"""
    templates = {
        'modern_newsletter': {
            'subject': 'Latest Updates from {{campaign.name}}',
            'html': '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{campaign.subject}}</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Arial', sans-serif; background-color: #f8f9fa;">
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f8f9fa;">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <table width="600" cellpadding="0" cellspacing="0" border="0" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 40px 30px; text-align: center; border-radius: 8px 8px 0 0;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 28px; font-weight: bold;">Your Company</h1>
                            <p style="margin: 10px 0 0 0; color: #ffffff; font-size: 16px; opacity: 0.9;">Newsletter</p>
                        </td>
                    </tr>
                    <!-- Main Content -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            <h2 style="margin: 0 0 20px 0; color: #333333; font-size: 24px;">Hello {{contact.first_name}}!</h2>
                            <p style="margin: 0 0 20px 0; color: #666666; font-size: 16px; line-height: 1.6;">
                                We're excited to share the latest updates and insights with you. Here's what's new:
                            </p>
                            
                            <!-- Feature Section -->
                            <div style="background-color: #f8f9fa; padding: 25px; border-radius: 6px; margin: 25px 0;">
                                <h3 style="margin: 0 0 15px 0; color: #333333; font-size: 20px;">Featured Content</h3>
                                <p style="margin: 0 0 15px 0; color: #666666; font-size: 16px; line-height: 1.6;">
                                    Add your featured content here. This section is perfect for highlighting your most important news or updates.
                                </p>
                                <a href="#" style="display: inline-block; background-color: #667eea; color: #ffffff; text-decoration: none; padding: 12px 24px; border-radius: 4px; font-weight: bold;">
                                    Learn More
                                </a>
                            </div>
                            
                            <p style="margin: 20px 0 0 0; color: #666666; font-size: 16px; line-height: 1.6;">
                                Thank you for being part of our community, {{contact.first_name}}!
                            </p>
                        </td>
                    </tr>
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f8f9fa; padding: 30px; text-align: center; border-radius: 0 0 8px 8px;">
                            <p style="margin: 0 0 10px 0; color: #999999; font-size: 14px;">
                                You're receiving this email because you subscribed to our newsletter.
                            </p>
                            <p style="margin: 0; color: #999999; font-size: 14px;">
                                <a href="{{unsubscribe_url}}" style="color: #667eea; text-decoration: none;">Unsubscribe</a> | 
                                <a href="#" style="color: #667eea; text-decoration: none;">Update Preferences</a>
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>'''
        },
        'promotional_sale': {
            'subject': '🔥 Special Offer Just for You, {{contact.first_name}}!',
            'html': '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{campaign.subject}}</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Arial', sans-serif; background-color: #f8f9fa;">
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f8f9fa;">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <table width="600" cellpadding="0" cellspacing="0" border="0" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); padding: 40px 30px; text-align: center; border-radius: 8px 8px 0 0;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 32px; font-weight: bold;">MEGA SALE</h1>
                            <p style="margin: 10px 0 0 0; color: #ffffff; font-size: 18px; font-weight: bold;">UP TO 50% OFF</p>
                        </td>
                    </tr>
                    <!-- Main Content -->
                    <tr>
                        <td style="padding: 40px 30px; text-align: center;">
                            <h2 style="margin: 0 0 20px 0; color: #333333; font-size: 24px;">Hey {{contact.first_name}}, Don't Miss Out!</h2>
                            <p style="margin: 0 0 30px 0; color: #666666; font-size: 16px; line-height: 1.6;">
                                Our biggest sale of the year is here! Save up to 50% on everything. Limited time only!
                            </p>
                            
                            <!-- Offer Box -->
                            <div style="background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%); color: #ffffff; padding: 30px; border-radius: 8px; margin: 30px 0;">
                                <h3 style="margin: 0 0 10px 0; font-size: 28px; font-weight: bold;">50% OFF</h3>
                                <p style="margin: 0 0 20px 0; font-size: 16px;">Use code: SAVE50</p>
                                <a href="#" style="display: inline-block; background-color: #ffffff; color: #ee5a24; text-decoration: none; padding: 15px 30px; border-radius: 4px; font-weight: bold; font-size: 16px;">
                                    SHOP NOW
                                </a>
                            </div>
                            
                            <p style="margin: 20px 0 0 0; color: #ff6b6b; font-size: 14px; font-weight: bold;">
                                ⏰ Hurry! Sale ends in 48 hours
                            </p>
                        </td>
                    </tr>
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f8f9fa; padding: 30px; text-align: center; border-radius: 0 0 8px 8px;">
                            <p style="margin: 0 0 10px 0; color: #999999; font-size: 14px;">
                                You're receiving this email because you're a valued customer.
                            </p>
                            <p style="margin: 0; color: #999999; font-size: 14px;">
                                <a href="{{unsubscribe_url}}" style="color: #ff6b6b; text-decoration: none;">Unsubscribe</a>
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>'''
        },
        'welcome_series': {
            'subject': 'Welcome to our community, {{contact.first_name}}!',
            'html': '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{campaign.subject}}</title>
</head>
<body style="margin: 0; padding: 0; font-family: 'Arial', sans-serif; background-color: #f8f9fa;">
    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f8f9fa;">
        <tr>
            <td align="center" style="padding: 40px 20px;">
                <table width="600" cellpadding="0" cellspacing="0" border="0" style="background-color: #ffffff; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%); padding: 40px 30px; text-align: center; border-radius: 8px 8px 0 0;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 32px; font-weight: bold;">Welcome!</h1>
                            <p style="margin: 10px 0 0 0; color: #ffffff; font-size: 16px; opacity: 0.9;">We're thrilled to have you join us</p>
                        </td>
                    </tr>
                    <!-- Main Content -->
                    <tr>
                        <td style="padding: 40px 30px;">
                            <h2 style="margin: 0 0 20px 0; color: #333333; font-size: 24px;">Hi {{contact.first_name}}, Welcome aboard! 🎉</h2>
                            <p style="margin: 0 0 20px 0; color: #666666; font-size: 16px; line-height: 1.6;">
                                Thank you for joining our community! We're excited to have you with us and can't wait to share amazing content, updates, and exclusive offers.
                            </p>
                            
                            <!-- Getting Started Section -->
                            <div style="background-color: #f8f9fa; padding: 25px; border-radius: 6px; margin: 25px 0;">
                                <h3 style="margin: 0 0 15px 0; color: #333333; font-size: 20px;">🚀 Getting Started</h3>
                                <ul style="margin: 0; padding-left: 20px; color: #666666; font-size: 16px; line-height: 1.8;">
                                    <li>Explore our latest content and resources</li>
                                    <li>Follow us on social media for daily updates</li>
                                    <li>Join our community discussions</li>
                                    <li>Don't forget to add us to your contacts</li>
                                </ul>
                            </div>
                            
                            <div style="text-align: center; margin: 30px 0;">
                                <a href="#" style="display: inline-block; background-color: #2ecc71; color: #ffffff; text-decoration: none; padding: 15px 30px; border-radius: 4px; font-weight: bold; font-size: 16px;">
                                    Get Started
                                </a>
                            </div>
                            
                            <p style="margin: 20px 0 0 0; color: #666666; font-size: 16px; line-height: 1.6;">
                                If you have any questions, feel free to reply to this email. We're here to help!
                            </p>
                            
                            <p style="margin: 20px 0 0 0; color: #666666; font-size: 16px; line-height: 1.6;">
                                Best regards,<br>
                                <strong>The Team</strong>
                            </p>
                        </td>
                    </tr>
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f8f9fa; padding: 30px; text-align: center; border-radius: 0 0 8px 8px;">
                            <p style="margin: 0 0 10px 0; color: #999999; font-size: 14px;">
                                You're receiving this email because you recently signed up.
                            </p>
                            <p style="margin: 0; color: #999999; font-size: 14px;">
                                <a href="{{unsubscribe_url}}" style="color: #2ecc71; text-decoration: none;">Unsubscribe</a> | 
                                <a href="#" style="color: #2ecc71; text-decoration: none;">Contact Us</a>
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>'''
        }
    }
    
    return templates.get(template_id)

def get_branded_template_info(template_id):
    """Get template information"""
    template_info = {
        'modern_newsletter': {
            'name': 'Modern Newsletter',
            'description': 'Clean, modern design perfect for newsletters and announcements'
        },
        'promotional_sale': {
            'name': 'Promotional Sale',
            'description': 'Eye-catching design for sales promotions and special offers'
        },
        'welcome_series': {
            'name': 'Welcome Email',
            'description': 'Professional welcome email for new subscribers'
        }
    }
    
    return template_info.get(template_id, {'name': 'Unknown Template', 'description': ''})

@main_bp.route('/analytics/comprehensive')
@login_required
def comprehensive_analytics():
    """Comprehensive analytics dashboard with all 6 metric categories"""
    try:
        from agents.analytics_agent import AnalyticsAgent
        
        agent = AnalyticsAgent()
        period_days = request.args.get('period_days', 30, type=int)
        
        metrics_result = agent.calculate_comprehensive_metrics({'period_days': period_days})
        
        if not metrics_result.get('success'):
            flash('Unable to load analytics data', 'error')
            return redirect(url_for('main.dashboard'))
        
        return render_template('analytics_comprehensive.html',
                             metrics=metrics_result.get('metrics', {}),
                             period_days=period_days,
                             generated_at=metrics_result.get('generated_at'))
        
    except Exception as e:
        logger.error(f"Comprehensive analytics error: {e}")
        flash('Error loading analytics dashboard', 'error')
        return redirect(url_for('main.dashboard'))

@main_bp.route('/analytics')
@login_required
def analytics():
    """Analytics and reporting dashboard"""
    # Campaign statistics
    total_campaigns = Campaign.query.count()
    sent_campaigns = Campaign.query.filter_by(status='sent').count()
    
    # Email delivery statistics
    total_sent = db.session.query(CampaignRecipient).filter_by(status='sent').count()
    total_failed = db.session.query(CampaignRecipient).filter_by(status='failed').count()
    total_bounced = db.session.query(CampaignRecipient).filter_by(status='bounced').count()
    total_pending = db.session.query(CampaignRecipient).filter_by(status='pending').count()
    
    # Engagement statistics
    total_opened = db.session.query(CampaignRecipient).filter(CampaignRecipient.opened_at.isnot(None)).count()
    total_clicked = db.session.query(CampaignRecipient).filter(CampaignRecipient.clicked_at.isnot(None)).count()
    
    # Calculate rates
    total_delivered = total_sent
    open_rate = (total_opened / total_delivered * 100) if total_delivered > 0 else 0
    click_rate = (total_clicked / total_delivered * 100) if total_delivered > 0 else 0
    bounce_rate = (total_bounced / (total_delivered + total_bounced) * 100) if (total_delivered + total_bounced) > 0 else 0
    
    # SMS Campaign statistics
    total_sms_campaigns = SMSCampaign.query.count()
    sent_sms_campaigns = SMSCampaign.query.filter_by(status='sent').count()
    sms_sent = db.session.query(SMSRecipient).filter_by(status='sent').count()
    sms_failed = db.session.query(SMSRecipient).filter_by(status='failed').count()
    sms_pending = db.session.query(SMSRecipient).filter_by(status='pending').count()
    sms_delivery_rate = (sms_sent / (sms_sent + sms_failed) * 100) if (sms_sent + sms_failed) > 0 else 0
    
    # Tracking events breakdown
    tracking_stats = db.session.query(
        EmailTracking.event_type, 
        db.func.count(EmailTracking.id).label('count')
    ).group_by(EmailTracking.event_type).all()
    
    tracking_data = {stat.event_type: stat.count for stat in tracking_stats}
    
    # Recent campaign performance
    recent_campaigns = Campaign.query.filter(Campaign.sent_at.isnot(None)).order_by(Campaign.sent_at.desc()).limit(10).all()
    
    # Top performing campaigns by open rate
    top_campaigns = []
    for campaign in Campaign.query.filter_by(status='sent').all():
        recipients = campaign.recipients.filter_by(status='sent').count()
        opens = campaign.recipients.filter(CampaignRecipient.opened_at.isnot(None)).count()
        clicks = campaign.recipients.filter(CampaignRecipient.clicked_at.isnot(None)).count()
        
        if recipients > 0:
            campaign_open_rate = (opens / recipients * 100)
            campaign_click_rate = (clicks / recipients * 100)
            top_campaigns.append({
                'campaign': campaign,
                'recipients': recipients,
                'opens': opens,
                'clicks': clicks,
                'open_rate': campaign_open_rate,
                'click_rate': campaign_click_rate
            })
    
    # Sort by open rate
    top_campaigns.sort(key=lambda x: x['open_rate'], reverse=True)
    top_campaigns = top_campaigns[:5]  # Top 5 campaigns
    
    return render_template('analytics.html',
                         total_campaigns=total_campaigns,
                         sent_campaigns=sent_campaigns,
                         total_sent=total_sent,
                         total_failed=total_failed,
                         total_bounced=total_bounced,
                         total_pending=total_pending,
                         total_opened=total_opened,
                         total_clicked=total_clicked,
                         open_rate=open_rate,
                         click_rate=click_rate,
                         bounce_rate=bounce_rate,
                         tracking_data=tracking_data,
                         recent_campaigns=recent_campaigns,
                         top_campaigns=top_campaigns,
                         total_sms_campaigns=total_sms_campaigns,
                         sent_sms_campaigns=sent_sms_campaigns,
                         sms_sent=sms_sent,
                         sms_failed=sms_failed,
                         sms_pending=sms_pending,
                         sms_delivery_rate=sms_delivery_rate)

@main_bp.route('/track/open/<tracking_id>')
def track_open(tracking_id):
    """Track email open events"""
    campaign_id, contact_id = decode_tracking_data(tracking_id)
    
    if campaign_id and contact_id:
        # Get client info for tracking
        event_data = {
            'user_agent': request.headers.get('User-Agent', ''),
            'ip_address': request.remote_addr,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Record the open event
        record_email_event(campaign_id, contact_id, 'opened', event_data)
    
    # Return a 1x1 transparent pixel
    from flask import Response
    
    # 1x1 transparent GIF in base64
    pixel_data = 'R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'
    pixel_bytes = base64.b64decode(pixel_data)
    
    response = Response(pixel_bytes, mimetype='image/gif')
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response

@main_bp.route('/track/click')
def track_click():
    """Track email click events"""
    tracking_id = request.args.get('tracking_id')
    original_url = request.args.get('url', '/')
    
    if tracking_id:
        campaign_id, contact_id = decode_tracking_data(tracking_id)
        
        if campaign_id and contact_id:
            # Get client info for tracking
            event_data = {
                'user_agent': request.headers.get('User-Agent', ''),
                'ip_address': request.remote_addr,
                'clicked_url': original_url,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Record the click event
            record_email_event(campaign_id, contact_id, 'clicked', event_data)
    
    # Redirect to the original URL
    return redirect(original_url)

@main_bp.route('/api/campaign/<int:campaign_id>/analytics')
@login_required
def campaign_analytics_api(campaign_id):
    """API endpoint for campaign analytics"""
    from tracking import get_campaign_analytics
    
    analytics = get_campaign_analytics(campaign_id)
    if not analytics:
        return jsonify({'error': 'Campaign not found'}), 404
    
    # Convert campaign object to dict for JSON serialization
    campaign_data = {
        'id': analytics['campaign'].id,
        'name': analytics['campaign'].name,
        'subject': analytics['campaign'].subject,
        'status': analytics['campaign'].status,
        'created_at': analytics['campaign'].created_at.isoformat() if analytics['campaign'].created_at else None,
        'sent_at': analytics['campaign'].sent_at.isoformat() if analytics['campaign'].sent_at else None
    }
    
    return jsonify({
        'campaign': campaign_data,
        'metrics': {
            'total_recipients': analytics['total_recipients'],
            'sent_count': analytics['sent_count'],
            'failed_count': analytics['failed_count'],
            'bounced_count': analytics['bounced_count'],
            'opened_count': analytics['opened_count'],
            'clicked_count': analytics['clicked_count'],
            'delivery_rate': round(analytics['delivery_rate'], 2),
            'open_rate': round(analytics['open_rate'], 2),
            'click_rate': round(analytics['click_rate'], 2),
            'bounce_rate': round(analytics['bounce_rate'], 2)
        },
        'events': analytics['event_counts']
    })

# LUX AI Agent Routes
@main_bp.route('/lux/generate-campaign', methods=['POST'])
@login_required
def lux_generate_campaign():
    """LUX AI agent - Generate automated campaign"""
    try:
        from ai_agent import lux_agent
        
        data = request.get_json() or {}
        campaign_brief = {
            'objective': data.get('objective', 'Engage audience and drive conversions'),
            'target_audience': data.get('target_audience', 'All active contacts'),
            'brand_info': data.get('brand_info', 'Professional business'),
            'target_tags': data.get('target_tags', []),
            'schedule_time': None
        }
        
        # Parse schedule time if provided
        if data.get('schedule_time'):
            try:
                campaign_brief['schedule_time'] = datetime.fromisoformat(data['schedule_time'])
            except ValueError:
                pass
        
        result = lux_agent.create_automated_campaign(campaign_brief)
        
        if result:
            return jsonify({
                'success': True,
                'campaign': result,
                'message': f'LUX created campaign "{result["campaign_name"]}" with {result["recipients_count"]} recipients'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'LUX was unable to create the campaign. Please check your OpenAI configuration.'
            }), 500
            
    except Exception as e:
        logger.error(f"LUX generate campaign error: {e}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@main_bp.route('/lux/optimize-campaign/<int:campaign_id>')
@login_required
def lux_optimize_campaign(campaign_id):
    """LUX AI agent - Optimize campaign performance"""
    try:
        from ai_agent import lux_agent
        
        optimization = lux_agent.optimize_campaign_performance(campaign_id)
        
        if optimization:
            return jsonify({
                'success': True,
                'optimization': optimization
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Unable to analyze campaign performance'
            }), 404
            
    except Exception as e:
        logger.error(f"LUX optimize campaign error: {e}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@main_bp.route('/lux/audience-analysis')
@login_required
def lux_audience_analysis():
    """LUX AI agent - Analyze audience segments"""
    try:
        from ai_agent import lux_agent
        
        contacts = Contact.query.filter_by(is_active=True).all()
        analysis = lux_agent.analyze_audience_segments(contacts)
        
        if analysis:
            return jsonify({
                'success': True,
                'analysis': analysis
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Unable to analyze audience'
            }), 500
            
    except Exception as e:
        logger.error(f"LUX audience analysis error: {e}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@main_bp.route('/lux/subject-variants', methods=['POST'])
@login_required
def lux_subject_variants():
    """LUX AI agent - Generate subject line variants"""
    try:
        from ai_agent import lux_agent
        
        data = request.get_json() or {}
        objective = data.get('objective', 'Engage audience')
        original_subject = data.get('original_subject')
        
        variants = lux_agent.generate_subject_line_variants(objective, original_subject)
        
        if variants:
            return jsonify({
                'success': True,
                'variants': variants
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Unable to generate subject line variants'
            }), 500
            
    except Exception as e:
        logger.error(f"LUX subject variants error: {e}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@main_bp.route('/lux/recommendations')
@login_required
def lux_recommendations():
    """LUX AI agent - Get campaign recommendations"""
    try:
        from ai_agent import lux_agent
        from tracking import get_campaign_analytics
        
        # Gather data to pass to LUX agent (avoiding circular imports)
        recent_campaigns = Campaign.query.order_by(Campaign.created_at.desc()).limit(5).all()
        total_contacts = Contact.query.filter_by(is_active=True).count()
        
        campaign_data = []
        for campaign in recent_campaigns:
            analytics = get_campaign_analytics(campaign.id)
            if analytics:
                campaign_data.append({
                    'name': campaign.name,
                    'open_rate': analytics['open_rate'],
                    'click_rate': analytics['click_rate'],
                    'created_at': campaign.created_at.strftime('%Y-%m-%d') if campaign.created_at else ''
                })
        
        recommendations = lux_agent.get_campaign_recommendations(campaign_data, total_contacts)
        
        if recommendations:
            return jsonify({
                'success': True,
                'recommendations': recommendations
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Unable to generate recommendations'
            }), 500
            
    except Exception as e:
        logger.error(f"LUX recommendations error: {e}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@main_bp.route('/lux')
@login_required
def lux_agent_dashboard():
    """LUX AI Agent dashboard"""
    # Get recent campaigns for optimization selection
    recent_campaigns = Campaign.query.filter(Campaign.sent_at.isnot(None)).order_by(Campaign.sent_at.desc()).limit(6).all()
    
    return render_template('lux_agent.html', recent_campaigns=recent_campaigns)

@main_bp.route('/test-email', methods=['GET', 'POST'])
@login_required
def test_email():
    """Test email sending functionality"""
    if request.method == 'POST':
        test_email_address = request.form.get('test_email', '').strip()
        
        if not test_email_address:
            flash('Please enter a test email address', 'error')
            return render_template('test_email.html')
        
        try:
            from email_service import EmailService
            email_service = EmailService()
            
            # Send test email
            subject = "LUX Email Marketing - Test Email"
            html_content = """
            <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center;">
                    <h1 style="color: white; margin: 0;">✅ LUX Email Marketing</h1>
                    <p style="color: white; margin: 10px 0 0 0;">Email Test Successful!</p>
                </div>
                <div style="padding: 30px; background: #f8f9fa;">
                    <h2 style="color: #333;">Email System Working</h2>
                    <p style="color: #666; line-height: 1.6;">
                        Congratulations! Your LUX Email Marketing system is properly configured 
                        and able to send emails. This means:
                    </p>
                    <ul style="color: #666; line-height: 1.8;">
                        <li>✅ Microsoft Graph API connection is working</li>
                        <li>✅ Email templates can be processed</li>
                        <li>✅ Campaign emails will be delivered</li>
                        <li>✅ Password reset emails will work</li>
                    </ul>
                    <p style="color: #666; line-height: 1.6;">
                        You can now confidently create and send email marketing campaigns!
                    </p>
                    <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                    <p style="color: #999; font-size: 12px; text-align: center;">
                        LUX Email Marketing Platform - Test Email
                    </p>
                </div>
            </body>
            </html>
            """
            
            result = email_service.send_email(
                to_email=test_email_address,
                subject=subject,
                html_content=html_content
            )
            
            if result:
                flash(f'✅ Test email sent successfully to {test_email_address}!', 'success')
            else:
                flash('❌ Failed to send test email. Please check your email configuration.', 'error')
                
        except Exception as e:
            flash(f'❌ Error testing email: {str(e)}', 'error')
    
    return render_template('test_email.html')

@main_bp.route('/lux/generate-image', methods=['POST'])
@login_required
def lux_generate_image():
    """LUX AI agent - Generate campaign images with DALL-E"""
    # Exempt from CSRF for JSON API
    from app import csrf
    csrf.exempt(lux_generate_image)
    
    try:
        from ai_agent import lux_agent
        
        data = request.get_json() or {}
        description = data.get('description', 'Professional marketing campaign')
        style = data.get('style', 'professional marketing')
        
        result = lux_agent.generate_campaign_image(description, style)
        
        if result:
            return jsonify({
                'success': True,
                'image': result,
                'message': 'Campaign image generated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Unable to generate image. Please check your OpenAI configuration.'
            }), 500
            
    except Exception as e:
        logger.error(f"LUX generate image error: {e}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@main_bp.route('/lux/product-campaign', methods=['POST'])
@login_required
def lux_product_campaign():
    """LUX AI agent - Create WooCommerce product campaign"""
    # Exempt from CSRF for JSON API
    from app import csrf
    csrf.exempt(lux_product_campaign)
    
    try:
        # Ensure no WooCommerce library conflicts
        import sys
        woo_modules = [mod for mod in sys.modules.keys() if 'woocommerce' in mod.lower()]
        if woo_modules:
            logging.warning(f"Detected WooCommerce modules: {woo_modules}")
            # Remove any problematic WooCommerce modules
            for mod in woo_modules:
                if mod in sys.modules:
                    del sys.modules[mod]
        
        from ai_agent import lux_agent
        
        data = request.get_json() or {}
        
        # WooCommerce configuration
        woocommerce_config = {
            'url': data.get('woocommerce_url', ''),
            'consumer_key': data.get('consumer_key', ''),
            'consumer_secret': data.get('consumer_secret', ''),
            'product_limit': data.get('product_limit', 6)
        }
        
        # Validate required WooCommerce fields
        if not all([woocommerce_config['url'], woocommerce_config['consumer_key'], woocommerce_config['consumer_secret']]):
            return jsonify({
                'success': False,
                'message': 'WooCommerce URL, Consumer Key, and Consumer Secret are required'
            }), 400
        
        campaign_objective = data.get('objective', 'Promote our latest products')
        product_filter = data.get('product_filter')  # Category filter
        include_images = data.get('include_images', True)
        
        result = lux_agent.create_product_campaign(
            woocommerce_config, 
            campaign_objective, 
            product_filter, 
            include_images
        )
        
        if result:
            # Create email template with product content
            template = EmailTemplate()
            template.name = f"LUX Product Campaign - {result['campaign_name']}"
            template.subject = result['subject']
            template.html_content = result['html_content']
            db.session.add(template)
            db.session.flush()
            
            # Create campaign
            campaign = Campaign()
            campaign.name = result['campaign_name']
            campaign.subject = result['subject']
            campaign.template_id = template.id
            campaign.status = 'draft'
            db.session.add(campaign)
            db.session.flush()
            
            # Add recipients
            contacts = Contact.query.filter_by(is_active=True).all()
            for contact in contacts:
                recipient = CampaignRecipient()
                recipient.campaign_id = campaign.id
                recipient.contact_id = contact.id
                db.session.add(recipient)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'campaign': {
                    'id': campaign.id,
                    'name': campaign.name,
                    'subject': campaign.subject,
                    'product_count': result['product_count'],
                    'featured_products': result['featured_products'],
                    'campaign_image': result['campaign_image'],
                    'recipients_count': len(contacts)
                },
                'message': f'Product campaign created with {result["product_count"]} products'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Unable to create product campaign. Please check your WooCommerce API credentials.'
            }), 500
            
    except Exception as e:
        logger.error(f"LUX product campaign error: {e}")
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

@main_bp.route('/lux/test-woocommerce', methods=['POST'])
@login_required
def lux_test_woocommerce():
    """Test WooCommerce API connection"""
    try:
        from ai_agent import lux_agent
        
        data = request.get_json() or {}
        
        # Test connection by fetching a few products
        products = lux_agent.fetch_woocommerce_products(
            data.get('woocommerce_url', ''),
            data.get('consumer_key', ''),
            data.get('consumer_secret', ''),
            product_limit=3
        )
        
        if products:
            return jsonify({
                'success': True,
                'message': f'Connected successfully! Found {len(products)} products.',
                'sample_products': products[:3]
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Unable to connect to WooCommerce. Please check your API credentials and URL.'
            }), 400
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"WooCommerce test error: {e}")
        
        # Handle specific error types
        if "proxies" in error_msg or "Client.__init__()" in error_msg or "woocommerce" in error_msg.lower():
            error_msg = "WooCommerce library conflict detected. The system will use pure requests implementation instead. Please try again."
        elif "timeout" in error_msg.lower():
            error_msg = "Connection timeout. Please check your WooCommerce store URL."
        elif "404" in error_msg:
            error_msg = "WooCommerce API not found. Please check your store URL and ensure WooCommerce REST API is enabled."
        elif "401" in error_msg or "unauthorized" in error_msg.lower():
            error_msg = "Invalid consumer key or secret. Please check your WooCommerce API credentials."
        
        return jsonify({
            'success': False,
            'message': f'Connection failed: {error_msg}'
        }), 500

# Drag & Drop Email Editor Routes
@main_bp.route('/editor')
@login_required
def drag_drop_editor():
    """Drag and drop email editor"""
    brandkits = BrandKit.query.filter_by(is_default=True).first()
    return render_template('drag_drop_editor.html', brandkit=brandkits)

@main_bp.route('/editor/save', methods=['POST'])
@login_required  
def save_drag_drop_template():
    """Save template from drag and drop editor"""
    try:
        name = request.form.get('name')
        subject = request.form.get('subject')
        html_content = request.form.get('html_content')
        template_type = request.form.get('template_type', 'custom')
        
        if not name or not subject or not html_content:
            return jsonify({'success': False, 'message': 'Missing required fields'})
            
        # Create new template
        template = EmailTemplate()
        template.name = name
        template.subject = subject
        template.html_content = html_content
        template.template_type = template_type
        
        db.session.add(template)
        db.session.commit()
        
        logger.info(f"Template '{name}' saved successfully by user {current_user.username}")
        return jsonify({'success': True, 'template_id': template.id})
        
    except Exception as e:
        logger.error(f"Error saving template: {e}")
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

# AI Content Generation Routes
@main_bp.route('/ai/generate-content', methods=['POST'])
@login_required
def generate_ai_content():
    """Generate AI content for emails"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        content_type = data.get('content_type', 'email_content')
        
        if not prompt:
            return jsonify({'success': False, 'message': 'Prompt is required'})
            
        # Generate content using LUX AI agent
        content_options = lux_agent.generate_email_content(prompt, content_type)
        
        return jsonify({'success': True, 'content': content_options})
        
    except Exception as e:
        logger.error(f"Error generating AI content: {e}")
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/ai/generate-subject-lines', methods=['POST'])
@login_required
def generate_subject_lines():
    """Generate AI subject line suggestions"""
    try:
        data = request.get_json()
        campaign_type = data.get('campaign_type', '')
        audience = data.get('audience', '')
        
        subject_lines = lux_agent.generate_subject_lines(campaign_type, audience)
        
        return jsonify({'success': True, 'subject_lines': subject_lines})
        
    except Exception as e:
        logger.error(f"Error generating subject lines: {e}")
        return jsonify({'success': False, 'message': str(e)})

# BrandKit Management Routes
@main_bp.route('/brandkit')
@login_required
def brandkit_management():
    """BrandKit management page"""
    brandkits = BrandKit.query.all()
    return render_template('brandkit.html', brandkits=brandkits)

@main_bp.route('/brandkit/create', methods=['POST'])
@login_required
def create_brandkit():
    """Create new BrandKit"""
    try:
        name = request.form.get('name')
        logo_url = request.form.get('logo_url')
        primary_color = request.form.get('primary_color')
        secondary_color = request.form.get('secondary_color')
        accent_color = request.form.get('accent_color')
        primary_font = request.form.get('primary_font')
        secondary_font = request.form.get('secondary_font')
        
        brandkit = BrandKit()
        brandkit.name = name
        brandkit.logo_url = logo_url
        brandkit.primary_color = primary_color
        brandkit.secondary_color = secondary_color
        brandkit.accent_color = accent_color
        brandkit.primary_font = primary_font
        brandkit.secondary_font = secondary_font
        
        db.session.add(brandkit)
        db.session.commit()
        
        flash('BrandKit created successfully!', 'success')
        return redirect(url_for('main.brandkit_management'))
        
    except Exception as e:
        logger.error(f"Error creating BrandKit: {e}")
        flash('Error creating BrandKit', 'error')
        return redirect(url_for('main.brandkit_management'))

# Poll and Survey Routes
@main_bp.route('/polls')
@login_required
def polls_management():
    """Polls and surveys management"""
    polls = Poll.query.filter_by(is_active=True).all()
    return render_template('polls.html', polls=polls)

@main_bp.route('/polls/create', methods=['POST'])
@login_required
def create_poll():
    """Create new poll"""
    try:
        question = request.form.get('question')
        poll_type = request.form.get('poll_type', 'multiple_choice')
        options = request.form.getlist('options[]')
        
        poll = Poll()
        poll.question = question
        poll.poll_type = poll_type
        poll.options = options
        
        db.session.add(poll)
        db.session.commit()
        
        flash('Poll created successfully!', 'success')
        return redirect(url_for('main.polls_management'))
        
    except Exception as e:
        logger.error(f"Error creating poll: {e}")
        flash('Error creating poll', 'error')
        return redirect(url_for('main.polls_management'))

@main_bp.route('/polls/<int:poll_id>/respond', methods=['POST'])
def respond_to_poll(poll_id):
    """Submit poll response (public endpoint)"""
    try:
        poll = Poll.query.get_or_404(poll_id)
        contact_id = request.form.get('contact_id')
        response_data = request.form.get('response_data')
        
        if contact_id and response_data:
            poll_response = PollResponse()
            poll_response.poll_id = poll_id
            poll_response.contact_id = contact_id
            poll_response.response_data = json.loads(response_data)
            
            db.session.add(poll_response)
            db.session.commit()
            
        return jsonify({'success': True})
        
    except Exception as e:
        logger.error(f"Error submitting poll response: {e}")
        return jsonify({'success': False, 'message': str(e)})

# A/B Testing Routes
@main_bp.route('/ab-tests')
@login_required
def ab_tests():
    """A/B testing management"""
    tests = ABTest.query.all()
    draft_campaigns = Campaign.query.filter_by(status='draft').all()
    return render_template('ab_tests.html', tests=tests, draft_campaigns=draft_campaigns)

@main_bp.route('/ab-tests/create', methods=['POST'])
@login_required
def create_ab_test():
    """Create new A/B test"""
    try:
        campaign_id = request.form.get('campaign_id')
        test_type = request.form.get('test_type', 'subject_line')
        variant_a = request.form.get('variant_a')
        variant_b = request.form.get('variant_b')
        split_ratio = float(request.form.get('split_ratio', 0.5))
        
        if not campaign_id or not variant_a or not variant_b:
            flash('Campaign, Variant A, and Variant B are required', 'error')
            return redirect(url_for('main.ab_tests'))
        
        # Validate campaign exists
        campaign = Campaign.query.get(campaign_id)
        if not campaign:
            flash('Selected campaign not found', 'error')
            return redirect(url_for('main.ab_tests'))
        
        ab_test = ABTest()
        ab_test.campaign_id = campaign_id
        ab_test.test_type = test_type
        ab_test.variant_a = variant_a
        ab_test.variant_b = variant_b
        ab_test.split_ratio = split_ratio
        ab_test.status = 'draft'
        
        db.session.add(ab_test)
        db.session.commit()
        
        flash('A/B test created successfully!', 'success')
        return redirect(url_for('main.ab_tests'))
        
    except Exception as e:
        logger.error(f"Error creating A/B test: {e}")
        db.session.rollback()
        flash('Error creating A/B test', 'error')
        return redirect(url_for('main.ab_tests'))

# Contact Segmentation Routes
@main_bp.route('/segments')
@login_required
def segments():
    """Contact segmentation management"""
    segments = Segment.query.all()
    return render_template('segments.html', segments=segments)

@main_bp.route('/segments/create', methods=['POST'])
@login_required
def create_segment():
    """Create new contact segment"""
    try:
        name = request.form.get('name')
        description = request.form.get('description')
        segment_type = request.form.get('segment_type', 'behavioral')
        conditions = request.form.get('conditions')
        is_dynamic = request.form.get('is_dynamic') == 'on'
        
        segment = Segment()
        segment.name = name
        segment.description = description
        segment.segment_type = segment_type
        segment.conditions = json.loads(conditions) if conditions else {}
        segment.is_dynamic = is_dynamic
        
        db.session.add(segment)
        db.session.commit()
        
        flash('Segment created successfully!', 'success')
        return redirect(url_for('main.segments'))
        
    except Exception as e:
        logger.error(f"Error creating segment: {e}")
        flash('Error creating segment', 'error')
        return redirect(url_for('main.segments'))

# Social Media Management Routes
@main_bp.route('/social')
@login_required
def social_media():
    """Social media management dashboard"""
    posts = SocialPost.query.order_by(SocialPost.created_at.desc()).limit(20).all()
    return render_template('social_media.html', posts=posts)

@main_bp.route('/social/create', methods=['POST'])
@login_required
def create_social_post():
    """Create new social media post"""
    try:
        content = request.form.get('content')
        platforms = request.form.getlist('platforms[]')
        scheduled_at = request.form.get('scheduled_at')
        
        post = SocialPost()
        post.content = content
        post.platforms = platforms
        post.scheduled_at = datetime.fromisoformat(scheduled_at) if scheduled_at else None
        
        db.session.add(post)
        db.session.commit()
        
        flash('Social media post created successfully!', 'success')
        return redirect(url_for('main.social_media'))
        
    except Exception as e:
        logger.error(f"Error creating social post: {e}")
        flash('Error creating social post', 'error')
        return redirect(url_for('main.social_media'))

# Advanced Automation Management Routes
@main_bp.route('/automations')
@login_required
def automation_dashboard():
    """Advanced automation management dashboard"""
    automations = Automation.query.all()
    templates = AutomationTemplate.query.filter_by(is_predefined=True).all()
    active_executions = AutomationExecution.query.filter_by(status='active').count()
    
    return render_template('automation_dashboard.html', 
                         automations=automations, 
                         templates=templates,
                         active_executions=active_executions)

@main_bp.route('/automations/create', methods=['GET', 'POST'])
@login_required
def create_automation():
    """Create new automation workflow"""
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            description = request.form.get('description')
            trigger_type = request.form.get('trigger_type')
            trigger_conditions = request.form.get('trigger_conditions')
            
            automation = Automation()
            automation.name = name
            automation.description = description
            automation.trigger_type = trigger_type
            automation.trigger_conditions = json.loads(trigger_conditions) if trigger_conditions else {}
            
            db.session.add(automation)
            db.session.commit()
            
            flash('Automation workflow created successfully!', 'success')
            return redirect(url_for('main.edit_automation', id=automation.id))
            
        except Exception as e:
            logger.error(f"Error creating automation: {e}")
            flash('Error creating automation workflow', 'error')
            return redirect(url_for('main.automation_dashboard'))
    
    templates = AutomationTemplate.query.filter_by(is_predefined=True).all()
    email_templates = EmailTemplate.query.all()
    return render_template('create_automation.html', templates=templates, email_templates=email_templates)

@main_bp.route('/automations/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_automation(id):
    """Edit automation workflow with visual builder"""
    automation = Automation.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Update automation details
            automation.name = request.form.get('name')
            automation.description = request.form.get('description')
            automation.trigger_type = request.form.get('trigger_type')
            trigger_conditions = request.form.get('trigger_conditions')
            automation.trigger_conditions = json.loads(trigger_conditions) if trigger_conditions else {}
            
            # Update steps from visual builder
            steps_data = request.form.get('steps_data')
            if steps_data:
                steps = json.loads(steps_data)
                
                # Delete existing steps
                AutomationStep.query.filter_by(automation_id=id).delete()
                
                # Create new steps
                for i, step_data in enumerate(steps):
                    step = AutomationStep()
                    step.automation_id = id
                    step.step_type = step_data.get('type')
                    step.step_order = i
                    step.template_id = step_data.get('template_id')
                    step.delay_hours = step_data.get('delay_hours', 0)
                    step.conditions = step_data.get('conditions', {})
                    
                    db.session.add(step)
            
            db.session.commit()
            flash('Automation updated successfully!', 'success')
            return redirect(url_for('main.automation_dashboard'))
            
        except Exception as e:
            logger.error(f"Error updating automation: {e}")
            db.session.rollback()
            flash('Error updating automation', 'error')
    
    steps = AutomationStep.query.filter_by(automation_id=id).order_by(AutomationStep.step_order).all()
    email_templates = EmailTemplate.query.all()
    executions = AutomationExecution.query.filter_by(automation_id=id).limit(10).all()
    
    return render_template('edit_automation.html', 
                         automation=automation, 
                         steps=steps,
                         email_templates=email_templates,
                         executions=executions)

@main_bp.route('/automations/<int:id>/toggle', methods=['POST'])
@login_required
def toggle_automation(id):
    """Enable/disable automation workflow"""
    try:
        automation = Automation.query.get_or_404(id)
        automation.is_active = not automation.is_active
        db.session.commit()
        
        status = 'activated' if automation.is_active else 'deactivated'
        flash(f'Automation {status} successfully!', 'success')
        
        return jsonify({'success': True, 'is_active': automation.is_active})
    except Exception as e:
        logger.error(f"Error toggling automation: {e}")
        return jsonify({'success': False, 'message': str(e)})

@main_bp.route('/automation-templates')
@login_required
def automation_templates():
    """Automation template library"""
    predefined = AutomationTemplate.query.filter_by(is_predefined=True).all()
    custom = AutomationTemplate.query.filter_by(is_predefined=False).all()
    
    return render_template('automation_templates.html', 
                         predefined_templates=predefined,
                         custom_templates=custom)

@main_bp.route('/automation-templates/create-from-template/<int:template_id>')
@login_required
def create_from_template(template_id):
    """Create automation from predefined template"""
    try:
        template = AutomationTemplate.query.get_or_404(template_id)
        template_data = template.template_data
        
        # Create automation from template
        automation = Automation()
        automation.name = f"{template.name} - Copy"
        automation.description = template.description
        automation.trigger_type = template_data.get('trigger_type', 'custom')
        automation.trigger_conditions = template_data.get('trigger_conditions', {})
        
        db.session.add(automation)
        db.session.flush()
        
        # Create steps from template
        for i, step_data in enumerate(template_data.get('steps', [])):
            step = AutomationStep()
            step.automation_id = automation.id
            step.step_type = step_data.get('type')
            step.step_order = i
            step.delay_hours = step_data.get('delay_hours', 0)
            step.conditions = step_data.get('conditions', {})
            
            db.session.add(step)
        
        # Update usage count
        template.usage_count += 1
        
        db.session.commit()
        
        flash(f'Created automation from template: {template.name}', 'success')
        return redirect(url_for('main.edit_automation', id=automation.id))
        
    except Exception as e:
        logger.error(f"Error creating from template: {e}")
        flash('Error creating automation from template', 'error')
        return redirect(url_for('main.automation_templates'))

@main_bp.route('/automation-analytics')
@login_required
def automation_analytics():
    """Automation performance analytics"""
    total_automations = Automation.query.count()
    active_automations = Automation.query.filter_by(is_active=True).count()
    total_executions = AutomationExecution.query.count()
    completed_executions = AutomationExecution.query.filter_by(status='completed').count()
    
    # Recent execution data
    recent_executions = AutomationExecution.query.order_by(AutomationExecution.started_at.desc()).limit(20).all()
    
    # Performance by automation
    automation_stats = []
    for automation in Automation.query.all():
        executions = AutomationExecution.query.filter_by(automation_id=automation.id)
        total = executions.count()
        completed = executions.filter_by(status='completed').count()
        completion_rate = (completed / total * 100) if total > 0 else 0
        
        automation_stats.append({
            'automation': automation,
            'total_executions': total,
            'completed': completed,
            'completion_rate': completion_rate
        })
    
    return render_template('automation_analytics.html',
                         total_automations=total_automations,
                         active_automations=active_automations,
                         total_executions=total_executions,
                         completed_executions=completed_executions,
                         recent_executions=recent_executions,
                         automation_stats=automation_stats)

# Non-Opener Resend Feature
@main_bp.route('/campaigns/<int:campaign_id>/resend-non-openers', methods=['GET', 'POST'])
@login_required
def setup_non_opener_resend(campaign_id):
    """Set up automatic resend to non-openers"""
    campaign = Campaign.query.get_or_404(campaign_id)
    
    if request.method == 'POST':
        try:
            hours_after = int(request.form.get('hours_after', 24))
            new_subject = request.form.get('new_subject_line')
            
            resend = NonOpenerResend()
            resend.original_campaign_id = campaign_id
            resend.hours_after_original = hours_after
            resend.new_subject_line = new_subject
            resend.scheduled_at = campaign.sent_at + timedelta(hours=hours_after) if campaign.sent_at else None
            
            db.session.add(resend)
            db.session.commit()
            
            flash('Non-opener resend scheduled successfully!', 'success')
            return redirect(url_for('main.campaign_details', id=campaign_id))
            
        except Exception as e:
            logger.error(f"Error setting up resend: {e}")
            flash('Error setting up resend', 'error')
    
    return render_template('setup_non_opener_resend.html', campaign=campaign)

# Web Forms & Landing Pages Routes
@main_bp.route('/forms')
@login_required
def forms_dashboard():
    """Web forms management dashboard"""
    forms = WebForm.query.all()
    total_submissions = FormSubmission.query.count()
    
    return render_template('forms_dashboard.html', forms=forms, total_submissions=total_submissions)

@main_bp.route('/forms/create', methods=['GET', 'POST'])
@login_required
def create_web_form():
    """Create new web signup form"""
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            title = request.form.get('title')
            description = request.form.get('description')
            fields_data = request.form.get('fields_data')
            success_message = request.form.get('success_message')
            redirect_url = request.form.get('redirect_url')
            
            form = WebForm()
            form.name = name
            form.title = title
            form.description = description
            form.fields = json.loads(fields_data) if fields_data else []
            form.success_message = success_message
            form.redirect_url = redirect_url
            
            db.session.add(form)
            db.session.commit()
            
            flash('Web form created successfully!', 'success')
            return redirect(url_for('main.forms_dashboard'))
            
        except Exception as e:
            logger.error(f"Error creating form: {e}")
            flash('Error creating web form', 'error')
    
    return render_template('create_web_form.html')

@main_bp.route('/forms/<int:id>/embed-code')
@login_required
def form_embed_code(id):
    """Get embed code for web form"""
    form = WebForm.query.get_or_404(id)
    
    embed_html = f"""
<div id="lux-form-{form.id}"></div>
<script>
(function() {{
    var script = document.createElement('script');
    script.src = '{request.url_root}static/js/form-embed.js';
    script.onload = function() {{
        LuxForm.render({form.id}, 'lux-form-{form.id}');
    }};
    document.head.appendChild(script);
}})();
</script>
    """
    
    return jsonify({'embed_code': embed_html})

@main_bp.route('/landing-pages')
@login_required
def landing_pages():
    """Landing pages management"""
    try:
        pages = LandingPage.query.all()
        try:
            forms = WebForm.query.all()
        except Exception as e:
            logger.warning(f"WebForm table not found: {e}")
            forms = []
        
        return render_template('landing_pages.html', pages=pages, forms=forms)
    except Exception as e:
        logger.error(f"Error loading landing pages: {e}")
        flash('Error loading landing pages. Please check database tables.', 'error')
        return redirect(url_for('main.dashboard'))

@main_bp.route('/landing-pages/create', methods=['GET', 'POST'])
@login_required
def create_landing_page():
    """Create new landing page"""
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            title = request.form.get('title')
            slug = request.form.get('slug')
            html_content = request.form.get('html_content')
            css_styles = request.form.get('css_styles')
            meta_description = request.form.get('meta_description')
            form_id = request.form.get('form_id') or None
            
            # Validate required fields
            if not name or not slug or not html_content:
                flash('Please fill in all required fields', 'error')
                return redirect(url_for('main.create_landing_page'))
            
            # Validate slug format (lowercase, letters, numbers, hyphens only)
            import re
            if not re.match(r'^[a-z0-9-]+$', slug):
                flash('URL slug must contain only lowercase letters, numbers, and hyphens', 'error')
                return redirect(url_for('main.create_landing_page'))
            
            # Check if slug already exists
            existing_page = LandingPage.query.filter_by(slug=slug).first()
            if existing_page:
                flash(f'A landing page with slug "{slug}" already exists', 'error')
                return redirect(url_for('main.create_landing_page'))
            
            page = LandingPage()
            page.name = name
            page.title = title
            page.slug = slug
            page.html_content = html_content
            page.css_styles = css_styles
            page.meta_description = meta_description
            page.form_id = int(form_id) if form_id else None
            
            db.session.add(page)
            db.session.commit()
            
            flash('Landing page created successfully!', 'success')
            return redirect(url_for('main.landing_pages'))
            
        except Exception as e:
            logger.error(f"Error creating landing page: {e}")
            flash(f'Error creating landing page: {str(e)}', 'error')
            db.session.rollback()
    
    try:
        forms = WebForm.query.all()
    except Exception as e:
        logger.warning(f"WebForm table not found: {e}")
        forms = []
    
    return render_template('create_landing_page.html', forms=forms)

@main_bp.route('/newsletter-archive')
def newsletter_archive():
    """Public newsletter archive"""
    newsletters = NewsletterArchive.query.filter_by(is_public=True).order_by(NewsletterArchive.published_at.desc()).all()
    
    return render_template('newsletter_archive_public.html', newsletters=newsletters)

@main_bp.route('/newsletter-archive/<slug>')
def view_newsletter(slug):
    """View individual newsletter"""
    newsletter = NewsletterArchive.query.filter_by(slug=slug, is_public=True).first_or_404()
    
    # Increment view count
    newsletter.view_count += 1
    db.session.commit()
    
    return render_template('newsletter_view.html', newsletter=newsletter)

# SMS Marketing Routes
@main_bp.route('/sms')
@login_required
def sms_campaigns():
    """SMS marketing campaigns dashboard"""
    campaigns = SMSCampaign.query.order_by(SMSCampaign.created_at.desc()).all()
    
    from sms_service import SMSService
    sms_service = SMSService()
    
    return render_template('sms_campaigns.html', 
                         campaigns=campaigns,
                         sms_enabled=sms_service.enabled)

@main_bp.route('/sms/create', methods=['GET', 'POST'])
@login_required
def create_sms_campaign():
    """Create new SMS campaign"""
    if request.method == 'POST':
        try:
            from sms_service import SMSService
            sms_service = SMSService()
            
            if not sms_service.enabled:
                flash('SMS service not configured. Please add Twilio credentials.', 'error')
                return redirect(url_for('main.sms_campaigns'))
            
            name = request.form.get('name')
            message = request.form.get('message', '')
            tags = request.form.get('tags', '').split(',')
            tags = [t.strip() for t in tags if t.strip()]
            
            # Validate message
            if not message:
                flash('Message is required', 'error')
                return redirect(url_for('main.create_sms_campaign'))
            
            # Validate message length (160 chars for single SMS)
            if len(message) > 160:
                flash('Warning: Message exceeds 160 characters and will be sent as multiple SMS', 'warning')
            
            # Create campaign
            campaign = SMSCampaign()
            campaign.name = name
            campaign.message = message[:160]  # Truncate to SMS limit
            campaign.status = 'draft'
            
            db.session.add(campaign)
            db.session.flush()
            
            # Add recipients based on tags
            if tags:
                if 'all' in tags:
                    contacts = Contact.query.filter_by(is_active=True).filter(Contact.phone.isnot(None)).all()
                else:
                    contacts = Contact.query.filter_by(is_active=True).filter(Contact.phone.isnot(None)).all()
                    contacts = [c for c in contacts if c.tags and any(tag in c.tags for tag in tags)]
            else:
                contacts = Contact.query.filter_by(is_active=True).filter(Contact.phone.isnot(None)).all()
            
            for contact in contacts:
                if contact.phone and sms_service.validate_phone_number(contact.phone):
                    recipient = SMSRecipient()
                    recipient.campaign_id = campaign.id
                    recipient.contact_id = contact.id
                    recipient.status = 'pending'
                    db.session.add(recipient)
            
            db.session.commit()
            
            flash(f'SMS campaign created with {len(contacts)} recipients!', 'success')
            return redirect(url_for('main.sms_campaigns'))
            
        except Exception as e:
            logger.error(f"Error creating SMS campaign: {e}")
            db.session.rollback()
            flash('Error creating SMS campaign', 'error')
    
    contacts_with_phone = Contact.query.filter_by(is_active=True).filter(Contact.phone.isnot(None)).count()
    return render_template('create_sms_campaign.html', contacts_with_phone=contacts_with_phone)

@main_bp.route('/sms/<int:campaign_id>/send', methods=['POST'])
@login_required
def send_sms_campaign(campaign_id):
    """Send SMS campaign"""
    try:
        from sms_service import SMSService
        from datetime import datetime
        
        campaign = SMSCampaign.query.get_or_404(campaign_id)
        
        if campaign.status not in ['draft', 'scheduled']:
            flash('Campaign cannot be sent in current status', 'error')
            return redirect(url_for('main.sms_campaigns'))
        
        sms_service = SMSService()
        if not sms_service.enabled:
            flash('SMS service not configured', 'error')
            return redirect(url_for('main.sms_campaigns'))
        
        # Update campaign status
        campaign.status = 'sending'
        campaign.sent_at = datetime.utcnow()
        db.session.commit()
        
        # Send to all pending recipients
        recipients = SMSRecipient.query.filter_by(
            campaign_id=campaign_id,
            status='pending'
        ).all()
        
        sent = 0
        failed = 0
        
        for recipient in recipients:
            contact = Contact.query.get(recipient.contact_id)
            if not contact or not contact.phone:
                recipient.status = 'failed'
                recipient.error_message = 'No phone number'
                failed += 1
                continue
            
            # COMPLIANCE: Check opt-out and consent
            if not contact.is_active:
                recipient.status = 'failed'
                recipient.error_message = 'Contact opted out or inactive'
                failed += 1
                logger.info(f"Skipped sending SMS to {contact.email} - opted out or inactive")
                continue
            
            result = sms_service.send_sms(contact.phone, campaign.message)
            
            if result['success']:
                recipient.status = 'sent'
                recipient.sent_at = datetime.utcnow()
                sent += 1
            else:
                recipient.status = 'failed'
                recipient.error_message = result.get('error', 'Unknown error')
                failed += 1
            
            db.session.commit()
        
        campaign.status = 'sent'
        db.session.commit()
        
        flash(f'SMS campaign sent! {sent} sent, {failed} failed', 'success' if failed == 0 else 'warning')
        
    except Exception as e:
        logger.error(f"Error sending SMS campaign: {e}")
        flash('Error sending SMS campaign', 'error')
    
    return redirect(url_for('main.sms_campaigns'))

# SEO Tools Routes
@main_bp.route('/seo')
@login_required
def seo_tools():
    """SEO analysis and optimization tools"""
    return render_template('seo_tools.html')

@main_bp.route('/seo/analyze', methods=['POST'])
@login_required
def analyze_seo():
    """Analyze a URL for SEO"""
    try:
        url = request.form.get('url')
        
        if not url:
            flash('Please enter a URL to analyze', 'error')
            return redirect(url_for('main.seo_tools'))
        
        # Ensure URL has a protocol
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        result = seo_service.analyze_page(url)
        
        if result['success']:
            return render_template('seo_results.html', analysis=result['data'])
        else:
            flash(f'Error analyzing URL: {result["error"]}', 'error')
            return redirect(url_for('main.seo_tools'))
        
    except Exception as e:
        logger.error(f"Error in SEO analysis: {e}")
        flash('Error analyzing URL', 'error')
        return redirect(url_for('main.seo_tools'))

# Events Management Routes
@main_bp.route('/events')
@login_required
def events_dashboard():
    """Events management dashboard"""
    events = Event.query.order_by(Event.start_date.desc()).all()
    return render_template('events.html', events=events)

@main_bp.route('/events/create', methods=['GET', 'POST'])
@login_required
def create_event():
    """Create new event"""
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            description = request.form.get('description')
            start_date_str = request.form.get('start_date')
            end_date_str = request.form.get('end_date')
            location = request.form.get('location')
            max_attendees = request.form.get('max_attendees')
            price = request.form.get('price', 0.0)
            
            if not start_date_str:
                flash('Start date is required', 'error')
                return redirect(url_for('main.create_event'))
            
            event = Event()
            event.name = name
            event.description = description
            event.start_date = datetime.fromisoformat(start_date_str)
            event.end_date = datetime.fromisoformat(end_date_str) if end_date_str else None
            event.location = location
            event.max_attendees = int(max_attendees) if max_attendees else None
            event.price = float(price)
            
            db.session.add(event)
            db.session.commit()
            
            flash('Event created successfully!', 'success')
            return redirect(url_for('main.events_dashboard'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating event: {e}")
            flash('Error creating event', 'error')
            return redirect(url_for('main.events_dashboard'))
    
    return render_template('create_event.html')

@main_bp.route('/events/<int:event_id>')
@login_required
def view_event(event_id):
    """View event details and registrations"""
    event = Event.query.get_or_404(event_id)
    registrations = EventRegistration.query.filter_by(event_id=event_id).all()
    
    # Get contacts for registrations
    for reg in registrations:
        reg.contact = Contact.query.get(reg.contact_id)
    
    return render_template('view_event.html', event=event, registrations=registrations)

# WooCommerce Integration Routes
@main_bp.route('/woocommerce')
@login_required
def woocommerce_dashboard():
    """WooCommerce integration dashboard"""
    from woocommerce_service import WooCommerceService
    wc_service = WooCommerceService()
    
    if not wc_service.is_configured():
        flash('WooCommerce integration is not configured. Please add WooCommerce credentials.', 'warning')
        return render_template('woocommerce_setup.html')
    
    try:
        # Get products summary
        products = wc_service.get_products(per_page=10)
        product_count = len(products) if products else 0
        
        # Get recent orders
        orders = wc_service.get_orders(per_page=5)
        order_count = len(orders) if orders else 0
        
        return render_template('woocommerce_dashboard.html', 
                             products=products,
                             product_count=product_count,
                             orders=orders,
                             order_count=order_count,
                             is_configured=True)
    except Exception as e:
        logger.error(f"WooCommerce error: {e}")
        flash('Error connecting to WooCommerce. Please check your credentials.', 'error')
        return render_template('woocommerce_setup.html')

@main_bp.route('/woocommerce/products')
@login_required
def woocommerce_products():
    """View WooCommerce products"""
    from woocommerce_service import WooCommerceService
    wc_service = WooCommerceService()
    
    if not wc_service.is_configured():
        flash('WooCommerce integration is not configured.', 'warning')
        return redirect(url_for('main.woocommerce_dashboard'))
    
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    
    if search:
        products = wc_service.search_products(search, per_page=20)
    else:
        products = wc_service.get_products(page=page, per_page=20)
    
    return render_template('woocommerce_products.html', 
                         products=products or [],
                         search=search,
                         page=page)

@main_bp.route('/woocommerce/products/<int:product_id>')
@login_required
def woocommerce_product_detail(product_id):
    """View single WooCommerce product"""
    from woocommerce_service import WooCommerceService
    wc_service = WooCommerceService()
    
    product = wc_service.get_product(product_id)
    if not product:
        flash('Product not found', 'error')
        return redirect(url_for('main.woocommerce_products'))
    
    return render_template('woocommerce_product_detail.html', product=product)

@main_bp.route('/woocommerce/sync-products', methods=['POST'])
@login_required
def sync_woocommerce_products():
    """Sync WooCommerce products to local database"""
    from woocommerce_service import WooCommerceService
    wc_service = WooCommerceService()
    
    try:
        products = wc_service.get_all_products(max_products=500)
        
        synced_count = 0
        for wc_product in products:
            # Check if product exists
            product = Product.query.filter_by(wc_product_id=wc_product['id']).first()
            
            if not product:
                product = Product()
                product.wc_product_id = wc_product['id']
            
            # Update product data
            product.name = wc_product['name']
            product.description = wc_product['description']
            product.price = float(wc_product['price']) if wc_product['price'] else 0.0
            product.sku = wc_product.get('sku', '')
            product.stock_quantity = wc_product.get('stock_quantity', 0)
            product.image_url = wc_product['images'][0]['src'] if wc_product.get('images') else None
            product.product_url = wc_product['permalink']
            
            db.session.add(product)
            synced_count += 1
        
        db.session.commit()
        flash(f'Successfully synced {synced_count} products from WooCommerce!', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error syncing WooCommerce products: {e}")
        flash('Error syncing products from WooCommerce', 'error')
    
    return redirect(url_for('main.woocommerce_dashboard'))

@main_bp.route('/woocommerce/create-product-campaign/<int:product_id>', methods=['GET', 'POST'])
@login_required
def create_product_campaign(product_id):
    """Create email campaign for a specific product"""
    from woocommerce_service import WooCommerceService
    wc_service = WooCommerceService()
    
    # Get product from WooCommerce
    product = wc_service.get_product(product_id)
    if not product:
        flash('Product not found', 'error')
        return redirect(url_for('main.woocommerce_products'))
    
    if request.method == 'POST':
        try:
            campaign_name = request.form.get('campaign_name')
            subject = request.form.get('subject')
            tag = request.form.get('tag')
            
            # Create campaign
            campaign = Campaign()
            campaign.name = campaign_name
            campaign.subject = subject
            campaign.status = 'draft'
            
            # Generate email content from product
            product_html = f"""
            <div style="max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif;">
                <h1 style="color: #333;">{product['name']}</h1>
                {'<img src="' + product['images'][0]['src'] + '" style="max-width: 100%; height: auto;" />' if product.get('images') else ''}
                <div style="margin: 20px 0;">
                    <h2 style="color: #0066cc;">Price: ${product['price']}</h2>
                </div>
                <div style="margin: 20px 0;">
                    {product.get('description', '')}
                </div>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{product['permalink']}" style="background: #0066cc; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                        Shop Now
                    </a>
                </div>
            </div>
            """
            
            # Create template for this campaign
            template = EmailTemplate()
            template.name = f"Product Campaign - {product['name']}"
            template.subject = subject
            template.html_content = product_html
            
            db.session.add(template)
            db.session.flush()
            
            campaign.template_id = template.id
            db.session.add(campaign)
            db.session.commit()
            
            flash(f'Product campaign created successfully!', 'success')
            return redirect(url_for('main.campaign_details', id=campaign.id))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating product campaign: {e}")
            flash('Error creating campaign', 'error')
    
    return render_template('create_product_campaign.html', product=product)

# AI Agent Dashboard Routes
@main_bp.route('/agents')
@login_required
def agents_dashboard():
    """AI Agents Dashboard - View and manage all marketing agents"""
    from models import AgentTask, AgentLog, AgentReport, AgentSchedule
    from agent_scheduler import get_agent_scheduler
    
    # Get scheduler and job information
    scheduler = get_agent_scheduler()
    scheduled_jobs = scheduler.get_scheduled_jobs() if scheduler else []
    
    # Get recent agent activity
    recent_logs = AgentLog.query.order_by(AgentLog.created_at.desc()).limit(20).all()
    pending_tasks = AgentTask.query.filter_by(status='pending').order_by(AgentTask.scheduled_at).all()
    recent_reports = AgentReport.query.order_by(AgentReport.created_at.desc()).limit(10).all()
    
    # Get agent stats
    agent_stats = {}
    agent_types = ['brand_strategy', 'content_seo', 'analytics', 'creative_design']
    
    for agent_type in agent_types:
        total_tasks = AgentTask.query.filter_by(agent_type=agent_type).count()
        completed_tasks = AgentTask.query.filter_by(agent_type=agent_type, status='completed').count()
        failed_tasks = AgentTask.query.filter_by(agent_type=agent_type, status='failed').count()
        
        agent_stats[agent_type] = {
            'total': total_tasks,
            'completed': completed_tasks,
            'failed': failed_tasks,
            'success_rate': round((completed_tasks / max(total_tasks, 1)) * 100, 1)
        }
    
    return render_template('agents_dashboard.html',
                         scheduled_jobs=scheduled_jobs,
                         recent_logs=recent_logs,
                         pending_tasks=pending_tasks,
                         recent_reports=recent_reports,
                         agent_stats=agent_stats)

@main_bp.route('/agents/<agent_type>/trigger', methods=['POST'])
@login_required
def trigger_agent(agent_type):
    """Manually trigger an agent task"""
    try:
        task_data = request.get_json() or {}
        
        # Ensure task_type is set with defaults per agent
        if 'task_type' not in task_data:
            task_type_defaults = {
                'brand_strategy': 'market_research',
                'content_seo': 'keyword_research',
                'analytics': 'performance_summary',
                'creative_design': 'generate_ad_creative',
                'advertising': 'campaign_strategy',
                'social_media': 'daily_posts',
                'email_crm': 'weekly_campaign',
                'sales_enablement': 'sales_deck',
                'retention': 'churn_analysis',
                'operations': 'system_health'
            }
            task_data['task_type'] = task_type_defaults.get(agent_type, 'default_task')
        
        # Get the appropriate agent
        agent = None
        if agent_type == 'brand_strategy':
            from agents.brand_strategy_agent import BrandStrategyAgent
            agent = BrandStrategyAgent()
        elif agent_type == 'content_seo':
            from agents.content_seo_agent import ContentSEOAgent
            agent = ContentSEOAgent()
        elif agent_type == 'analytics':
            from agents.analytics_agent import AnalyticsAgent
            agent = AnalyticsAgent()
        elif agent_type == 'creative_design':
            from agents.creative_agent import CreativeAgent
            agent = CreativeAgent()
        elif agent_type == 'advertising':
            from agents.advertising_agent import AdvertisingAgent
            agent = AdvertisingAgent()
        elif agent_type == 'social_media':
            from agents.social_media_agent import SocialMediaAgent
            agent = SocialMediaAgent()
        elif agent_type == 'email_crm':
            from agents.email_crm_agent import EmailCRMAgent
            agent = EmailCRMAgent()
        elif agent_type == 'sales_enablement':
            from agents.sales_enablement_agent import SalesEnablementAgent
            agent = SalesEnablementAgent()
        elif agent_type == 'retention':
            from agents.retention_agent import RetentionAgent
            agent = RetentionAgent()
        elif agent_type == 'operations':
            from agents.operations_agent import OperationsAgent
            agent = OperationsAgent()
        else:
            return jsonify({'success': False, 'error': 'Unknown agent type'}), 400
        
        # Create and execute task
        task_id = agent.create_task(
            task_name=task_data.get('task_name', 'Manual Trigger'),
            task_data=task_data
        )
        
        result = agent.execute(task_data)
        
        if task_id:
            agent.complete_task(
                task_id,
                result,
                status='completed' if result.get('success') else 'failed'
            )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error triggering agent {agent_type}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/agents/logs')
@login_required
def agent_logs():
    """View detailed agent logs"""
    from models import AgentLog
    
    page = request.args.get('page', 1, type=int)
    agent_type = request.args.get('agent_type', '')
    
    query = AgentLog.query
    
    if agent_type:
        query = query.filter_by(agent_type=agent_type)
    
    logs = query.order_by(AgentLog.created_at.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    
    return render_template('agent_logs.html', logs=logs, selected_agent=agent_type)

@main_bp.route('/agents/reports')
@login_required
def agent_reports():
    """View agent-generated reports"""
    from models import AgentReport
    
    page = request.args.get('page', 1, type=int)
    report_type = request.args.get('report_type', '')
    
    query = AgentReport.query
    
    if report_type:
        query = query.filter_by(report_type=report_type)
    
    reports = query.order_by(AgentReport.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('agent_reports.html', reports=reports, selected_type=report_type)

@main_bp.route('/agents/reports/<int:report_id>')
@login_required
def view_agent_report(report_id):
    """View detailed agent report"""
    from models import AgentReport
    
    report = AgentReport.query.get_or_404(report_id)
    
    return render_template('view_agent_report.html', report=report)
