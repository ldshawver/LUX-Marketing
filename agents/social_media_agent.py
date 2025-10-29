"""
Social Media & Community Agent
Handles social posting, engagement, and community management
"""
import logging
from datetime import datetime
from typing import Dict, Any
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class SocialMediaAgent(BaseAgent):
    """AI Agent for social media and community management"""
    
    def __init__(self):
        super().__init__(
            agent_name="Social Media & Community Agent",
            agent_type="social_media",
            description="Social posting, engagement tracking, and community management"
        )
    
    def _define_personality(self) -> str:
        return """
        You are the Social Media & Community Agent, an expert in social media strategy,
        community engagement, and brand building. You create engaging content and foster
        authentic connections with audiences across platforms.
        """
    
    def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute social media task"""
        task_type = task_data.get('task_type', 'daily_posts')
        
        if task_type == 'daily_posts':
            return self.generate_daily_posts(task_data)
        elif task_type == 'engagement_report':
            return self.create_engagement_report(task_data)
        else:
            return {'success': False, 'error': f'Unknown task type: {task_type}'}
    
    def generate_daily_posts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate daily social media posts"""
        try:
            platforms = params.get('platforms', ['LinkedIn', 'Twitter', 'Facebook'])
            theme = params.get('theme', 'industry insights')
            
            prompt = f"Create engaging social media posts for {', '.join(platforms)} about {theme}. Include captions and hashtags."
            
            result = self.generate_with_ai(prompt, response_format={"type": "json_object"}, temperature=0.7)
            
            if result:
                self.log_activity('daily_posts_generation', {'platforms': platforms}, 'success')
                return {'success': True, 'posts': result, 'generated_at': datetime.now().isoformat()}
            return {'success': False, 'error': 'Failed to generate posts'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_engagement_report(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create engagement analytics report"""
        try:
            from models import SocialPost
            
            recent_posts = SocialPost.query.order_by(SocialPost.scheduled_at.desc()).limit(20).all()
            
            post_data = [{
                'platform': p.platform,
                'content': p.content[:100],
                'scheduled': p.scheduled_at.isoformat() if p.scheduled_at else None
            } for p in recent_posts]
            
            prompt = f"Analyze these social posts and provide engagement insights: {post_data}"
            
            result = self.generate_with_ai(prompt, response_format={"type": "json_object"}, temperature=0.3)
            
            if result:
                return {'success': True, 'report': result, 'generated_at': datetime.now().isoformat()}
            return {'success': False, 'error': 'Failed to create report'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
