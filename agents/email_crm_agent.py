"""
Email & CRM Agent
Enhanced email campaign management with automation and advanced segmentation
"""
import logging
from datetime import datetime
from typing import Dict, Any
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class EmailCRMAgent(BaseAgent):
    """AI Agent for email campaigns and CRM management"""
    
    def __init__(self):
        super().__init__(
            agent_name="Email & CRM Agent",
            agent_type="email_crm",
            description="Email campaigns, automation flows, and CRM segmentation"
        )
    
    def _define_personality(self) -> str:
        return """
        You are the Email & CRM Agent, an expert in email marketing, marketing automation,
        and customer relationship management. You create personalized campaigns and optimize
        customer journeys for maximum engagement and conversion.
        """
    
    def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute email/CRM task"""
        task_type = task_data.get('task_type', 'weekly_campaign')
        
        if task_type == 'weekly_campaign':
            return self.create_weekly_campaign(task_data)
        elif task_type == 'drip_sequence':
            return self.design_drip_sequence(task_data)
        elif task_type == 'segmentation':
            return self.advanced_segmentation(task_data)
        elif task_type == 'subscriber_sync':
            return self.sync_subscribers(task_data)
        else:
            return {'success': False, 'error': f'Unknown task type: {task_type}'}
    
    def create_weekly_campaign(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create weekly email campaign - submits to approval queue"""
        try:
            if not self.check_feature_enabled():
                return {'success': False, 'reason': 'Email & CRM Agent is disabled'}
            
            theme = params.get('theme', 'newsletter')
            
            prompt = f"""Create a compelling email campaign for a {theme}. 
            Return JSON with: {{"subject": "...", "preview_text": "...", "body": "...", "cta_text": "...", "cta_url": "..."}}"""
            
            result = self.generate_with_ai(prompt, response_format={"type": "json_object"}, temperature=0.7)
            
            if result:
                approval_result = self.submit_for_approval(
                    content_type='email_campaign',
                    title=result.get('subject', f'Weekly Campaign - {theme}'),
                    content=result,
                    target_platform='email',
                    confidence_score=0.82,
                    rationale=f"Weekly automated email campaign about {theme}"
                )
                
                self.log_activity('weekly_campaign_creation', {'theme': theme, 'submitted': approval_result.get('success')}, 'success')
                return {
                    'success': True, 
                    'message': 'Campaign submitted for admin approval',
                    'approval_id': approval_result.get('approval_id'),
                    'generated_at': datetime.now().isoformat()
                }
            return {'success': False, 'error': 'Failed to create campaign'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def design_drip_sequence(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Design email drip sequence"""
        try:
            goal = params.get('goal', 'onboarding')
            
            prompt = f"Design a 5-email drip sequence for {goal}. Include timing, subject lines, and key messages for each email."
            
            result = self.generate_with_ai(prompt, response_format={"type": "json_object"}, temperature=0.6)
            
            if result:
                return {'success': True, 'sequence': result, 'generated_at': datetime.now().isoformat()}
            return {'success': False, 'error': 'Failed to design sequence'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def advanced_segmentation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Perform advanced contact segmentation"""
        try:
            from models import Contact
            
            contacts = Contact.query.filter_by(is_active=True).limit(50).all()
            contact_data = [{'email': c.email, 'engagement_score': c.engagement_score} for c in contacts]
            
            prompt = f"Analyze these contacts and create behavior-based segments: {contact_data}"
            
            result = self.generate_with_ai(prompt, response_format={"type": "json_object"}, temperature=0.3)
            
            if result:
                return {'success': True, 'segments': result, 'generated_at': datetime.now().isoformat()}
            return {'success': False, 'error': 'Failed to segment'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def sync_subscribers(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sync contacts with newsletter subscribers"""
        try:
            from services.subscriber_sync_service import SubscriberSyncService
            
            result = SubscriberSyncService.full_sync()
            
            if result.get('success'):
                contacts_synced = result.get('contacts_to_subscribers', 0)
                tags_added = result.get('subscribers_to_contacts', 0)
                
                self.log_activity('subscriber_sync', {
                    'contacts_synced': contacts_synced,
                    'tags_added': tags_added
                }, 'success')
                
                stats = SubscriberSyncService.get_subscriber_stats()
                
                return {
                    'success': True,
                    'message': f'Synced {contacts_synced} contacts to subscribers, added newsletter tag to {tags_added} contacts',
                    'contacts_synced': contacts_synced,
                    'tags_added': tags_added,
                    'stats': stats.get('stats', {}),
                    'synced_at': datetime.now().isoformat()
                }
            
            return {'success': False, 'error': result.get('error', 'Sync failed')}
            
        except Exception as e:
            logger.error(f"Subscriber sync error: {e}")
            return {'success': False, 'error': str(e)}
