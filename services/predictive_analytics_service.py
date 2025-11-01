"""
Predictive Analytics & AI Insights Service
Lead scoring, churn prediction, send-time optimization, and forecasting
"""

from datetime import datetime, timedelta
from models import db
import logging
import json
import openai
import os

logger = logging.getLogger(__name__)


class PredictiveAnalyticsService:
    """Service for AI-powered predictive analytics"""
    
    @staticmethod
    def calculate_lead_score(contact):
        """
        Calculate predictive lead score using multiple factors.
        
        Args:
            contact: Contact object
        
        Returns:
            dict: Lead score and breakdown
        """
        try:
            score = 0
            breakdown = {}
            
            # Engagement score (0-30 points)
            from models import EmailTracking, CampaignRecipient
            
            email_opens = EmailTracking.query.filter_by(
                contact_id=contact.id,
                event_type='open'
            ).count()
            
            email_clicks = EmailTracking.query.filter_by(
                contact_id=contact.id,
                event_type='click'
            ).count()
            
            engagement_score = min(30, (email_opens * 2) + (email_clicks * 5))
            score += engagement_score
            breakdown['engagement'] = engagement_score
            
            # Recency score (0-25 points)
            last_activity = EmailTracking.query.filter_by(
                contact_id=contact.id
            ).order_by(EmailTracking.created_at.desc()).first()
            
            if last_activity:
                days_since = (datetime.utcnow() - last_activity.created_at).days
                if days_since < 7:
                    recency_score = 25
                elif days_since < 30:
                    recency_score = 15
                elif days_since < 90:
                    recency_score = 5
                else:
                    recency_score = 0
            else:
                recency_score = 0
            
            score += recency_score
            breakdown['recency'] = recency_score
            
            # Profile completeness (0-20 points)
            completeness = 0
            if contact.email:
                completeness += 5
            if contact.phone:
                completeness += 5
            if contact.company:
                completeness += 5
            if hasattr(contact, 'industry') and contact.industry:
                completeness += 5
            
            score += completeness
            breakdown['profile_completeness'] = completeness
            
            # Tag quality (0-15 points)
            if contact.tags:
                tag_count = len(contact.tags.split(','))
                tag_score = min(15, tag_count * 3)
            else:
                tag_score = 0
            
            score += tag_score
            breakdown['tags'] = tag_score
            
            # Conversion indicators (0-10 points)
            conversion_score = 0
            if hasattr(contact, 'purchases') and contact.purchases:
                conversion_score = 10
            
            score += conversion_score
            breakdown['conversions'] = conversion_score
            
            # Normalize to 0-100
            total_score = min(100, score)
            
            # Classify
            if total_score >= 80:
                classification = 'hot'
            elif total_score >= 60:
                classification = 'warm'
            elif total_score >= 40:
                classification = 'cold'
            else:
                classification = 'frozen'
            
            return {
                'score': total_score,
                'classification': classification,
                'breakdown': breakdown,
                'recommendation': PredictiveAnalyticsService._get_lead_recommendation(classification)
            }
            
        except Exception as e:
            logger.error(f"Error calculating lead score: {e}")
            return {
                'score': 0,
                'classification': 'unknown',
                'breakdown': {},
                'recommendation': 'Unable to calculate score'
            }
    
    @staticmethod
    def _get_lead_recommendation(classification):
        """Get marketing recommendation based on classification."""
        recommendations = {
            'hot': 'High priority! Reach out immediately with personalized offer. Consider direct sales contact.',
            'warm': 'Nurture with targeted content. Send case studies and product demos.',
            'cold': 'Re-engagement campaign recommended. Offer valuable content to warm up.',
            'frozen': 'Low priority. Consider automated drip campaign or list cleanup.'
        }
        return recommendations.get(classification, 'No recommendation available')
    
    @staticmethod
    def predict_churn_risk(contact):
        """
        Predict customer churn risk.
        
        Returns:
            dict: Churn risk analysis
        """
        try:
            from models import EmailTracking
            
            risk_score = 0
            indicators = []
            
            # Check engagement decline
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            sixty_days_ago = datetime.utcnow() - timedelta(days=60)
            
            recent_activity = EmailTracking.query.filter(
                EmailTracking.contact_id == contact.id,
                EmailTracking.created_at >= thirty_days_ago
            ).count()
            
            older_activity = EmailTracking.query.filter(
                EmailTracking.contact_id == contact.id,
                EmailTracking.created_at >= sixty_days_ago,
                EmailTracking.created_at < thirty_days_ago
            ).count()
            
            # Declining engagement
            if older_activity > 0 and recent_activity < (older_activity * 0.5):
                risk_score += 30
                indicators.append('Engagement declined by 50%+ in last 30 days')
            
            # No recent activity
            last_activity = EmailTracking.query.filter_by(
                contact_id=contact.id
            ).order_by(EmailTracking.created_at.desc()).first()
            
            if last_activity:
                days_inactive = (datetime.utcnow() - last_activity.created_at).days
                if days_inactive > 90:
                    risk_score += 40
                    indicators.append(f'No activity for {days_inactive} days')
                elif days_inactive > 60:
                    risk_score += 25
                    indicators.append(f'Inactive for {days_inactive} days')
            else:
                risk_score += 50
                indicators.append('Never engaged')
            
            # Low email open rate
            total_sent = EmailTracking.query.filter(
                EmailTracking.contact_id == contact.id,
                EmailTracking.event_type == 'sent'
            ).count()
            
            total_opens = EmailTracking.query.filter(
                EmailTracking.contact_id == contact.id,
                EmailTracking.event_type == 'open'
            ).count()
            
            if total_sent > 0:
                open_rate = (total_opens / total_sent) * 100
                if open_rate < 10:
                    risk_score += 20
                    indicators.append(f'Very low open rate ({open_rate:.1f}%)')
            
            # Determine risk level
            if risk_score >= 70:
                risk_level = 'critical'
                action = 'Immediate intervention required. Launch win-back campaign.'
            elif risk_score >= 50:
                risk_level = 'high'
                action = 'High risk of churn. Send re-engagement offer.'
            elif risk_score >= 30:
                risk_level = 'medium'
                action = 'Monitor closely. Increase engagement frequency.'
            else:
                risk_level = 'low'
                action = 'Continue current engagement strategy.'
            
            return {
                'risk_score': min(100, risk_score),
                'risk_level': risk_level,
                'indicators': indicators,
                'action': action,
                'days_inactive': days_inactive if last_activity else 999
            }
            
        except Exception as e:
            logger.error(f"Error predicting churn: {e}")
            return {
                'risk_score': 0,
                'risk_level': 'unknown',
                'indicators': [],
                'action': 'Unable to assess risk'
            }
    
    @staticmethod
    def optimize_send_time(contact_id=None):
        """
        Determine optimal send time based on historical engagement.
        
        Returns:
            dict: Best times to send
        """
        try:
            from models import EmailTracking
            from sqlalchemy import func, extract
            
            # Analyze open patterns by hour and day
            query = db.session.query(
                extract('dow', EmailTracking.created_at).label('day_of_week'),
                extract('hour', EmailTracking.created_at).label('hour'),
                func.count(EmailTracking.id).label('open_count')
            ).filter(
                EmailTracking.event_type == 'open'
            )
            
            if contact_id:
                query = query.filter(EmailTracking.contact_id == contact_id)
            
            results = query.group_by('day_of_week', 'hour').all()
            
            # Find peak engagement times
            if not results:
                return {
                    'best_time': {'day': 'Tuesday', 'hour': 10},
                    'confidence': 'low',
                    'note': 'Using industry defaults (Tuesday 10 AM)'
                }
            
            # Get top 3 best times
            sorted_results = sorted(results, key=lambda x: x.open_count, reverse=True)[:3]
            
            day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
            
            recommendations = []
            for result in sorted_results:
                recommendations.append({
                    'day': day_names[int(result.day_of_week)],
                    'hour': int(result.hour),
                    'engagement_count': result.open_count
                })
            
            return {
                'recommendations': recommendations,
                'best_time': recommendations[0] if recommendations else {'day': 'Tuesday', 'hour': 10},
                'confidence': 'high' if len(results) > 20 else 'medium'
            }
            
        except Exception as e:
            logger.error(f"Error optimizing send time: {e}")
            return {
                'best_time': {'day': 'Tuesday', 'hour': 10},
                'confidence': 'low',
                'note': 'Error analyzing data, using defaults'
            }
    
    @staticmethod
    def predict_content_performance(content_type, subject_line=None):
        """
        Predict content performance using AI.
        
        Args:
            content_type: Type of content (email, social, etc)
            subject_line: Email subject line to analyze
        
        Returns:
            dict: Performance predictions
        """
        try:
            if not subject_line:
                return {
                    'predicted_open_rate': 22.0,
                    'predicted_click_rate': 2.5,
                    'quality_score': 70,
                    'suggestions': []
                }
            
            # Analyze subject line
            suggestions = []
            quality_score = 70
            
            # Length check
            if len(subject_line) < 20:
                suggestions.append('Subject line is too short. Aim for 40-60 characters.')
                quality_score -= 10
            elif len(subject_line) > 70:
                suggestions.append('Subject line is too long. Keep it under 60 characters.')
                quality_score -= 10
            
            # Emoji check
            if any(ord(char) > 127 for char in subject_line):
                quality_score += 5
            else:
                suggestions.append('Consider adding an emoji for higher open rates.')
            
            # Personalization check
            if '{' in subject_line or 'you' in subject_line.lower():
                quality_score += 10
            else:
                suggestions.append('Add personalization tokens like {{first_name}} for better engagement.')
            
            # Urgency/scarcity
            urgency_words = ['now', 'today', 'limited', 'last chance', 'hurry', 'ending']
            if any(word in subject_line.lower() for word in urgency_words):
                quality_score += 5
            
            # Predict rates based on quality score
            predicted_open_rate = 15 + (quality_score * 0.3)
            predicted_click_rate = 1.5 + (quality_score * 0.05)
            
            return {
                'predicted_open_rate': round(predicted_open_rate, 1),
                'predicted_click_rate': round(predicted_click_rate, 1),
                'quality_score': quality_score,
                'suggestions': suggestions,
                'analysis': {
                    'length': len(subject_line),
                    'has_emoji': any(ord(char) > 127 for char in subject_line),
                    'has_personalization': '{' in subject_line or 'you' in subject_line.lower()
                }
            }
            
        except Exception as e:
            logger.error(f"Error predicting content performance: {e}")
            return {
                'predicted_open_rate': 22.0,
                'predicted_click_rate': 2.5,
                'quality_score': 70,
                'suggestions': ['Unable to analyze']
            }
    
    @staticmethod
    def forecast_revenue(days_ahead=30):
        """
        Forecast revenue based on historical data.
        
        Returns:
            dict: Revenue forecast
        """
        try:
            from models import AffiliateConversion
            
            # Get historical data (last 90 days)
            ninety_days_ago = datetime.utcnow() - timedelta(days=90)
            
            conversions = AffiliateConversion.query.filter(
                AffiliateConversion.converted_at >= ninety_days_ago
            ).all()
            
            if not conversions:
                return {
                    'forecast': 0,
                    'confidence': 'low',
                    'trend': 'insufficient_data'
                }
            
            # Calculate daily average
            total_revenue = sum(c.sale_amount for c in conversions)
            avg_daily_revenue = total_revenue / 90
            
            # Simple linear forecast
            forecast = avg_daily_revenue * days_ahead
            
            # Calculate trend
            recent_30 = [c for c in conversions if c.converted_at >= (datetime.utcnow() - timedelta(days=30))]
            older_30 = [c for c in conversions if c.converted_at < (datetime.utcnow() - timedelta(days=30)) and c.converted_at >= (datetime.utcnow() - timedelta(days=60))]
            
            recent_avg = sum(c.sale_amount for c in recent_30) / 30 if recent_30 else 0
            older_avg = sum(c.sale_amount for c in older_30) / 30 if older_30 else 1
            
            trend_pct = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
            
            if trend_pct > 10:
                trend = 'growing'
                forecast *= 1.1  # Adjust forecast up
            elif trend_pct < -10:
                trend = 'declining'
                forecast *= 0.9  # Adjust forecast down
            else:
                trend = 'stable'
            
            return {
                'forecast': round(forecast, 2),
                'daily_average': round(avg_daily_revenue, 2),
                'trend': trend,
                'trend_percentage': round(trend_pct, 1),
                'confidence': 'high' if len(conversions) > 50 else 'medium',
                'days_ahead': days_ahead
            }
            
        except Exception as e:
            logger.error(f"Error forecasting revenue: {e}")
            return {
                'forecast': 0,
                'confidence': 'low',
                'trend': 'error'
            }
