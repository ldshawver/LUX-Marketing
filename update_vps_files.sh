#!/bin/bash
# Update VPS files from local machine (Mac) to VPS

# VPS connection details
VPS_USER="root"
VPS_HOST="194.195.92.52"
VPS_PATH="/var/www/lux-marketing/"

# Local project path (your Replit export or local folder)
LOCAL_PATH="/Users/lukeshawver/Downloads/LUX-Email-Marketing-Bot/"

echo "🚀 Deploying files from $LOCAL_PATH to $VPS_USER@$VPS_HOST:$VPS_PATH"

# Use rsync for efficient sync (preserves permissions, only copies changes)
rsync -avz --delete "$LOCAL_PATH" "$VPS_USER@$VPS_HOST:$VPS_PATH"

echo "✅ Deployment complete!"