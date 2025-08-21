#!/bin/bash

# Deployment script for lux.lucifercruz.com
# Run this locally to deploy to your VPS

VPS_IP="194.195.92.52"
DOMAIN="lux.lucifercruz.com"
PACKAGE_FILE="email-marketing-app-20250821_005020.tar.gz"

echo "=== Deploying Email Marketing App to lux.lucifercruz.com ==="
echo ""

# Check if package exists
if [ ! -f "$PACKAGE_FILE" ]; then
    echo "Error: Package file $PACKAGE_FILE not found!"
    echo "Run ./create-deployment-package.sh first"
    exit 1
fi

echo "Step 1: Uploading files to VPS..."
scp "$PACKAGE_FILE" "root@$VPS_IP:/root/"

echo ""
echo "Step 2: Connecting to VPS and running deployment..."

ssh "root@$VPS_IP" << 'REMOTE_SCRIPT'
cd /root

# Extract the package
echo "Extracting deployment package..."
tar -xzf email-marketing-app-*.tar.gz
cd email-marketing-app-*

# Make scripts executable
chmod +x *.sh

# Run the deployment
echo "Starting automated deployment..."
./deploy.sh

# Configure domain
echo "Configuring domain for lux.lucifercruz.com..."
sed -i 's/your_domain.com www.your_domain.com/lux.lucifercruz.com www.lux.lucifercruz.com/g' /etc/nginx/sites-available/email-marketing

# Test nginx configuration
nginx -t

# Restart services
systemctl restart email-marketing nginx

echo ""
echo "=== Basic Deployment Complete ==="
echo ""
echo "Next steps:"
echo "1. Configure API credentials in /opt/email-marketing/.env"
echo "2. Set up SSL certificate"
echo "3. Test the application"

REMOTE_SCRIPT

echo ""
echo "=== Deployment script completed ==="
echo ""
echo "Your app should now be running at:"
echo "  http://lux.lucifercruz.com"
echo ""
echo "To set up SSL certificate, run:"
echo "  ssh root@$VPS_IP"
echo "  cd /root/email-marketing-app-*"
echo "  ./ssl-setup.sh lux.lucifercruz.com"
echo ""
echo "To configure API keys:"
echo "  ssh root@$VPS_IP"
echo "  nano /opt/email-marketing/.env"
echo ""