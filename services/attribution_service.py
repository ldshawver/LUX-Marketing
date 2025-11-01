"""
Attribution Service - Multi-Touch Attribution Calculations
Implements 4 attribution models: First Touch, Last Touch, Linear, Time Decay
"""

from datetime import datetime, timedelta
from sqlalchemy import func
from models import db, AttributionTouch, ConversionEvent, Contact, Campaign
import math


class AttributionService:
    """Service for calculating multi-touch attribution"""
    
    @staticmethod
    def calculate_attribution(contact_id, conversion_value, model='last_touch'):
        """
        Calculate attribution for a conversion based on the selected model.
        
        Args:
            contact_id: ID of the contact who converted
            conversion_value: Revenue/value of the conversion
            model: Attribution model ('first_touch', 'last_touch', 'linear', 'time_decay')
        
        Returns:
            dict: Attribution credit per touchpoint
        """
        # Get all touchpoints for this contact leading up to conversion
        touches = AttributionTouch.query.filter_by(
            contact_id=contact_id
        ).order_by(AttributionTouch.occurred_at.asc()).all()
        
        if not touches:
            return {}
        
        # Calculate attribution based on model
        if model == 'first_touch':
            return AttributionService._first_touch_attribution(touches, conversion_value)
        elif model == 'last_touch':
            return AttributionService._last_touch_attribution(touches, conversion_value)
        elif model == 'linear':
            return AttributionService._linear_attribution(touches, conversion_value)
        elif model == 'time_decay':
            return AttributionService._time_decay_attribution(touches, conversion_value)
        else:
            # Default to last touch
            return AttributionService._last_touch_attribution(touches, conversion_value)
    
    @staticmethod
    def _first_touch_attribution(touches, value):
        """100% credit to first touchpoint"""
        if not touches:
            return {}
        
        first_touch = touches[0]
        return {
            first_touch.id: {
                'credit': value,
                'percentage': 100,
                'touchpoint_type': first_touch.touchpoint_type,
                'utm_source': first_touch.utm_source,
                'utm_medium': first_touch.utm_medium,
                'utm_campaign': first_touch.utm_campaign
            }
        }
    
    @staticmethod
    def _last_touch_attribution(touches, value):
        """100% credit to last touchpoint"""
        if not touches:
            return {}
        
        last_touch = touches[-1]
        return {
            last_touch.id: {
                'credit': value,
                'percentage': 100,
                'touchpoint_type': last_touch.touchpoint_type,
                'utm_source': last_touch.utm_source,
                'utm_medium': last_touch.utm_medium,
                'utm_campaign': last_touch.utm_campaign
            }
        }
    
    @staticmethod
    def _linear_attribution(touches, value):
        """Equal credit distributed across all touchpoints"""
        if not touches:
            return {}
        
        num_touches = len(touches)
        credit_per_touch = value / num_touches
        percentage = 100 / num_touches
        
        attribution = {}
        for touch in touches:
            attribution[touch.id] = {
                'credit': credit_per_touch,
                'percentage': percentage,
                'touchpoint_type': touch.touchpoint_type,
                'utm_source': touch.utm_source,
                'utm_medium': touch.utm_medium,
                'utm_campaign': touch.utm_campaign
            }
        
        return attribution
    
    @staticmethod
    def _time_decay_attribution(touches, value, half_life_days=7):
        """
        More recent touchpoints get more credit with exponential decay.
        Default half-life is 7 days.
        """
        if not touches:
            return {}
        
        # Calculate weights based on time decay
        conversion_time = touches[-1].occurred_at
        weights = []
        
        for touch in touches:
            days_before_conversion = (conversion_time - touch.occurred_at).days
            # Exponential decay formula: weight = 2^(-days/half_life)
            weight = math.pow(2, -days_before_conversion / half_life_days)
            weights.append(weight)
        
        total_weight = sum(weights)
        
        # Distribute value based on weights
        attribution = {}
        for i, touch in enumerate(touches):
            credit = (weights[i] / total_weight) * value
            percentage = (weights[i] / total_weight) * 100
            
            attribution[touch.id] = {
                'credit': credit,
                'percentage': percentage,
                'touchpoint_type': touch.touchpoint_type,
                'utm_source': touch.utm_source,
                'utm_medium': touch.utm_medium,
                'utm_campaign': touch.utm_campaign
            }
        
        return attribution
    
    @staticmethod
    def _position_based_attribution(touches, value, first_weight=0.4, last_weight=0.4):
        """
        U-shaped attribution: 40% to first, 40% to last, 20% distributed among middle.
        """
        if not touches:
            return {}
        
        if len(touches) == 1:
            # Only one touch gets 100%
            return AttributionService._first_touch_attribution(touches, value)
        
        attribution = {}
        
        if len(touches) == 2:
            # Two touches: split 50/50 (or use first/last weights)
            attribution[touches[0].id] = {
                'credit': value * 0.5,
                'percentage': 50,
                'touchpoint_type': touches[0].touchpoint_type,
                'utm_source': touches[0].utm_source,
                'utm_medium': touches[0].utm_medium,
                'utm_campaign': touches[0].utm_campaign
            }
            attribution[touches[-1].id] = {
                'credit': value * 0.5,
                'percentage': 50,
                'touchpoint_type': touches[-1].touchpoint_type,
                'utm_source': touches[-1].utm_source,
                'utm_medium': touches[-1].utm_medium,
                'utm_campaign': touches[-1].utm_campaign
            }
        else:
            # More than 2 touches
            middle_credit = value * (1 - first_weight - last_weight)
            middle_touches = len(touches) - 2
            credit_per_middle = middle_credit / middle_touches if middle_touches > 0 else 0
            
            # First touch
            attribution[touches[0].id] = {
                'credit': value * first_weight,
                'percentage': first_weight * 100,
                'touchpoint_type': touches[0].touchpoint_type,
                'utm_source': touches[0].utm_source,
                'utm_medium': touches[0].utm_medium,
                'utm_campaign': touches[0].utm_campaign
            }
            
            # Middle touches
            for touch in touches[1:-1]:
                attribution[touch.id] = {
                    'credit': credit_per_middle,
                    'percentage': (credit_per_middle / value) * 100,
                    'touchpoint_type': touch.touchpoint_type,
                    'utm_source': touch.utm_source,
                    'utm_medium': touch.utm_medium,
                    'utm_campaign': touch.utm_campaign
                }
            
            # Last touch
            attribution[touches[-1].id] = {
                'credit': value * last_weight,
                'percentage': last_weight * 100,
                'touchpoint_type': touches[-1].touchpoint_type,
                'utm_source': touches[-1].utm_source,
                'utm_medium': touches[-1].utm_medium,
                'utm_campaign': touches[-1].utm_campaign
            }
        
        return attribution
    
    @staticmethod
    def get_channel_attribution(model='last_touch', days=30):
        """
        Get attribution by channel for all conversions in the time period.
        
        Args:
            model: Attribution model to use
            days: Number of days to look back
        
        Returns:
            dict: Channel attribution summary
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get all conversions in the period
        conversions = ConversionEvent.query.filter(
            ConversionEvent.occurred_at >= cutoff_date
        ).all()
        
        channel_data = {}
        
        for conversion in conversions:
            # Calculate attribution for this conversion
            attribution = AttributionService.calculate_attribution(
                conversion.contact_id,
                conversion.event_value,
                model
            )
            
            # Aggregate by channel
            for touch_id, data in attribution.items():
                channel = data['touchpoint_type'] or 'direct'
                
                if channel not in channel_data:
                    channel_data[channel] = {
                        'revenue': 0,
                        'conversions': 0,
                        'touches': 0
                    }
                
                channel_data[channel]['revenue'] += data['credit']
                channel_data[channel]['touches'] += 1
        
        # Count conversions per channel
        for conversion in conversions:
            channel = conversion.utm_medium or 'direct'
            if channel in channel_data:
                channel_data[channel]['conversions'] += 1
        
        return channel_data
    
    @staticmethod
    def compare_models(contact_id, conversion_value):
        """
        Compare attribution across all models for a single conversion.
        
        Returns:
            dict: Attribution results for each model
        """
        models = ['first_touch', 'last_touch', 'linear', 'time_decay']
        comparison = {}
        
        for model in models:
            comparison[model] = AttributionService.calculate_attribution(
                contact_id,
                conversion_value,
                model
            )
        
        return comparison
    
    @staticmethod
    def get_customer_journey(contact_id):
        """
        Get the full customer journey for a contact.
        
        Returns:
            list: Ordered list of touchpoints
        """
        touches = AttributionTouch.query.filter_by(
            contact_id=contact_id
        ).order_by(AttributionTouch.occurred_at.asc()).all()
        
        journey = []
        for i, touch in enumerate(touches):
            journey.append({
                'position': i + 1,
                'type': touch.touchpoint_type,
                'source': touch.utm_source,
                'medium': touch.utm_medium,
                'campaign': touch.utm_campaign,
                'timestamp': touch.occurred_at,
                'page_url': touch.page_url,
                'referrer': touch.referrer_url
            })
        
        return journey
    
    @staticmethod
    def get_top_conversion_paths(limit=10, days=30):
        """
        Identify the most common customer journey patterns.
        
        Returns:
            list: Top conversion paths with counts
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get all conversions with their journeys
        conversions = ConversionEvent.query.filter(
            ConversionEvent.occurred_at >= cutoff_date
        ).all()
        
        path_patterns = {}
        
        for conversion in conversions:
            # Get journey for this contact
            touches = AttributionTouch.query.filter_by(
                contact_id=conversion.contact_id
            ).order_by(AttributionTouch.occurred_at.asc()).all()
            
            # Create path signature
            path = ' → '.join([t.touchpoint_type or 'direct' for t in touches])
            
            if path not in path_patterns:
                path_patterns[path] = {
                    'count': 0,
                    'revenue': 0,
                    'steps': [t.touchpoint_type or 'direct' for t in touches],
                    'avg_days': 0
                }
            
            path_patterns[path]['count'] += 1
            path_patterns[path]['revenue'] += conversion.event_value
            
            # Calculate journey length in days
            if touches:
                journey_days = (touches[-1].occurred_at - touches[0].occurred_at).days
                path_patterns[path]['avg_days'] = (
                    (path_patterns[path]['avg_days'] * (path_patterns[path]['count'] - 1) + journey_days)
                    / path_patterns[path]['count']
                )
        
        # Sort by count and return top paths
        top_paths = sorted(
            path_patterns.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:limit]
        
        return [{'path': path, **data} for path, data in top_paths]
