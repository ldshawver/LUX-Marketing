"""
Facebook Webhook Handler for LUX Marketing Platform
"""
import os
import logging
from flask import request

logger = logging.getLogger(__name__)
FB_VERIFY_TOKEN = os.environ.get("FB_VERIFY_TOKEN", "lux_fb_webhook_secret_123")


def register_facebook_webhook(app, csrf):
    """Register Facebook webhook route on the app with CSRF exemption"""
    
    @app.route("/webhooks/facebook", methods=["GET", "POST"])
    def facebook_webhook():
        """Handle Facebook webhooks - simple, bulletproof implementation"""
        try:
            if request.method == "GET":
                hub_mode = request.args.get("hub.mode")
                hub_token = request.args.get("hub.verify_token")
                hub_challenge = request.args.get("hub.challenge")
                
                logger.info(f"Facebook webhook verification: mode={hub_mode}, token_match={hub_token == FB_VERIFY_TOKEN}")
                
                if hub_mode == "subscribe" and hub_token == FB_VERIFY_TOKEN:
                    logger.info("Webhook verification successful")
                    return hub_challenge
                
                logger.error("Webhook verification failed - invalid token or mode")
                return "Forbidden", 403
            
            elif request.method == "POST":
                data = request.get_json()
                logger.info(f"Webhook POST received: {data}")
                return "ok", 200
                
        except Exception as e:
            logger.error(f"Webhook handler error: {e}", exc_info=True)
            return "ok", 200
    
    csrf.exempt(facebook_webhook)
    logger.info("Facebook webhook route registered at /webhooks/facebook (CSRF exempt)")
