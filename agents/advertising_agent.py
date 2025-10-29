"""
Advertising & Demand Gen Agent
Handles ad targeting, campaign setup, A/B tests, and landing page optimization
"""
import logging
from datetime import datetime
from typing import Dict, Any
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class AdvertisingAgent(BaseAgent):
    """AI Agent for advertising and demand generation"""
    
    def __init__(self):
        super().__init__(
            agent_name="Advertising & Demand Gen Agent",
            agent_type="advertising",
            description="Ad targeting, creative, A/B testing, and campaign optimization"
        )
    
    def _define_personality(self) -> str:
        return """
        You are the Advertising & Demand Gen Agent, an expert in paid advertising, campaign
        management, and conversion optimization. You understand ad platforms, targeting strategies,
        and performance marketing. You create high-converting ad campaigns and optimize for ROI.
        """
    
    def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute advertising task"""
        task_type = task_data.get('task_type', 'campaign_strategy')
        
        if task_type == 'campaign_strategy':
            return self.create_campaign_strategy(task_data)
        elif task_type == 'ad_copy':
            return self.generate_ad_copy(task_data)
        elif task_type == 'targeting':
            return self.define_targeting(task_data)
        else:
            return {'success': False, 'error': f'Unknown task type: {task_type}'}
    
    def create_campaign_strategy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create advertising campaign strategy"""
        try:
            objective = params.get('objective', 'conversions')
            budget = params.get('budget', 1000)
            
            prompt = f"""
            Create a comprehensive paid advertising campaign strategy.
            Objective: {objective}
            Budget: ${budget}
            
            Provide campaign plan with targeting, channels, budget allocation, and KPIs.
            
            Respond in JSON format with detailed strategy.
            """
            
            result = self.generate_with_ai(prompt, response_format={"type": "json_object"}, temperature=0.4)
            
            if result:
                self.log_activity('campaign_strategy_generation', {'objective': objective}, 'success')
                return {'success': True, 'strategy': result, 'generated_at': datetime.now().isoformat()}
            return {'success': False, 'error': 'Failed to generate strategy'}
            
        except Exception as e:
            logger.error(f"Campaign strategy error: {e}")
            return {'success': False, 'error': str(e)}
    
    def generate_ad_copy(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate advertising copy variations"""
        try:
            product = params.get('product', '')
            platform = params.get('platform', 'Facebook')
            
            prompt = f"Create 5 high-converting ad copy variations for {product} on {platform}. Include headlines, body text, and CTAs."
            
            result = self.generate_with_ai(prompt, temperature=0.8)
            
            if result:
                return {'success': True, 'ad_copy': result, 'generated_at': datetime.now().isoformat()}
            return {'success': False, 'error': 'Failed to generate ad copy'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def define_targeting(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Define ad targeting strategy"""
        try:
            audience = params.get('audience', 'professionals')
            
            prompt = f"Define detailed ad targeting strategy for {audience}. Include demographics, interests, behaviors, and lookalike audiences."
            
            result = self.generate_with_ai(prompt, response_format={"type": "json_object"}, temperature=0.3)
            
            if result:
                return {'success': True, 'targeting': result, 'generated_at': datetime.now().isoformat()}
            return {'success': False, 'error': 'Failed to define targeting'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
