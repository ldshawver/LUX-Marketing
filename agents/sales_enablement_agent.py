"""
Sales Enablement Agent
Handles sales materials, proposals, and lead management
"""
import logging
from datetime import datetime
from typing import Dict, Any
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class SalesEnablementAgent(BaseAgent):
    """AI Agent for sales enablement"""
    
    def __init__(self):
        super().__init__(
            agent_name="Sales Enablement Agent",
            agent_type="sales_enablement",
            description="Sales decks, proposals, and MQL management"
        )
    
    def _define_personality(self) -> str:
        return """
        You are the Sales Enablement Agent, an expert in sales materials, proposal writing,
        and lead qualification. You create persuasive sales content that converts.
        """
    
    def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute sales enablement task"""
        task_type = task_data.get('task_type', 'sales_deck')
        
        if task_type == 'sales_deck':
            return self.create_sales_deck(task_data)
        elif task_type == 'proposal':
            return self.generate_proposal(task_data)
        elif task_type == 'lead_scoring':
            return self.score_leads(task_data)
        else:
            return {'success': False, 'error': f'Unknown task type: {task_type}'}
    
    def create_sales_deck(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create sales presentation deck"""
        try:
            product = params.get('product', 'solution')
            
            prompt = f"Create a compelling sales deck outline for {product}. Include slide titles, key points, and visual suggestions."
            
            result = self.generate_with_ai(prompt, response_format={"type": "json_object"}, temperature=0.6)
            
            if result:
                self.log_activity('sales_deck_creation', {'product': product}, 'success')
                return {'success': True, 'deck': result, 'generated_at': datetime.now().isoformat()}
            return {'success': False, 'error': 'Failed to create deck'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_proposal(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sales proposal"""
        try:
            client = params.get('client', 'prospect')
            
            prompt = f"Create a professional sales proposal for {client}. Include executive summary, solution overview, pricing, and next steps."
            
            result = self.generate_with_ai(prompt, response_format={"type": "json_object"}, temperature=0.5)
            
            if result:
                return {'success': True, 'proposal': result, 'generated_at': datetime.now().isoformat()}
            return {'success': False, 'error': 'Failed to generate proposal'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def score_leads(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Score and prioritize leads"""
        try:
            from models import Contact
            
            contacts = Contact.query.filter_by(is_active=True).limit(50).all()
            lead_data = [{'email': c.email, 'engagement': c.engagement_score, 'company': c.company} for c in contacts]
            
            prompt = f"Score and prioritize these leads for sales outreach: {lead_data}"
            
            result = self.generate_with_ai(prompt, response_format={"type": "json_object"}, temperature=0.2)
            
            if result:
                return {'success': True, 'scoring': result, 'generated_at': datetime.now().isoformat()}
            return {'success': False, 'error': 'Failed to score leads'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
