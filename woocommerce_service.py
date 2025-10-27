"""
WooCommerce Integration Service
Provides integration with WordPress WooCommerce for product management
"""
import os
import logging
from typing import List, Dict, Optional
from woocommerce import API

logger = logging.getLogger(__name__)


class WooCommerceService:
    """Service class for WooCommerce integration"""
    
    def __init__(self):
        """Initialize WooCommerce API client"""
        self.api = None
        self._init_api()
    
    def _init_api(self):
        """Initialize WooCommerce API with credentials from environment"""
        try:
            store_url = os.environ.get('WC_STORE_URL')
            consumer_key = os.environ.get('WC_CONSUMER_KEY')
            consumer_secret = os.environ.get('WC_CONSUMER_SECRET')
            
            if not all([store_url, consumer_key, consumer_secret]):
                logger.warning("WooCommerce credentials not configured")
                return
            
            self.api = API(
                url=store_url,
                consumer_key=consumer_key,
                consumer_secret=consumer_secret,
                version="wc/v3",
                timeout=30
            )
            logger.info("WooCommerce API initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize WooCommerce API: {e}")
    
    def is_configured(self) -> bool:
        """Check if WooCommerce integration is configured"""
        return self.api is not None
    
    def get_products(self, page: int = 1, per_page: int = 20, **kwargs) -> Optional[List[Dict]]:
        """
        Fetch products from WooCommerce
        
        Args:
            page: Page number
            per_page: Number of products per page (max 100)
            **kwargs: Additional query parameters
            
        Returns:
            List of product dictionaries or None on error
        """
        if not self.is_configured():
            logger.error("WooCommerce not configured")
            return None
        
        try:
            params = {
                'page': page,
                'per_page': min(per_page, 100),
                **kwargs
            }
            
            response = self.api.get("products", params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to fetch products: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching products from WooCommerce: {e}")
            return None
    
    def get_product(self, product_id: int) -> Optional[Dict]:
        """
        Fetch single product by ID
        
        Args:
            product_id: WooCommerce product ID
            
        Returns:
            Product dictionary or None
        """
        if not self.is_configured():
            logger.error("WooCommerce not configured")
            return None
        
        try:
            response = self.api.get(f"products/{product_id}")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to fetch product {product_id}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching product {product_id}: {e}")
            return None
    
    def search_products(self, search_term: str, per_page: int = 20) -> Optional[List[Dict]]:
        """
        Search products by name or description
        
        Args:
            search_term: Search query
            per_page: Number of results
            
        Returns:
            List of matching products or None
        """
        return self.get_products(per_page=per_page, search=search_term)
    
    def get_product_categories(self, page: int = 1, per_page: int = 50) -> Optional[List[Dict]]:
        """
        Fetch product categories
        
        Args:
            page: Page number
            per_page: Number of categories per page
            
        Returns:
            List of category dictionaries or None
        """
        if not self.is_configured():
            logger.error("WooCommerce not configured")
            return None
        
        try:
            params = {
                'page': page,
                'per_page': min(per_page, 100)
            }
            
            response = self.api.get("products/categories", params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to fetch categories: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching product categories: {e}")
            return None
    
    def get_all_products(self, max_products: int = 1000) -> List[Dict]:
        """
        Fetch all products with pagination handling
        
        Args:
            max_products: Maximum number of products to fetch
            
        Returns:
            List of all products
        """
        all_products = []
        page = 1
        per_page = 100
        
        while len(all_products) < max_products:
            products = self.get_products(page=page, per_page=per_page)
            
            if not products:
                break
            
            all_products.extend(products)
            
            if len(products) < per_page:
                break
            
            page += 1
        
        return all_products[:max_products]
    
    def get_orders(self, page: int = 1, per_page: int = 20, status: str = 'any') -> Optional[List[Dict]]:
        """
        Fetch orders from WooCommerce
        
        Args:
            page: Page number
            per_page: Number of orders per page
            status: Order status filter (any, pending, processing, completed, etc.)
            
        Returns:
            List of order dictionaries or None
        """
        if not self.is_configured():
            logger.error("WooCommerce not configured")
            return None
        
        try:
            params = {
                'page': page,
                'per_page': min(per_page, 100),
                'status': status
            }
            
            response = self.api.get("orders", params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to fetch orders: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching orders: {e}")
            return None
    
    def get_customers(self, page: int = 1, per_page: int = 20) -> Optional[List[Dict]]:
        """
        Fetch customers from WooCommerce
        
        Args:
            page: Page number
            per_page: Number of customers per page
            
        Returns:
            List of customer dictionaries or None
        """
        if not self.is_configured():
            logger.error("WooCommerce not configured")
            return None
        
        try:
            params = {
                'page': page,
                'per_page': min(per_page, 100)
            }
            
            response = self.api.get("customers", params=params)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to fetch customers: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching customers: {e}")
            return None
