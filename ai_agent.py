"""
LUX AI Agent - Automated Email Marketing Assistant
Powered by OpenAI GPT-4o for intelligent email campaign management
"""
import os
import json
import logging
from datetime import datetime, timedelta
from openai import OpenAI
from models import Campaign, Contact, EmailTemplate, CampaignRecipient, db
from email_service import EmailService
from tracking import get_campaign_analytics
import base64
import requests
from urllib.parse import urljoin

logger = logging.getLogger(__name__)

class LUXAgent:
    """LUX - Automated Email Marketing AI Agent"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = "gpt-4o"  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
        self.agent_name = "LUX"
        self.agent_personality = """
        You are LUX, an expert email marketing automation agent. You are professional, data-driven, 
        and focused on creating high-converting email campaigns. You understand marketing psychology, 
        audience segmentation, and email best practices. You always aim to maximize engagement rates 
        and conversions while maintaining brand consistency.
        """
    
    def generate_campaign_content(self, campaign_objective, target_audience, brand_info=None):
        """Generate email campaign content based on objectives and audience"""
        try:
            prompt = f"""
            As LUX, an email marketing expert, create a high-converting email campaign.
            
            Campaign Objective: {campaign_objective}
            Target Audience: {target_audience}
            Brand Information: {brand_info or 'Professional business'}
            
            Generate a complete email campaign with:
            1. Compelling subject line (under 50 characters)
            2. Professional HTML email content
            3. Clear call-to-action
            4. Personalization elements
            
            Respond in JSON format with:
            {
                "subject": "email subject line",
                "html_content": "complete HTML email content",
                "campaign_name": "descriptive campaign name",
                "recommendations": "optimization tips"
            }
            
            Make the content engaging, professional, and conversion-focused.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.agent_personality},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            content = response.choices[0].message.content
            if not content:
                logger.error("LUX received empty response from OpenAI")
                return None
            result = json.loads(content)
            logger.info(f"LUX generated campaign content: {result['campaign_name']}")
            return result
            
        except Exception as e:
            logger.error(f"LUX error generating campaign content: {e}")
            return None
    
    def analyze_audience_segments(self, contacts):
        """Analyze contact data to create audience segments"""
        try:
            # Prepare contact data for analysis
            contact_data = []
            for contact in contacts[:50]:  # Limit for API efficiency
                contact_data.append({
                    'email': contact.email,
                    'company': contact.company or 'Unknown',
                    'tags': contact.tags or '',
                    'created_at': contact.created_at.strftime('%Y-%m-%d') if contact.created_at else ''
                })
            
            prompt = f"""
            As LUX, analyze this contact data and create optimal audience segments for email marketing.
            
            Contact Data: {json.dumps(contact_data[:20])}  # Sample of contacts
            Total Contacts: {len(contacts)}
            
            Create 3-5 audience segments based on:
            - Company types/industries
            - Contact behavior patterns
            - Optimal messaging strategies
            
            Respond in JSON format with:
            {
                "segments": [
                    {
                        "name": "segment name",
                        "description": "who this segment includes",
                        "size_estimate": "percentage of audience",
                        "messaging_strategy": "how to communicate with this segment",
                        "recommended_tags": ["tag1", "tag2"]
                    }
                ],
                "insights": "key findings about the audience"
            }
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.agent_personality},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"LUX analyzed audience and created {len(result['segments'])} segments")
            return result
            
        except Exception as e:
            logger.error(f"LUX error analyzing audience: {e}")
            return None
    
    def optimize_campaign_performance(self, campaign_id):
        """Analyze campaign performance and provide optimization recommendations"""
        try:
            # Get campaign analytics
            analytics = get_campaign_analytics(campaign_id)
            if not analytics:
                return None
            
            campaign_data = {
                'name': analytics['campaign'].name,
                'subject': analytics['campaign'].subject,
                'total_recipients': analytics['total_recipients'],
                'delivery_rate': analytics['delivery_rate'],
                'open_rate': analytics['open_rate'],
                'click_rate': analytics['click_rate'],
                'bounce_rate': analytics['bounce_rate']
            }
            
            prompt = f"""
            As LUX, analyze this email campaign performance and provide optimization recommendations.
            
            Campaign Data: {json.dumps(campaign_data)}
            
            Industry Benchmarks:
            - Average Open Rate: 21.33%
            - Average Click Rate: 2.62%
            - Average Bounce Rate: 0.58%
            
            Provide actionable recommendations to improve performance.
            
            Respond in JSON format with:
            {
                "performance_assessment": "overall performance evaluation",
                "strengths": ["what's working well"],
                "improvements": [
                    {
                        "area": "specific area to improve",
                        "recommendation": "specific action to take",
                        "expected_impact": "predicted improvement"
                    }
                ],
                "next_campaign_suggestions": "ideas for follow-up campaigns"
            }
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.agent_personality},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"LUX analyzed campaign {campaign_id} performance")
            return result
            
        except Exception as e:
            logger.error(f"LUX error optimizing campaign: {e}")
            return None
    
    def create_automated_campaign(self, campaign_brief, template_id=None):
        """Automatically create and schedule a complete email campaign"""
        try:
            # Generate campaign content
            content = self.generate_campaign_content(
                campaign_brief.get('objective', 'Engage audience'),
                campaign_brief.get('target_audience', 'All contacts'),
                campaign_brief.get('brand_info', 'Professional business')
            )
            
            if not content:
                return None
            
            # Create email template if not provided
            if not template_id:
                template = EmailTemplate(
                    name=f"LUX Generated - {content['campaign_name']}",
                    subject=content['subject'],
                    html_content=content['html_content']
                )
                db.session.add(template)
                db.session.flush()
                template_id = template.id
            
            # Create campaign
            campaign = Campaign(
                name=content['campaign_name'],
                subject=content['subject'],
                template_id=template_id,
                status='draft'
            )
            
            # Schedule if requested
            if campaign_brief.get('schedule_time'):
                campaign.scheduled_at = campaign_brief['schedule_time']
                campaign.status = 'scheduled'
            
            db.session.add(campaign)
            db.session.flush()
            
            # Add recipients based on targeting
            contacts_query = Contact.query.filter_by(is_active=True)
            
            # Apply audience filtering if specified
            if campaign_brief.get('target_tags'):
                tags = campaign_brief['target_tags']
                tag_conditions = []
                for tag in tags:
                    tag_conditions.append(Contact.tags.contains(tag))
                if tag_conditions:
                    from sqlalchemy import or_
                    contacts_query = contacts_query.filter(or_(*tag_conditions))
            
            contacts = contacts_query.all()
            
            # Add recipients
            for contact in contacts:
                recipient = CampaignRecipient(
                    campaign_id=campaign.id,
                    contact_id=contact.id
                )
                db.session.add(recipient)
            
            db.session.commit()
            
            result = {
                'campaign_id': campaign.id,
                'campaign_name': campaign.name,
                'recipients_count': len(contacts),
                'recommendations': content.get('recommendations', ''),
                'status': campaign.status
            }
            
            logger.info(f"LUX created automated campaign: {campaign.name} with {len(contacts)} recipients")
            return result
            
        except Exception as e:
            logger.error(f"LUX error creating automated campaign: {e}")
            db.session.rollback()
            return None
    
    def generate_subject_line_variants(self, campaign_objective, original_subject=None):
        """Generate multiple subject line variants for A/B testing"""
        try:
            prompt = f"""
            As LUX, generate 5 high-converting email subject line variants for A/B testing.
            
            Campaign Objective: {campaign_objective}
            Original Subject: {original_subject or 'Not provided'}
            
            Create subject lines that use different psychological triggers:
            - Urgency
            - Curiosity
            - Benefit-focused
            - Personalization
            - Social proof
            
            Respond in JSON format with:
            {
                "variants": [
                    {
                        "subject": "subject line text",
                        "strategy": "psychological trigger used",
                        "predicted_performance": "high/medium/low"
                    }
                ],
                "testing_recommendations": "how to test these effectively"
            }
            
            Keep all subject lines under 50 characters for mobile optimization.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.agent_personality},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.8
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"LUX generated {len(result['variants'])} subject line variants")
            return result
            
        except Exception as e:
            logger.error(f"LUX error generating subject lines: {e}")
            return None
    
    def get_campaign_recommendations(self):
        """Get AI-powered recommendations for new campaigns based on current data"""
        try:
            # Get recent campaign data
            recent_campaigns = Campaign.query.order_by(Campaign.created_at.desc()).limit(5).all()
            total_contacts = Contact.query.filter_by(is_active=True).count()
            
            campaign_data = []
            for campaign in recent_campaigns:
                analytics = get_campaign_analytics(campaign.id)
                if analytics:
                    campaign_data.append({
                        'name': campaign.name,
                        'open_rate': analytics['open_rate'],
                        'click_rate': analytics['click_rate'],
                        'created_at': campaign.created_at.strftime('%Y-%m-%d') if campaign.created_at else ''
                    })
            
            prompt = f"""
            As LUX, analyze the current email marketing situation and recommend new campaign strategies.
            
            Current Data:
            - Total Active Contacts: {total_contacts}
            - Recent Campaigns: {json.dumps(campaign_data)}
            - Current Date: {datetime.now().strftime('%Y-%m-%d')}
            
            Provide strategic recommendations for upcoming campaigns considering:
            - Seasonal opportunities
            - Performance trends
            - Audience engagement patterns
            - Industry best practices
            
            Respond in JSON format with:
            {{
                "recommended_campaigns": [
                    {{
                        "campaign_type": "type of campaign",
                        "objective": "primary goal", 
                        "timing": "when to send",
                        "expected_results": "predicted performance",
                        "priority": "high/medium/low"
                    }}
                ],
                "strategic_insights": "key observations and next steps"
            }}
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.agent_personality},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.4
            )
            
            result = json.loads(response.choices[0].message.content)
            logger.info(f"LUX generated {len(result['recommended_campaigns'])} campaign recommendations")
            return result
            
        except Exception as e:
            logger.error(f"LUX error getting recommendations: {e}")
            return None
    
    def generate_campaign_image(self, campaign_description, style="professional marketing"):
        """Generate marketing images using DALL-E"""
        try:
            prompt = f"""
            Create a professional marketing image for: {campaign_description}
            
            Style: {style}
            Requirements:
            - High-quality, professional marketing design
            - Suitable for email marketing campaigns
            - Clear, engaging visual that supports the campaign message
            - Modern, clean aesthetic
            - Brand-friendly colors and composition
            """
            
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                size="1024x1024",
                quality="standard"
            )
            
            image_url = response.data[0].url
            logger.info(f"LUX generated campaign image: {campaign_description[:50]}...")
            
            return {
                'image_url': image_url,
                'prompt_used': prompt,
                'campaign_description': campaign_description
            }
            
        except Exception as e:
            logger.error(f"LUX error generating image: {e}")
            return None
    
    def fetch_woocommerce_products(self, woocommerce_url, consumer_key, consumer_secret, 
                                  product_limit=10, category_filter=None):
        """Fetch products from WooCommerce API"""
        try:
            # Construct API endpoint
            api_url = urljoin(woocommerce_url, '/wp-json/wc/v3/products')
            
            # Set up authentication and parameters
            auth = (consumer_key, consumer_secret)
            params = {
                'per_page': product_limit,
                'status': 'publish',
                'stock_status': 'instock'
            }
            
            if category_filter:
                params['category'] = category_filter
            
            response = requests.get(api_url, auth=auth, params=params, timeout=10)
            
            if response.status_code == 200:
                products = response.json()
                
                # Process products for email use
                processed_products = []
                for product in products:
                    processed_product = {
                        'id': product.get('id'),
                        'name': product.get('name', ''),
                        'price': product.get('price', '0'),
                        'regular_price': product.get('regular_price', '0'),
                        'sale_price': product.get('sale_price', ''),
                        'description': product.get('short_description', ''),
                        'image_url': product.get('images', [{}])[0].get('src', '') if product.get('images') else '',
                        'permalink': product.get('permalink', ''),
                        'categories': [cat.get('name', '') for cat in product.get('categories', [])],
                        'tags': [tag.get('name', '') for tag in product.get('tags', [])],
                        'in_stock': product.get('stock_status') == 'instock',
                        'featured': product.get('featured', False)
                    }
                    processed_products.append(processed_product)
                
                logger.info(f"LUX fetched {len(processed_products)} WooCommerce products")
                return processed_products
            else:
                logger.error(f"WooCommerce API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"LUX error fetching WooCommerce products: {e}")
            return None
    
    def create_product_campaign(self, woocommerce_config, campaign_objective, 
                               product_filter=None, include_images=True):
        """Create a product-focused email campaign with WooCommerce integration"""
        try:
            # Fetch products from WooCommerce
            products = self.fetch_woocommerce_products(
                woocommerce_config['url'],
                woocommerce_config['consumer_key'],
                woocommerce_config['consumer_secret'],
                product_limit=woocommerce_config.get('product_limit', 6),
                category_filter=product_filter
            )
            
            if not products:
                return None
            
            # Generate campaign image if requested
            campaign_image = None
            if include_images:
                image_description = f"Product showcase for {campaign_objective} featuring {len(products)} products"
                campaign_image = self.generate_campaign_image(image_description, "e-commerce product showcase")
            
            # Create product-focused campaign content
            prompt = f"""
            As LUX, create a high-converting product email campaign.
            
            Campaign Objective: {campaign_objective}
            Products to Feature: {json.dumps(products[:3])}  # Top 3 products for context
            Total Products Available: {len(products)}
            Campaign Image: {'Available' if campaign_image else 'Not generated'}
            
            Create an HTML email that:
            1. Features the products prominently with images and prices
            2. Includes compelling product descriptions
            3. Has clear call-to-action buttons for each product
            4. Uses professional e-commerce email styling
            5. Includes the campaign image if available
            6. Has a compelling subject line focused on the products
            
            Respond in JSON format with:
            {
                "subject": "product-focused subject line",
                "html_content": "complete HTML email with product showcase",
                "campaign_name": "descriptive campaign name",
                "featured_products": ["list of product names featured"],
                "recommendations": "optimization tips for product campaigns"
            }
            
            Make it conversion-focused with clear pricing and purchase buttons.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.agent_personality},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            
            campaign_content = json.loads(response.choices[0].message.content)
            
            # Add product and image data to response
            result = {
                **campaign_content,
                'products': products,
                'campaign_image': campaign_image,
                'product_count': len(products),
                'woocommerce_integration': True
            }
            
            logger.info(f"LUX created product campaign with {len(products)} products")
            return result
            
        except Exception as e:
            logger.error(f"LUX error creating product campaign: {e}")
            return None

# Global LUX agent instance
lux_agent = LUXAgent()