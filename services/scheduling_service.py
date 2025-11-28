"""Scheduling Service for campaign scheduling"""
from datetime import datetime

class SchedulingService:
    """Service for scheduling campaigns"""
    
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
