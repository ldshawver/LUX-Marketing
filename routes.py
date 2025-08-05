import csv
import io
import base64
from datetime import datetime
from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, make_response
from flask_login import login_required, current_user
from sqlalchemy import or_
from app import db
from models import Contact, Campaign, EmailTemplate, CampaignRecipient, EmailTracking
from email_service import EmailService
from utils import validate_email
from tracking import decode_tracking_data, record_email_event
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
                         top_campaigns=top_campaigns)

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
        
        recommendations = lux_agent.get_campaign_recommendations()
        
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
