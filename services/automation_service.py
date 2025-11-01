"""
Automation Service - Phase 5
Handles automation testing, trigger library, and A/B testing
"""

from datetime import datetime
from app import db
from models import (Automation, AutomationTest, AutomationTriggerLibrary, 
                    AutomationABTest, Contact)
import logging

logger = logging.getLogger(__name__)

class AutomationService:
    @staticmethod
    def run_test(automation_id, test_contact_id=None, test_data=None):
        """Run automation in test mode"""
        try:
            automation = Automation.query.get(automation_id)
            if not automation:
                return None
            
            test = AutomationTest(
                automation_id=automation_id,
                test_contact_id=test_contact_id,
                test_data=test_data or {},
                status='running',
                started_at=datetime.utcnow()
            )
            db.session.add(test)
            db.session.commit()
            
            # Simulate test execution
            test_results = []
            for step in automation.steps:
                test_results.append({
                    'step_id': step.id,
                    'step_type': step.step_type,
                    'status': 'success',
                    'message': f'{step.step_type} would be executed'
                })
            
            test.test_results = test_results
            test.status = 'completed'
            test.completed_at = datetime.utcnow()
            db.session.commit()
            
            return test
        except Exception as e:
            logger.error(f"Error running automation test: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def create_trigger_template(name, trigger_type, description, category, trigger_config, steps_template):
        """Create pre-built trigger template"""
        try:
            template = AutomationTriggerLibrary(
                name=name,
                trigger_type=trigger_type,
                description=description,
                category=category,
                trigger_config=trigger_config,
                steps_template=steps_template
            )
            db.session.add(template)
            db.session.commit()
            return template
        except Exception as e:
            logger.error(f"Error creating trigger template: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def get_trigger_library(category=None):
        """Get available trigger templates"""
        try:
            query = AutomationTriggerLibrary.query
            if category:
                query = query.filter_by(category=category)
            return query.order_by(AutomationTriggerLibrary.usage_count.desc()).all()
        except Exception as e:
            logger.error(f"Error getting trigger library: {e}")
            return []
    
    @staticmethod
    def create_ab_test(automation_id, step_id, variant_a_id, variant_b_id, split=50):
        """Create A/B test for automation step"""
        try:
            ab_test = AutomationABTest(
                automation_id=automation_id,
                step_id=step_id,
                variant_a_template_id=variant_a_id,
                variant_b_template_id=variant_b_id,
                split_percentage=split
            )
            db.session.add(ab_test)
            db.session.commit()
            return ab_test
        except Exception as e:
            logger.error(f"Error creating A/B test: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def update_ab_test_results(test_id, variant, sent=0, opens=0, clicks=0):
        """Update A/B test results"""
        try:
            ab_test = AutomationABTest.query.get(test_id)
            if not ab_test:
                return None
            
            if variant == 'A':
                ab_test.variant_a_sent += sent
                ab_test.variant_a_opens += opens
                ab_test.variant_a_clicks += clicks
            else:
                ab_test.variant_b_sent += sent
                ab_test.variant_b_opens += opens
                ab_test.variant_b_clicks += clicks
            
            # Determine winner if enough data
            if ab_test.variant_a_sent >= 100 and ab_test.variant_b_sent >= 100:
                a_rate = (ab_test.variant_a_opens / ab_test.variant_a_sent * 100) if ab_test.variant_a_sent > 0 else 0
                b_rate = (ab_test.variant_b_opens / ab_test.variant_b_sent * 100) if ab_test.variant_b_sent > 0 else 0
                
                ab_test.winner_variant = 'A' if a_rate > b_rate else 'B'
                ab_test.status = 'completed'
                ab_test.completed_at = datetime.utcnow()
            
            db.session.commit()
            return ab_test
        except Exception as e:
            logger.error(f"Error updating A/B test results: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def seed_trigger_library():
        """Seed database with pre-built triggers"""
        templates = [
            {
                'name': 'Welcome Series',
                'trigger_type': 'signup',
                'description': 'Send welcome emails to new subscribers',
                'category': 'engagement',
                'trigger_config': {'event': 'user_signup'},
                'steps_template': [
                    {'type': 'email', 'delay': 0, 'template': 'Welcome Email'},
                    {'type': 'wait', 'delay': 24},
                    {'type': 'email', 'delay': 0, 'template': 'Getting Started'}
                ]
            },
            {
                'name': 'Abandoned Cart',
                'trigger_type': 'abandoned_cart',
                'description': 'Recover abandoned carts with follow-up emails',
                'category': 'ecommerce',
                'trigger_config': {'event': 'cart_abandoned', 'wait_hours': 1},
                'steps_template': [
                    {'type': 'email', 'delay': 1, 'template': 'Cart Reminder'},
                    {'type': 'wait', 'delay': 24},
                    {'type': 'email', 'delay': 0, 'template': 'Special Discount'}
                ]
            },
            {
                'name': 'Re-engagement Campaign',
                'trigger_type': 'inactive',
                'description': 'Win back inactive subscribers',
                'category': 'retention',
                'trigger_config': {'inactive_days': 30},
                'steps_template': [
                    {'type': 'email', 'delay': 0, 'template': 'We Miss You'},
                    {'type': 'wait', 'delay': 72},
                    {'type': 'email', 'delay': 0, 'template': 'Last Chance Offer'}
                ]
            }
        ]
        
        for template in templates:
            existing = AutomationTriggerLibrary.query.filter_by(name=template['name']).first()
            if not existing:
                AutomationService.create_trigger_template(**template)
