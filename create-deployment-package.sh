#!/bin/bash

# Script to create a deployment package for VPS upload
# This creates a tar.gz file with all necessary files

PACKAGE_NAME="email-marketing-app-$(date +%Y%m%d_%H%M%S)"
TEMP_DIR="/tmp/$PACKAGE_NAME"

echo "=== Creating Deployment Package ==="

# Create temporary directory
mkdir -p "$TEMP_DIR"

# Copy application files
echo "Copying application files..."
cp -r *.py "$TEMP_DIR/"
cp -r templates "$TEMP_DIR/"
cp -r static "$TEMP_DIR/"

# Copy deployment scripts
echo "Copying deployment scripts..."
cp deploy_requirements.txt "$TEMP_DIR/"
cp wsgi.py "$TEMP_DIR/"
cp gunicorn.conf.py "$TEMP_DIR/"
cp gunicorn-dev.conf.py "$TEMP_DIR/"
cp deploy.sh "$TEMP_DIR/"
cp ssl-setup.sh "$TEMP_DIR/"
cp backup.sh "$TEMP_DIR/"
cp update.sh "$TEMP_DIR/"
cp monitoring.sh "$TEMP_DIR/"
cp README-DEPLOYMENT.md "$TEMP_DIR/"

# Copy documentation
cp replit.md "$TEMP_DIR/"

# Make scripts executable
chmod +x "$TEMP_DIR"/*.sh

# Create the archive
echo "Creating archive..."
cd /tmp
tar -czf "$PACKAGE_NAME.tar.gz" "$PACKAGE_NAME"

# Move to current directory
mv "$PACKAGE_NAME.tar.gz" "$OLDPWD/"

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo "=== Package Created Successfully! ==="
echo ""
echo "Package file: $PACKAGE_NAME.tar.gz"
echo "Size: $(du -h $PACKAGE_NAME.tar.gz | cut -f1)"
echo ""
echo "To upload to your VPS:"
echo "  scp $PACKAGE_NAME.tar.gz root@your-vps-ip:/root/"
echo ""
echo "To extract on VPS:"
echo "  cd /root"
echo "  tar -xzf $PACKAGE_NAME.tar.gz"
echo "  cd $PACKAGE_NAME"
echo "  chmod +x deploy.sh"
echo "  ./deploy.sh"
echo ""