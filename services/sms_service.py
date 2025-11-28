"""SMS Service for sending SMS campaigns via Twilio"""
from models import SMSCampaign, SMSRecipient, db
from datetime import datetime

class SMSService:
    """Service for SMS campaign management"""
    
    @staticmethod
    def create_campaign(name, message, scheduled_at=None):
        """Create a new SMS campaign"""
        campaign = SMSCampaign(
            name=name,
            message=message,
            status='draft' if scheduled_at else 'active',
            scheduled_at=scheduled_at,
            created_at=datetime.utcnow()
        )
        db.session.add(campaign)
        db.session.commit()
        return campaign
    
    @staticmethod
    def send_to_contact(campaign_id, contact_id, phone_number):
        """Send SMS to a specific contact"""
        # Placeholder for actual Twilio integration
        recipient = SMSRecipient(
            campaign_id=campaign_id,
            contact_id=contact_id,
            phone_number=phone_number,
            status='sent',
            sent_at=datetime.utcnow()
        )
        db.session.add(recipient)
        db.session.commit()
        return recipient
