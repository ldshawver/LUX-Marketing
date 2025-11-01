"""
Affiliate Marketing Service
Deep-link builder, tracking, and commission management
"""

import os
import hashlib
import qrcode
from io import BytesIO
import base64
from datetime import datetime, timedelta
from models import db
import logging

logger = logging.getLogger(__name__)


class AffiliateService:
    """Service for affiliate marketing management"""
    
    @staticmethod
    def generate_affiliate_link(affiliate_id, product_url, campaign_name=None, custom_params=None, commission_rate=10.0, commission_type='percentage'):
        """
        Generate a trackable affiliate deep link.
        
        Args:
            affiliate_id: Affiliate/influencer ID
            product_url: Base product URL
            campaign_name: Optional campaign identifier
            custom_params: Additional tracking parameters
            commission_rate: Commission rate (default 10%)
            commission_type: 'percentage' or 'fixed'
        
        Returns:
            dict: Generated link data
        """
        try:
            if custom_params is None:
                custom_params = {}
            
            # Generate unique tracking code
            timestamp = datetime.utcnow().isoformat()
            tracking_string = f"{affiliate_id}:{product_url}:{timestamp}"
            tracking_code = hashlib.md5(tracking_string.encode()).hexdigest()[:12]
            
            # Store affiliate link in database for later lookup
            from models import AffiliateLink
            affiliate_link = AffiliateLink(
                tracking_code=tracking_code,
                affiliate_id=affiliate_id,
                product_url=product_url,
                campaign_name=campaign_name,
                commission_rate=commission_rate,
                commission_type=commission_type
            )
            db.session.add(affiliate_link)
            db.session.commit()
            
            # Build affiliate parameters
            affiliate_params = {
                'aff_id': affiliate_id,
                'aff_code': tracking_code,
                'utm_source': 'affiliate',
                'utm_medium': 'referral',
                'utm_campaign': campaign_name or f'affiliate_{affiliate_id}'
            }
            
            # Add custom parameters
            affiliate_params.update(custom_params)
            
            # Build query string
            param_string = '&'.join([f"{k}={v}" for k, v in affiliate_params.items() if v])
            
            # Combine with base URL
            separator = '&' if '?' in product_url else '?'
            deep_link = f"{product_url}{separator}{param_string}"
            
            return {
                'success': True,
                'deep_link': deep_link,
                'tracking_code': tracking_code,
                'short_code': tracking_code[:8],
                'affiliate_id': affiliate_id,
                'campaign': campaign_name
            }
            
        except Exception as e:
            logger.error(f"Error generating affiliate link: {e}")
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def generate_qr_code(url, size=300):
        """
        Generate QR code for affiliate link.
        
        Args:
            url: URL to encode
            size: QR code size in pixels
        
        Returns:
            str: Base64 encoded QR code image
        """
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(url)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_str = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{img_str}"
            
        except Exception as e:
            logger.error(f"Error generating QR code: {e}")
            return None
    
    @staticmethod
    def calculate_commission(sale_amount, commission_rate, commission_type='percentage'):
        """
        Calculate affiliate commission.
        
        Args:
            sale_amount: Sale value
            commission_rate: Commission rate (percentage or fixed amount)
            commission_type: 'percentage' or 'fixed'
        
        Returns:
            float: Commission amount
        """
        if commission_type == 'percentage':
            return (sale_amount * commission_rate / 100)
        else:
            return commission_rate
    
    @staticmethod
    def track_click(tracking_code, ip_address=None, user_agent=None, referrer=None):
        """
        Track affiliate link click.
        
        Args:
            tracking_code: Unique tracking code
            ip_address: Visitor IP
            user_agent: Browser user agent
            referrer: Referrer URL
        
        Returns:
            bool: Success status
        """
        try:
            from models import AffiliateClick
            
            click = AffiliateClick(
                tracking_code=tracking_code,
                ip_address=ip_address,
                user_agent=user_agent,
                referrer=referrer,
                clicked_at=datetime.utcnow()
            )
            
            db.session.add(click)
            db.session.commit()
            
            return True
            
        except Exception as e:
            logger.error(f"Error tracking affiliate click: {e}")
            return False
    
    @staticmethod
    def track_conversion(tracking_code, sale_amount, order_id=None):
        """
        Track affiliate conversion.
        
        Args:
            tracking_code: Affiliate tracking code
            sale_amount: Sale value
            order_id: Optional order identifier
        
        Returns:
            dict: Conversion data
        """
        try:
            from models import AffiliateConversion, AffiliateClick, AffiliateLink
            
            # Find the affiliate link to get commission settings
            affiliate_link = AffiliateLink.query.filter_by(
                tracking_code=tracking_code
            ).first()
            
            if not affiliate_link:
                return {'success': False, 'error': 'Affiliate link not found'}
            
            # Get affiliate_id and commission settings from the stored link
            affiliate_id = affiliate_link.affiliate_id
            commission_rate = affiliate_link.commission_rate
            commission_type = affiliate_link.commission_type
            
            # Calculate commission using actual stored settings
            commission = AffiliateService.calculate_commission(
                sale_amount, 
                commission_rate, 
                commission_type
            )
            
            conversion = AffiliateConversion(
                tracking_code=tracking_code,
                affiliate_id=affiliate_id,
                sale_amount=sale_amount,
                commission_amount=commission,
                order_id=order_id,
                converted_at=datetime.utcnow(),
                status='pending'
            )
            
            db.session.add(conversion)
            db.session.commit()
            
            return {
                'success': True,
                'conversion_id': conversion.id,
                'affiliate_id': affiliate_id,
                'commission': commission,
                'commission_rate': commission_rate,
                'commission_type': commission_type
            }
            
        except Exception as e:
            logger.error(f"Error tracking conversion: {e}")
            db.session.rollback()
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def get_affiliate_performance(affiliate_id, days=30):
        """
        Get performance metrics for an affiliate.
        
        Returns:
            dict: Performance data
        """
        try:
            from models import AffiliateClick, AffiliateConversion
            from sqlalchemy import func
            
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Get clicks
            total_clicks = AffiliateClick.query.filter(
                AffiliateClick.clicked_at >= start_date
            ).count()
            
            # Get conversions
            conversions = AffiliateConversion.query.filter(
                AffiliateConversion.affiliate_id == affiliate_id,
                AffiliateConversion.converted_at >= start_date
            ).all()
            
            total_conversions = len(conversions)
            total_sales = sum(c.sale_amount for c in conversions)
            total_commission = sum(c.commission_amount for c in conversions)
            pending_commission = sum(
                c.commission_amount for c in conversions if c.status == 'pending'
            )
            paid_commission = sum(
                c.commission_amount for c in conversions if c.status == 'paid'
            )
            
            conversion_rate = (total_conversions / total_clicks * 100) if total_clicks > 0 else 0
            avg_order_value = (total_sales / total_conversions) if total_conversions > 0 else 0
            
            return {
                'clicks': total_clicks,
                'conversions': total_conversions,
                'conversion_rate': conversion_rate,
                'total_sales': total_sales,
                'total_commission': total_commission,
                'pending_commission': pending_commission,
                'paid_commission': paid_commission,
                'avg_order_value': avg_order_value,
                'period_days': days
            }
            
        except Exception as e:
            logger.error(f"Error getting affiliate performance: {e}")
            return {
                'clicks': 0,
                'conversions': 0,
                'conversion_rate': 0,
                'total_sales': 0,
                'total_commission': 0,
                'pending_commission': 0,
                'paid_commission': 0,
                'avg_order_value': 0,
                'period_days': days
            }
    
    @staticmethod
    def process_payout(affiliate_id, amount, payment_method='paypal', notes=None):
        """
        Process commission payout.
        
        Args:
            affiliate_id: Affiliate ID
            amount: Payout amount
            payment_method: Payment method
            notes: Optional notes
        
        Returns:
            dict: Payout result
        """
        try:
            from models import AffiliatePayout, AffiliateConversion
            
            # Create payout record
            payout = AffiliatePayout(
                affiliate_id=affiliate_id,
                amount=amount,
                payment_method=payment_method,
                status='pending',
                notes=notes,
                requested_at=datetime.utcnow()
            )
            
            db.session.add(payout)
            
            # Mark conversions as paid
            AffiliateConversion.query.filter_by(
                affiliate_id=affiliate_id,
                status='pending'
            ).update({'status': 'paid', 'paid_at': datetime.utcnow()})
            
            db.session.commit()
            
            return {
                'success': True,
                'payout_id': payout.id,
                'amount': amount
            }
            
        except Exception as e:
            logger.error(f"Error processing payout: {e}")
            db.session.rollback()
            return {'success': False, 'error': str(e)}
