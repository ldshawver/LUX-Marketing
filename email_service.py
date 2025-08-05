import os
import logging
from datetime import datetime
from jinja2 import Template
import msal
import requests
from app import db
from models import Campaign, CampaignRecipient, EmailTracking

class EmailService:
    def __init__(self):
        self.client_id = os.environ.get("MS_CLIENT_ID", "")
        self.client_secret = os.environ.get("MS_CLIENT_SECRET", "")
        self.tenant_id = os.environ.get("MS_TENANT_ID", "")
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scope = ["https://graph.microsoft.com/.default"]
        
        if not all([self.client_id, self.client_secret, self.tenant_id]):
            logging.warning("Microsoft Graph API credentials not configured")
    
    def get_access_token(self):
        """Get access token for Microsoft Graph API"""
        try:
            app = msal.ConfidentialClientApplication(
                self.client_id,
                authority=self.authority,
                client_credential=self.client_secret
            )
            
            result = app.acquire_token_silent(self.scope, account=None)
            
            if not result:
                result = app.acquire_token_for_client(scopes=self.scope)
            
            if "access_token" in result:
                return result["access_token"]
            else:
                logging.error(f"Failed to acquire token: {result.get('error_description', 'Unknown error')}")
                return None
                
        except Exception as e:
            logging.error(f"Error getting access token: {str(e)}")
            return None
    
    def send_email(self, to_email, subject, html_content, from_email=None):
        """Send a single email using Microsoft Graph API"""
        if not from_email:
            from_email = os.environ.get("MS_FROM_EMAIL", "noreply@yourdomain.com")
        
        access_token = self.get_access_token()
        if not access_token:
            raise Exception("Failed to get access token")
        
        # Prepare email message
        message = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML",
                    "content": html_content
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": to_email
                        }
                    }
                ],
                "from": {
                    "emailAddress": {
                        "address": from_email
                    }
                }
            }
        }
        
        # Send email via Microsoft Graph API
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        endpoint = f"https://graph.microsoft.com/v1.0/users/{from_email}/sendMail"
        
        try:
            response = requests.post(endpoint, json=message, headers=headers)
            
            if response.status_code == 202:
                logging.info(f"Email sent successfully to {to_email}")
                return True
            else:
                logging.error(f"Failed to send email to {to_email}: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"Error sending email to {to_email}: {str(e)}")
            return False
    
    def render_template(self, template_html, contact, campaign):
        """Render email template with contact and campaign data"""
        try:
            template = Template(template_html)
            
            # Prepare template context
            context = {
                'contact': {
                    'first_name': contact.first_name or '',
                    'last_name': contact.last_name or '',
                    'full_name': contact.full_name,
                    'email': contact.email,
                    'company': contact.company or '',
                    'phone': contact.phone or ''
                },
                'campaign': {
                    'name': campaign.name,
                    'subject': campaign.subject
                },
                'unsubscribe_url': f"https://yourdomain.com/unsubscribe?email={contact.email}&campaign={campaign.id}",
                'tracking_pixel': f"https://yourdomain.com/track/open?campaign={campaign.id}&contact={contact.id}"
            }
            
            return template.render(**context)
            
        except Exception as e:
            logging.error(f"Error rendering template: {str(e)}")
            return template_html
    
    def send_campaign(self, campaign):
        """Send campaign to all recipients"""
        if not campaign.template:
            raise Exception("Campaign has no template")
        
        recipients = campaign.recipients.filter_by(status='pending').all()
        
        if not recipients:
            raise Exception("No pending recipients found")
        
        success_count = 0
        failed_count = 0
        
        for recipient in recipients:
            try:
                # Render email content
                html_content = self.render_template(
                    campaign.template.html_content,
                    recipient.contact,
                    campaign
                )
                
                # Send email
                success = self.send_email(
                    recipient.contact.email,
                    campaign.subject,
                    html_content
                )
                
                if success:
                    recipient.status = 'sent'
                    recipient.sent_at = datetime.utcnow()
                    success_count += 1
                    
                    # Log tracking event
                    tracking = EmailTracking(
                        campaign_id=campaign.id,
                        contact_id=recipient.contact.id,
                        event_type='sent'
                    )
                    db.session.add(tracking)
                    
                else:
                    recipient.status = 'failed'
                    recipient.error_message = 'Failed to send via Microsoft Graph API'
                    failed_count += 1
                
                db.session.commit()
                
            except Exception as e:
                logging.error(f"Error sending to recipient {recipient.id}: {str(e)}")
                recipient.status = 'failed'
                recipient.error_message = str(e)
                failed_count += 1
                db.session.commit()
        
        # Update campaign status
        if failed_count == 0:
            campaign.status = 'sent'
        elif success_count == 0:
            campaign.status = 'failed'
        else:
            campaign.status = 'partial'
        
        db.session.commit()
        
        logging.info(f"Campaign {campaign.id} completed: {success_count} sent, {failed_count} failed")
        
        return {
            'success_count': success_count,
            'failed_count': failed_count
        }
