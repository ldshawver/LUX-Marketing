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
        else:
            return {'success': False, 'error': f'Unknown task type: {task_type}'}
    
    def create_weekly_campaign(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create weekly email campaign"""
        try:
            theme = params.get('theme', 'newsletter')
            
            prompt = f"Create a compelling email campaign for a {theme}. Include subject line, preview text, and HTML content structure."
            
            result = self.generate_with_ai(prompt, response_format={"type": "json_object"}, temperature=0.7)
            
            if result:
                self.log_activity('weekly_campaign_creation', {'theme': theme}, 'success')
                return {'success': True, 'campaign': result, 'generated_at': datetime.now().isoformat()}
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
