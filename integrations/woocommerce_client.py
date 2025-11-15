"""
WooCommerce API Client for LUX Marketing
Fetches e-commerce data from WooCommerce stores
"""

import os
import logging
from datetime import datetime, timedelta
from woocommerce import API

logger = logging.getLogger(__name__)

class WooCommerceClient:
    """Client for interacting with WooCommerce REST API"""
    
    def __init__(self):
        """Initialize WooCommerce client with environment credentials"""
        self.store_url = os.getenv('WC_STORE_URL')
        self.consumer_key = os.getenv('WC_CONSUMER_KEY')
        self.consumer_secret = os.getenv('WC_CONSUMER_SECRET')
        self.client = None
        
        if self.is_configured():
            try:
                self.client = API(
                    url=self.store_url,
                    consumer_key=self.consumer_key,
                    consumer_secret=self.consumer_secret,
                    version="wc/v3",
                    timeout=30
                )
                logger.info("WooCommerce client initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing WooCommerce client: {e}")
    
    def is_configured(self):
        """Check if WooCommerce credentials are configured"""
        return bool(self.store_url and self.consumer_key and self.consumer_secret)
    
    def get_revenue_stats(self, days=30, start_date=None, end_date=None):
        """
        Get revenue statistics for the specified period
        
        Args:
            days: Number of days to look back (default: 30, used if dates not provided)
            start_date: Explicit start date for the query
            end_date: Explicit end date for the query
            
        Returns:
            dict: Revenue statistics including total sales, orders, average order value
        """
        if not self.client:
            logger.warning("WooCommerce client not configured")
            return None
        
        try:
            # Calculate date range
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=days)
            
            # Fetch orders within date range
            params = {
                'after': start_date.isoformat(),
                'before': end_date.isoformat(),
                'status': 'completed',
                'per_page': 100
            }
            
            orders = self.client.get("orders", params=params).json()
            
            if not orders:
                return {
                    'total_sales': 0,
                    'total_orders': 0,
                    'average_order_value': 0,
                    'period_days': days
                }
            
            # Calculate metrics
            total_sales = sum(float(order.get('total', 0)) for order in orders)
            total_orders = len(orders)
            average_order_value = total_sales / total_orders if total_orders > 0 else 0
            
            return {
                'total_sales': round(total_sales, 2),
                'total_orders': total_orders,
                'average_order_value': round(average_order_value, 2),
                'period_days': days,
                'currency': orders[0].get('currency', 'USD') if orders else 'USD'
            }
            
        except Exception as e:
            logger.error(f"Error fetching WooCommerce revenue stats: {e}")
            return None
    
    def get_top_products(self, limit=10):
        """
        Get top selling products
        
        Args:
            limit: Number of products to return (default: 10)
            
        Returns:
            list: Top selling products
        """
        if not self.client:
            return []
        
        try:
            params = {
                'orderby': 'popularity',
                'per_page': limit
            }
            products = self.client.get("products", params=params).json()
            return products
        except Exception as e:
            logger.error(f"Error fetching top products: {e}")
            return []
    
    def get_recent_orders(self, limit=10):
        """
        Get recent orders
        
        Args:
            limit: Number of orders to return (default: 10)
            
        Returns:
            list: Recent orders
        """
        if not self.client:
            return []
        
        try:
            params = {
                'per_page': limit,
                'orderby': 'date',
                'order': 'desc'
            }
            orders = self.client.get("orders", params=params).json()
            return orders
        except Exception as e:
            logger.error(f"Error fetching recent orders: {e}")
            return []


# Singleton instance
_woocommerce_client = None

def get_woocommerce_client():
    """Get or create WooCommerce client instance"""
    global _woocommerce_client
    if _woocommerce_client is None:
        _woocommerce_client = WooCommerceClient()
    return _woocommerce_client
