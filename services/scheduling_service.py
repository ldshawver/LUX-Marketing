"""Scheduling Service for campaign and unified calendar scheduling"""
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SchedulingService:
    """Service for scheduling campaigns and unified calendar"""
    
    @staticmethod
    def schedule_campaign(campaign, scheduled_at):
        """Schedule a campaign for future sending"""
        campaign.scheduled_at = scheduled_at
        campaign.status = 'scheduled'
        return campaign
    
    @staticmethod
    def cancel_scheduled_campaign(campaign):
        """Cancel a scheduled campaign"""
        campaign.scheduled_at = None
        campaign.status = 'draft'
        return campaign
    
    @staticmethod
    def create_schedule(module_type, module_object_id, title, scheduled_at, description=''):
        """Create a unified schedule entry for the marketing calendar
        
        Args:
            module_type: Type of item (sms, email, social, event, automation)
            module_object_id: ID of the related object
            title: Display title for the calendar
            scheduled_at: Datetime when scheduled
            description: Optional description
            
        Returns:
            dict: Schedule info (stored in the related model, not separate table)
        """
        try:
            logger.info(f"Schedule created: {module_type} - {title} at {scheduled_at}")
            return {
                'success': True,
                'module_type': module_type,
                'module_object_id': module_object_id,
                'title': title,
                'scheduled_at': scheduled_at,
                'description': description
            }
        except Exception as e:
            logger.error(f"Error creating schedule: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def get_calendar_view(year, month):
        """Get all scheduled items for a given month
        
        This aggregates SMS campaigns, social posts, and email campaigns
        that are scheduled for the specified month.
        """
        from models import SMSCampaign, SocialPost, Campaign
        from datetime import datetime
        
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        
        calendar_data = {}
        
        sms_campaigns = SMSCampaign.query.filter(
            SMSCampaign.scheduled_at.isnot(None),
            SMSCampaign.scheduled_at >= start_date,
            SMSCampaign.scheduled_at < end_date,
            SMSCampaign.status.in_(['draft', 'scheduled'])
        ).all()
        
        for campaign in sms_campaigns:
            day = campaign.scheduled_at.day
            if day not in calendar_data:
                calendar_data[day] = []
            calendar_data[day].append({
                'type': 'sms',
                'title': campaign.name,
                'time': campaign.scheduled_at.strftime('%H:%M'),
                'id': campaign.id,
                'status': campaign.status,
                'color': 'success'
            })
        
        social_posts = SocialPost.query.filter(
            SocialPost.scheduled_at.isnot(None),
            SocialPost.scheduled_at >= start_date,
            SocialPost.scheduled_at < end_date,
            SocialPost.status.in_(['draft', 'scheduled'])
        ).all()
        
        for post in social_posts:
            day = post.scheduled_at.day
            if day not in calendar_data:
                calendar_data[day] = []
            platforms_str = ', '.join(post.platforms[:2]) if post.platforms else 'Social'
            calendar_data[day].append({
                'type': 'social',
                'title': f"{platforms_str}: {post.content[:30]}..." if post.content else platforms_str,
                'time': post.scheduled_at.strftime('%H:%M'),
                'id': post.id,
                'status': post.status,
                'color': 'primary'
            })
        
        email_campaigns = Campaign.query.filter(
            Campaign.scheduled_at.isnot(None),
            Campaign.scheduled_at >= start_date,
            Campaign.scheduled_at < end_date,
            Campaign.status.in_(['draft', 'scheduled'])
        ).all()
        
        for campaign in email_campaigns:
            day = campaign.scheduled_at.day
            if day not in calendar_data:
                calendar_data[day] = []
            calendar_data[day].append({
                'type': 'email',
                'title': campaign.name,
                'time': campaign.scheduled_at.strftime('%H:%M'),
                'id': campaign.id,
                'status': campaign.status,
                'color': 'info'
            })
        
        return calendar_data
    
    @staticmethod
    def get_upcoming_schedules(days=30):
        """Get upcoming scheduled items for the next N days"""
        from models import SMSCampaign, SocialPost, Campaign
        from datetime import datetime, timedelta
        
        now = datetime.now()
        end_date = now + timedelta(days=days)
        upcoming = []
        
        sms_campaigns = SMSCampaign.query.filter(
            SMSCampaign.scheduled_at.isnot(None),
            SMSCampaign.scheduled_at >= now,
            SMSCampaign.scheduled_at <= end_date,
            SMSCampaign.status.in_(['draft', 'scheduled'])
        ).order_by(SMSCampaign.scheduled_at).limit(10).all()
        
        for item in sms_campaigns:
            upcoming.append({
                'type': 'sms',
                'title': item.name,
                'scheduled_at': item.scheduled_at,
                'id': item.id,
                'color': 'success'
            })
        
        social_posts = SocialPost.query.filter(
            SocialPost.scheduled_at.isnot(None),
            SocialPost.scheduled_at >= now,
            SocialPost.scheduled_at <= end_date,
            SocialPost.status.in_(['draft', 'scheduled'])
        ).order_by(SocialPost.scheduled_at).limit(10).all()
        
        for item in social_posts:
            platforms_str = ', '.join(item.platforms[:2]) if item.platforms else 'Social'
            upcoming.append({
                'type': 'social',
                'title': f"{platforms_str}: {item.content[:30]}..." if item.content else platforms_str,
                'scheduled_at': item.scheduled_at,
                'id': item.id,
                'color': 'primary'
            })
        
        email_campaigns = Campaign.query.filter(
            Campaign.scheduled_at.isnot(None),
            Campaign.scheduled_at >= now,
            Campaign.scheduled_at <= end_date,
            Campaign.status.in_(['draft', 'scheduled'])
        ).order_by(Campaign.scheduled_at).limit(10).all()
        
        for item in email_campaigns:
            upcoming.append({
                'type': 'email',
                'title': item.name,
                'scheduled_at': item.scheduled_at,
                'id': item.id,
                'color': 'info'
            })
        
        upcoming.sort(key=lambda x: x['scheduled_at'])
        return upcoming[:15]
