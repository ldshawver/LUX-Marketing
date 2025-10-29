"""
Creative & Design Agent
Handles image generation, ad creatives, and visual content using DALL-E
"""
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class CreativeAgent(BaseAgent):
    """AI Agent for creative and design work"""
    
    def __init__(self):
        super().__init__(
            agent_name="Creative & Design Agent",
            agent_type="creative_design",
            description="Generate product visuals, ads, banners, and creative assets"
        )
    
    def _define_personality(self) -> str:
        return """
        You are the Creative & Design Agent, an expert in visual design, branding, and 
        creative content. You understand design principles, color theory, composition, and 
        visual storytelling. You create compelling visuals that capture attention and drive 
        engagement. You balance creativity with marketing effectiveness.
        """
    
    def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute creative task"""
        task_type = task_data.get('task_type')
        
        if task_type == 'generate_ad_creative':
            return self.generate_ad_creative(task_data)
        elif task_type == 'product_visual':
            return self.generate_product_visual(task_data)
        elif task_type == 'social_media_graphic':
            return self.generate_social_graphic(task_data)
        elif task_type == 'brand_asset':
            return self.generate_brand_asset(task_data)
        else:
            return {'success': False, 'error': f'Unknown task type: {task_type}'}
    
    def generate_ad_creative(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate advertising creative with image and copy"""
        try:
            product_name = params.get('product_name', '')
            ad_objective = params.get('objective', 'awareness')
            platform = params.get('platform', 'facebook')
            target_audience = params.get('audience', 'general')
            
            # Generate copy first
            copy_prompt = f"""
            Create compelling advertising copy for {product_name}.
            
            Platform: {platform}
            Objective: {ad_objective}
            Target Audience: {target_audience}
            
            Provide:
            1. Headline (attention-grabbing)
            2. Body Copy (benefit-focused)
            3. Call-to-Action (action-oriented)
            4. Visual Description (for image generation)
            
            Respond in JSON format with:
            {{
                "headline": "powerful headline",
                "body_copy": "compelling body text",
                "cta": "clear call-to-action",
                "visual_description": "detailed description for image generation",
                "hashtags": ["relevant hashtags"]
            }}
            """
            
            copy_result = self.generate_with_ai(
                prompt=copy_prompt,
                response_format={"type": "json_object"},
                temperature=0.8
            )
            
            if not copy_result:
                return {'success': False, 'error': 'Failed to generate ad copy'}
            
            # Generate visual
            visual_desc = copy_result.get('visual_description', f'Professional advertisement for {product_name}')
            image_result = self.generate_image(visual_desc, style='professional advertising')
            
            if not image_result:
                return {'success': False, 'error': 'Failed to generate image'}
            
            self.log_activity(
                activity_type='ad_creative_generation',
                details={'product': product_name, 'platform': platform},
                status='success'
            )
            
            return {
                'success': True,
                'ad_creative': {
                    **copy_result,
                    'image_url': image_result['image_url'],
                    'platform': platform,
                    'objective': ad_objective
                },
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Ad creative generation error: {e}")
            return {'success': False, 'error': str(e)}
    
    def generate_product_visual(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate product visualization"""
        try:
            product_name = params.get('product_name', '')
            product_description = params.get('description', '')
            visual_style = params.get('style', 'professional product photography')
            
            description = f"{product_name}: {product_description}"
            
            image_result = self.generate_image(description, style=visual_style)
            
            if image_result:
                self.log_activity(
                    activity_type='product_visual_generation',
                    details={'product': product_name},
                    status='success'
                )
                
                return {
                    'success': True,
                    'product_visual': image_result,
                    'product_name': product_name,
                    'generated_at': datetime.now().isoformat()
                }
            else:
                return {'success': False, 'error': 'Failed to generate product visual'}
                
        except Exception as e:
            logger.error(f"Product visual error: {e}")
            return {'success': False, 'error': str(e)}
    
    def generate_social_graphic(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate social media graphic"""
        try:
            message = params.get('message', '')
            platform = params.get('platform', 'instagram')
            theme = params.get('theme', 'modern')
            
            description = f"Social media graphic for {platform}: {message}"
            style = f"{theme} social media design"
            
            image_result = self.generate_image(description, style=style)
            
            if image_result:
                self.log_activity(
                    activity_type='social_graphic_generation',
                    details={'platform': platform},
                    status='success'
                )
                
                return {
                    'success': True,
                    'social_graphic': image_result,
                    'platform': platform,
                    'generated_at': datetime.now().isoformat()
                }
            else:
                return {'success': False, 'error': 'Failed to generate social graphic'}
                
        except Exception as e:
            logger.error(f"Social graphic error: {e}")
            return {'success': False, 'error': str(e)}
    
    def generate_brand_asset(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate branded visual asset"""
        try:
            asset_type = params.get('asset_type', 'banner')
            brand_name = params.get('brand_name', '')
            message = params.get('message', '')
            
            description = f"{asset_type} for {brand_name}: {message}"
            
            image_result = self.generate_image(description, style='professional branding')
            
            if image_result:
                self.log_activity(
                    activity_type='brand_asset_generation',
                    details={'asset_type': asset_type, 'brand': brand_name},
                    status='success'
                )
                
                return {
                    'success': True,
                    'brand_asset': image_result,
                    'asset_type': asset_type,
                    'generated_at': datetime.now().isoformat()
                }
            else:
                return {'success': False, 'error': 'Failed to generate brand asset'}
                
        except Exception as e:
            logger.error(f"Brand asset error: {e}")
            return {'success': False, 'error': str(e)}
