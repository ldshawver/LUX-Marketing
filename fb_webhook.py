"""
Facebook Webhook Handler for LUX Marketing Platform
Minimal implementation that ALWAYS validates correctly
"""
import os
from flask import Blueprint, request

fb_webhook = Blueprint("fb_webhook", __name__)

FB_VERIFY_TOKEN = os.environ.get("FB_VERIFY_TOKEN", "lux_fb_webhook_secret_123")

@fb_webhook.route("/webhooks/facebook", methods=["GET", "POST"])
def facebook_webhook():
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        print("FB VERIFY REQUEST:", mode, token, challenge, flush=True)

        if mode == "subscribe" and token == FB_VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Verification token mismatch", 403

    if request.method == "POST":
        print("FB EVENT:", request.get_json(), flush=True)
        return "EVENT_RECEIVED", 200
