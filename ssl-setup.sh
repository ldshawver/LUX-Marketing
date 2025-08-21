#!/bin/bash

# SSL Certificate Setup Script using Let's Encrypt
# Run this after updating your domain in the Nginx configuration

APP_NAME="email-marketing"
DOMAIN=""

echo "=== SSL Certificate Setup ==="
echo ""

# Check if domain is provided
if [ -z "$1" ]; then
    echo "Usage: $0 your_domain.com"
    echo "Example: $0 example.com"
    exit 1
fi

DOMAIN="$1"

echo "Setting up SSL certificate for domain: $DOMAIN"

# Install certbot
echo "Installing certbot..."
apt update
apt install -y certbot python3-certbot-nginx

# Update Nginx configuration with the domain
echo "Updating Nginx configuration..."
sed -i "s/your_domain.com www.your_domain.com/$DOMAIN www.$DOMAIN/g" /etc/nginx/sites-available/$APP_NAME

# Test Nginx configuration
nginx -t

# Reload Nginx
systemctl reload nginx

# Obtain SSL certificate
echo "Obtaining SSL certificate..."
certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --non-interactive --agree-tos --email admin@$DOMAIN

# Set up automatic renewal
echo "Setting up automatic certificate renewal..."
systemctl enable certbot.timer
systemctl start certbot.timer

echo ""
echo "=== SSL Setup Complete! ==="
echo ""
echo "Your site is now available at:"
echo "  https://$DOMAIN"
echo "  https://www.$DOMAIN"
echo ""
echo "Certificate will auto-renew. Check status with:"
echo "  certbot certificates"
echo "  systemctl status certbot.timer"
echo ""