"""
Customer Retention & Loyalty Agent
Handles retention campaigns, churn prevention, and loyalty programs
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class RetentionAgent(BaseAgent):
    """AI Agent for customer retention and loyalty"""
    
    def __init__(self):
        super().__init__(
            agent_name="Customer Retention & Loyalty Agent",
            agent_type="retention",
            description="Retention campaigns, churn detection, and loyalty management"
        )
    
    def _define_personality(self) -> str:
        return """
        You are the Customer Retention & Loyalty Agent, an expert in customer success,
        churn prevention, and loyalty program design. You keep customers engaged and satisfied.
        """
    
    def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute retention task"""
        task_type = task_data.get('task_type', 'churn_analysis')
        
        if task_type == 'churn_analysis':
            return self.analyze_churn_risk(task_data)
        elif task_type == 'winback_campaign':
            return self.create_winback_campaign(task_data)
        elif task_type == 'loyalty_program':
            return self.design_loyalty_program(task_data)
        else:
            return {'success': False, 'error': f'Unknown task type: {task_type}'}
    
    def analyze_churn_risk(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze customer churn risk"""
        try:
            from models import Contact
            
            inactive_threshold = datetime.now() - timedelta(days=90)
            inactive_contacts = Contact.query.filter(
                Contact.is_active == True,
                Contact.last_activity < inactive_threshold
            ).limit(50).all()
            
            contact_data = [{'email': c.email, 'last_activity': c.last_activity.isoformat() if c.last_activity else None} for c in inactive_contacts]
            
            prompt = f"Analyze churn risk for these inactive contacts and recommend retention strategies: {contact_data}"
            
            result = self.generate_with_ai(prompt, response_format={"type": "json_object"}, temperature=0.3)
            
            if result:
                self.log_activity('churn_analysis', {'at_risk_count': len(inactive_contacts)}, 'success')
                return {'success': True, 'analysis': result, 'at_risk_count': len(inactive_contacts), 'generated_at': datetime.now().isoformat()}
            return {'success': False, 'error': 'Failed to analyze churn'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_winback_campaign(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create win-back campaign"""
        try:
            segment = params.get('segment', 'inactive users')
            
            prompt = f"Create a compelling win-back email campaign for {segment}. Include subject lines, offers, and messaging strategy."
            
            result = self.generate_with_ai(prompt, response_format={"type": "json_object"}, temperature=0.7)
            
            if result:
                return {'success': True, 'campaign': result, 'generated_at': datetime.now().isoformat()}
            return {'success': False, 'error': 'Failed to create campaign'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def design_loyalty_program(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Design customer loyalty program"""
        try:
            business_type = params.get('business_type', 'B2B')
            
            prompt = f"Design a customer loyalty program for a {business_type} business. Include tiers, rewards, and engagement mechanics."
            
            result = self.generate_with_ai(prompt, response_format={"type": "json_object"}, temperature=0.6)
            
            if result:
                return {'success': True, 'program': result, 'generated_at': datetime.now().isoformat()}
            return {'success': False, 'error': 'Failed to design program'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
