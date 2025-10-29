"""
Content & SEO Agent
Handles keyword research, blog writing, content calendar, and SEO optimization
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class ContentSEOAgent(BaseAgent):
    """AI Agent for content creation and SEO optimization"""
    
    def __init__(self):
        super().__init__(
            agent_name="Content & SEO Agent",
            agent_type="content_seo",
            description="Keyword research, blog writing, content calendar, and SEO optimization"
        )
    
    def _define_personality(self) -> str:
        return """
        You are the Content & SEO Agent, an expert in content marketing, SEO strategy, and 
        organic traffic generation. You understand search engine algorithms, keyword strategy, 
        content optimization, and user intent. You create high-quality, SEO-optimized content 
        that ranks well and engages readers. You are data-driven, creative, and focused on 
        driving organic growth through strategic content.
        """
    
    def execute(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute content/SEO task"""
        task_type = task_data.get('task_type')
        
        if task_type == 'keyword_research':
            return self.research_keywords(task_data)
        elif task_type == 'blog_post':
            return self.write_blog_post(task_data)
        elif task_type == 'content_calendar':
            return self.generate_content_calendar(task_data)
        elif task_type == 'seo_optimization':
            return self.optimize_for_seo(task_data)
        elif task_type == 'content_repurpose':
            return self.repurpose_content(task_data)
        else:
            return {'success': False, 'error': f'Unknown task type: {task_type}'}
    
    def research_keywords(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct keyword research and clustering"""
        try:
            topic = params.get('topic', '')
            industry = params.get('industry', '')
            intent_type = params.get('intent', 'mixed')  # informational, commercial, transactional
            
            prompt = f"""
            Conduct comprehensive keyword research for: {topic} in the {industry} industry.
            
            Focus on {intent_type} search intent.
            
            Provide:
            1. Primary Keywords (high volume, medium competition)
            2. Long-tail Keywords (lower volume, lower competition)
            3. Question-based Keywords (for featured snippets)
            4. Keyword Clusters (topic groups)
            5. Search Intent Analysis
            6. Content Gap Opportunities
            7. Competitor Keyword Gaps
            8. Seasonal Trends
            9. Content Recommendations
            
            Respond in JSON format with:
            {{
                "primary_keywords": [
                    {{
                        "keyword": "keyword phrase",
                        "estimated_volume": "monthly searches",
                        "competition": "low/medium/high",
                        "intent": "informational/commercial/transactional",
                        "content_opportunity": "why it's valuable"
                    }}
                ],
                "long_tail_keywords": ["keyword phrases"],
                "question_keywords": ["question-based searches"],
                "keyword_clusters": [
                    {{
                        "cluster_name": "topic group",
                        "primary_keyword": "main keyword",
                        "supporting_keywords": ["related keywords"],
                        "content_format": "blog/guide/comparison"
                    }}
                ],
                "content_gaps": ["opportunities to create unique content"],
                "seasonal_opportunities": ["time-based content ideas"],
                "recommendations": ["strategic content recommendations"],
                "priority_actions": ["what to create first"]
            }}
            """
            
            result = self.generate_with_ai(
                prompt=prompt,
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            if result:
                self.log_activity(
                    activity_type='keyword_research',
                    details={'topic': topic, 'industry': industry},
                    status='success'
                )
                
                return {
                    'success': True,
                    'keyword_data': result,
                    'topic': topic,
                    'generated_at': datetime.now().isoformat()
                }
            else:
                return {'success': False, 'error': 'Failed to generate keyword research'}
                
        except Exception as e:
            logger.error(f"Keyword research error: {e}")
            return {'success': False, 'error': str(e)}
    
    def write_blog_post(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Write SEO-optimized blog post"""
        try:
            topic = params.get('topic', '')
            target_keyword = params.get('target_keyword', '')
            word_count = params.get('word_count', 1500)
            tone = params.get('tone', 'professional')
            audience = params.get('audience', 'general')
            
            prompt = f"""
            Write a comprehensive, SEO-optimized blog post on: {topic}
            
            Target Keyword: {target_keyword}
            Word Count: {word_count} words
            Tone: {tone}
            Target Audience: {audience}
            
            Create a complete blog post with:
            1. Compelling headline (include target keyword)
            2. Meta description (155-160 characters)
            3. Introduction (hook + value proposition)
            4. Well-structured body content with H2/H3 headings
            5. Data, examples, and actionable insights
            6. Internal linking suggestions
            7. Strong conclusion with CTA
            8. Related keywords naturally integrated
            9. Image suggestions with alt text
            
            SEO Requirements:
            - Target keyword in first 100 words
            - Natural keyword density (1-2%)
            - Use of semantic keywords
            - Structured with headers (H2, H3)
            - Scannable with bullet points and short paragraphs
            - E-E-A-T principles (Expertise, Experience, Authority, Trust)
            
            Respond in JSON format with:
            {{
                "headline": "SEO-optimized headline",
                "meta_description": "155-160 character meta description",
                "slug": "url-friendly-slug",
                "introduction": "engaging intro paragraph",
                "body_sections": [
                    {{
                        "heading": "H2 heading",
                        "content": "section content",
                        "subheadings": [
                            {{
                                "heading": "H3 heading",
                                "content": "subsection content"
                            }}
                        ]
                    }}
                ],
                "conclusion": "conclusion with CTA",
                "seo_keywords": ["list of keywords used"],
                "internal_links": ["suggested internal link topics"],
                "external_links": ["suggested authoritative sources"],
                "images": [
                    {{
                        "placement": "where in article",
                        "description": "what to show",
                        "alt_text": "SEO alt text"
                    }}
                ],
                "estimated_word_count": "total words",
                "readability_score": "8th grade level target",
                "key_takeaways": ["main points covered"]
            }}
            """
            
            result = self.generate_with_ai(
                prompt=prompt,
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            if result:
                self.log_activity(
                    activity_type='blog_post_creation',
                    details={'topic': topic, 'keyword': target_keyword},
                    status='success'
                )
                
                return {
                    'success': True,
                    'blog_post': result,
                    'topic': topic,
                    'generated_at': datetime.now().isoformat()
                }
            else:
                return {'success': False, 'error': 'Failed to generate blog post'}
                
        except Exception as e:
            logger.error(f"Blog post creation error: {e}")
            return {'success': False, 'error': str(e)}
    
    def generate_content_calendar(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Generate monthly content calendar"""
        try:
            month = params.get('month', datetime.now().strftime('%B %Y'))
            content_themes = params.get('themes', [])
            frequency = params.get('frequency', 'weekly')  # weekly, biweekly, daily
            
            prompt = f"""
            Create a comprehensive content calendar for {month}.
            
            Content Themes: {', '.join(content_themes) if content_themes else 'Industry insights, how-to guides, trends'}
            Publishing Frequency: {frequency}
            
            Create a strategic content calendar including:
            1. Blog post topics and titles
            2. Publishing dates
            3. Target keywords
            4. Content type/format
            5. Target audience segment
            6. Promotion strategy
            7. Social media snippets
            8. Email newsletter tie-ins
            9. Performance goals
            
            Respond in JSON format with:
            {{
                "month_overview": "strategic focus for the month",
                "content_schedule": [
                    {{
                        "publish_date": "YYYY-MM-DD",
                        "content_title": "blog post title",
                        "content_type": "how-to/listicle/guide/case-study",
                        "target_keyword": "primary keyword",
                        "audience_segment": "who it's for",
                        "description": "what it covers",
                        "word_count": "estimated length",
                        "promotion_channels": ["email", "social", "paid"],
                        "social_snippets": {{
                            "linkedin": "LinkedIn post text",
                            "twitter": "Twitter post text",
                            "facebook": "Facebook post text"
                        }},
                        "expected_impact": "traffic/engagement goal"
                    }}
                ],
                "content_themes": ["overarching themes"],
                "special_dates": [
                    {{
                        "date": "relevant date",
                        "event": "holiday/event",
                        "content_opportunity": "how to leverage"
                    }}
                ],
                "repurposing_opportunities": ["how to reuse content"],
                "cross_channel_strategy": "how content works across channels",
                "success_metrics": ["what to track"],
                "optimization_notes": ["tips for success"]
            }}
            """
            
            result = self.generate_with_ai(
                prompt=prompt,
                response_format={"type": "json_object"},
                temperature=0.6
            )
            
            if result:
                self.log_activity(
                    activity_type='content_calendar',
                    details={'month': month, 'frequency': frequency},
                    status='success'
                )
                
                return {
                    'success': True,
                    'calendar_data': result,
                    'month': month,
                    'generated_at': datetime.now().isoformat()
                }
            else:
                return {'success': False, 'error': 'Failed to generate content calendar'}
                
        except Exception as e:
            logger.error(f"Content calendar error: {e}")
            return {'success': False, 'error': str(e)}
    
    def optimize_for_seo(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze and optimize content for SEO"""
        try:
            content_url = params.get('url', '')
            content_text = params.get('content', '')
            target_keyword = params.get('target_keyword', '')
            
            prompt = f"""
            Perform comprehensive SEO analysis and optimization for this content.
            
            Target Keyword: {target_keyword}
            Content URL: {content_url}
            Content Sample: {content_text[:1000]}...
            
            Analyze and provide recommendations for:
            1. On-Page SEO Elements
            2. Keyword Optimization
            3. Content Structure and Readability
            4. Meta Tags (Title, Description)
            5. Header Tags (H1, H2, H3)
            6. Internal Linking
            7. Image Optimization
            8. Mobile Friendliness
            9. Page Speed Considerations
            10. Schema Markup Opportunities
            
            Respond in JSON format with:
            {{
                "seo_score": "score out of 100",
                "optimization_priority": [
                    {{
                        "issue": "what needs fixing",
                        "severity": "critical/high/medium/low",
                        "recommendation": "how to fix",
                        "impact": "expected improvement"
                    }}
                ],
                "keyword_analysis": {{
                    "primary_keyword_usage": "count and placement",
                    "keyword_density": "percentage",
                    "semantic_keywords": ["related terms to add"],
                    "keyword_opportunities": ["where to add keywords"]
                }},
                "technical_seo": {{
                    "title_tag": {{
                        "current": "existing title",
                        "recommended": "optimized title",
                        "character_count": "length"
                    }},
                    "meta_description": {{
                        "current": "existing description",
                        "recommended": "optimized description",
                        "character_count": "length"
                    }},
                    "header_structure": "analysis of H1-H3 tags",
                    "url_structure": "URL optimization notes"
                }},
                "content_recommendations": [
                    "specific content improvements"
                ],
                "internal_linking": ["suggested internal links"],
                "external_linking": ["authoritative sources to link"],
                "image_optimization": [
                    {{
                        "image": "which image",
                        "alt_text": "recommended alt text",
                        "file_name": "SEO-friendly filename"
                    }}
                ],
                "schema_markup": "recommended structured data",
                "quick_wins": ["easy improvements with high impact"],
                "long_term_optimizations": ["strategic improvements"]
            }}
            """
            
            result = self.generate_with_ai(
                prompt=prompt,
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            if result:
                self.log_activity(
                    activity_type='seo_optimization',
                    details={'url': content_url, 'keyword': target_keyword},
                    status='success'
                )
                
                return {
                    'success': True,
                    'seo_analysis': result,
                    'url': content_url,
                    'generated_at': datetime.now().isoformat()
                }
            else:
                return {'success': False, 'error': 'Failed to generate SEO analysis'}
                
        except Exception as e:
            logger.error(f"SEO optimization error: {e}")
            return {'success': False, 'error': str(e)}
    
    def repurpose_content(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Repurpose blog content for other channels"""
        try:
            original_content = params.get('content', '')
            target_formats = params.get('formats', ['social', 'email', 'video'])
            
            prompt = f"""
            Repurpose this blog content for multiple marketing channels.
            
            Original Content: {original_content[:1500]}
            
            Target Formats: {', '.join(target_formats)}
            
            Create adapted versions for:
            1. Social Media Posts (LinkedIn, Twitter, Facebook, Instagram)
            2. Email Newsletter Snippet
            3. Video Script/Talking Points
            4. Infographic Content Points
            5. Slide Deck Outline
            6. Thread/Twitter Thread
            
            Respond in JSON format with:
            {{
                "social_media": {{
                    "linkedin": {{
                        "post": "LinkedIn post text",
                        "hashtags": ["relevant hashtags"]
                    }},
                    "twitter": {{
                        "thread": ["tweet 1", "tweet 2", "tweet 3"],
                        "hashtags": ["hashtags"]
                    }},
                    "facebook": {{
                        "post": "Facebook post text"
                    }},
                    "instagram": {{
                        "caption": "Instagram caption",
                        "hashtags": ["hashtags"],
                        "carousel_slides": ["slide 1 text", "slide 2 text"]
                    }}
                }},
                "email_newsletter": {{
                    "subject_line": "email subject",
                    "preview_text": "preview text",
                    "body_snippet": "newsletter content",
                    "cta": "call to action"
                }},
                "video_script": {{
                    "hook": "opening hook (first 5 seconds)",
                    "talking_points": ["key points to cover"],
                    "script": "full video script",
                    "duration": "estimated length",
                    "cta": "video call to action"
                }},
                "infographic_outline": {{
                    "title": "infographic title",
                    "data_points": ["key statistics"],
                    "sections": ["section titles"],
                    "visual_suggestions": ["what to visualize"]
                }},
                "slide_deck": {{
                    "title_slide": "presentation title",
                    "slides": [
                        {{
                            "title": "slide title",
                            "content": "bullet points",
                            "visual": "image suggestion"
                        }}
                    ]
                }},
                "repurposing_strategy": "how to use these across time",
                "engagement_tips": ["tips for maximum reach"]
            }}
            """
            
            result = self.generate_with_ai(
                prompt=prompt,
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            if result:
                self.log_activity(
                    activity_type='content_repurposing',
                    details={'formats': target_formats},
                    status='success'
                )
                
                return {
                    'success': True,
                    'repurposed_content': result,
                    'formats': target_formats,
                    'generated_at': datetime.now().isoformat()
                }
            else:
                return {'success': False, 'error': 'Failed to repurpose content'}
                
        except Exception as e:
            logger.error(f"Content repurposing error: {e}")
            return {'success': False, 'error': str(e)}
