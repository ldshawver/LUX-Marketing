import csv
import io
from datetime import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, make_response
from flask_login import login_required, current_user
from sqlalchemy import or_
from app import db
from models import Contact, Campaign, EmailTemplate, CampaignRecipient, EmailTracking
from email_service import EmailService
from utils import validate_email
import logging

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
    
    contact = Contact(
        email=email,
        first_name=first_name,
        last_name=last_name,
        company=company,
        phone=phone,
        tags=tags
    )
    
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
    
    if not file.filename.endswith('.csv'):
        flash('Please upload a CSV file', 'error')
        return redirect(url_for('main.contacts'))
    
    try:
        # Read CSV file
        stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        csv_input = csv.DictReader(stream)
        
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
            
            contact = Contact(
                email=email,
                first_name=row.get('first_name', '').strip(),
                last_name=row.get('last_name', '').strip(),
                company=row.get('company', '').strip(),
                phone=row.get('phone', '').strip(),
                tags=row.get('tags', '').strip()
            )
            
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
        campaign = Campaign(
            name=name,
            subject=subject,
            template_id=template_id,
            status='draft'
        )
        
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
            recipient = CampaignRecipient(
                campaign_id=campaign.id,
                contact_id=contact.id
            )
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

@main_bp.route('/templates/create', methods=['GET', 'POST'])
@login_required
def create_template():
    """Create a new email template"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        subject = request.form.get('subject', '').strip()
        html_content = request.form.get('html_content', '').strip()
        
        if not name or not subject or not html_content:
            flash('All fields are required', 'error')
            return redirect(url_for('main.create_template'))
        
        template = EmailTemplate(
            name=name,
            subject=subject,
            html_content=html_content
        )
        
        db.session.add(template)
        db.session.commit()
        
        flash('Template created successfully', 'success')
        return redirect(url_for('main.templates'))
    
    return render_template('template_create.html')

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
    total_pending = db.session.query(CampaignRecipient).filter_by(status='pending').count()
    
    # Recent campaign performance
    recent_campaigns = Campaign.query.filter(Campaign.sent_at.isnot(None)).order_by(Campaign.sent_at.desc()).limit(10).all()
    
    return render_template('analytics.html',
                         total_campaigns=total_campaigns,
                         sent_campaigns=sent_campaigns,
                         total_sent=total_sent,
                         total_failed=total_failed,
                         total_pending=total_pending,
                         recent_campaigns=recent_campaigns)
