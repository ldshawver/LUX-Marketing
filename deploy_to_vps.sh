#!/bin/bash

# LUX Marketing VPS Deployment Script
# This script safely uploads and deploys your LUX Marketing app to your VPS

set -e  # Exit on any error

# Configuration
LOCAL_PATH="/Users/lukeshawver/Downloads/lux-marketing"
VPS_HOST="194.195.92.52"
VPS_USER="deploy"  # Recommended: create dedicated user (not root)
VPS_PATH="/var/www/lux-marketing"
BACKUP_PATH="/var/backups/lux-marketing-$(date +%Y%m%d_%H%M%S)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 LUX Marketing VPS Deployment Script${NC}"
echo "=================================================="

# Verify local files exist
if [ ! -d "$LOCAL_PATH" ]; then
    echo -e "${RED}❌ Error: Local path $LOCAL_PATH not found${NC}"
    echo "Please ensure your LUX Marketing files are in: $LOCAL_PATH"
    exit 1
fi

echo -e "${YELLOW}📋 Deployment Configuration:${NC}"
echo "  Local Path: $LOCAL_PATH"
echo "  VPS Host: $VPS_HOST"
echo "  VPS User: $VPS_USER"
echo "  VPS Path: $VPS_PATH"
echo ""

# Ask for confirmation
read -p "Continue with deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

echo -e "${YELLOW}🔍 Testing VPS connection...${NC}"
if ! ssh -o ConnectTimeout=10 $VPS_USER@$VPS_HOST "echo 'Connection successful'"; then
    echo -e "${RED}❌ Cannot connect to VPS. Please check:${NC}"
    echo "  1. VPS is accessible: ssh $VPS_USER@$VPS_HOST"
    echo "  2. User '$VPS_USER' exists (create with: useradd -m $VPS_USER)"
    echo "  3. SSH keys are set up or password authentication works"
    exit 1
fi

echo -e "${GREEN}✅ VPS connection successful${NC}"

echo -e "${YELLOW}💾 Creating backup of existing deployment...${NC}"
ssh $VPS_USER@$VPS_HOST "
    if [ -d '$VPS_PATH' ]; then
        sudo mkdir -p /var/backups
        sudo cp -r $VPS_PATH $BACKUP_PATH 2>/dev/null || true
        echo 'Backup created at: $BACKUP_PATH'
    else
        echo 'No existing deployment found, skipping backup'
    fi
"

echo -e "${YELLOW}📁 Creating deployment directory...${NC}"
ssh $VPS_USER@$VPS_HOST "
    sudo mkdir -p $VPS_PATH
    sudo chown $VPS_USER:www-data $VPS_PATH
    sudo chmod 755 $VPS_PATH
"

echo -e "${YELLOW}📤 Uploading files to VPS...${NC}"
# Exclude certain files/directories that shouldn't be deployed
rsync -avz --progress \
    --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.DS_Store' \
    --exclude='node_modules' \
    --exclude='venv' \
    --exclude='.env' \
    --exclude='instance' \
    --exclude='*.log' \
    $LOCAL_PATH/ $VPS_USER@$VPS_HOST:$VPS_PATH/

echo -e "${YELLOW}🔧 Setting up deployment environment...${NC}"
ssh $VPS_USER@$VPS_HOST "
    cd $VPS_PATH
    
    # Set proper permissions
    sudo chown -R $VPS_USER:www-data $VPS_PATH
    sudo chmod -R 755 $VPS_PATH
    sudo chmod -R 664 $VPS_PATH/*.py 2>/dev/null || true
    
    # Create necessary directories
    mkdir -p logs static/uploads instance
    
    # Install Python dependencies (if requirements.txt exists)
    if [ -f 'requirements.txt' ]; then
        echo 'Installing Python dependencies...'
        python3 -m venv venv 2>/dev/null || true
        source venv/bin/activate 2>/dev/null || true
        pip install -r requirements.txt || echo 'Note: Install dependencies manually if needed'
    fi
    
    echo 'Deployment files copied successfully'
"

echo -e "${YELLOW}⚙️  Post-deployment setup...${NC}"
ssh $VPS_USER@$VPS_HOST "
    cd $VPS_PATH
    
    # Create systemd service file (optional)
    sudo tee /etc/systemd/system/lux-marketing.service > /dev/null << 'EOF'
[Unit]
Description=LUX Marketing Flask Application
After=network.target

[Service]
User=deploy
Group=www-data
WorkingDirectory=$VPS_PATH
Environment=PATH=$VPS_PATH/venv/bin
ExecStart=$VPS_PATH/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 2 main:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF
    
    # Reload systemd and enable service
    sudo systemctl daemon-reload
    sudo systemctl enable lux-marketing 2>/dev/null || true
    
    echo 'Service configuration created'
"

echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo ""
echo -e "${YELLOW}📋 Next steps:${NC}"
echo "  1. Set up environment variables on VPS:"
echo "     sudo nano /etc/environment"
echo "     Add: DATABASE_URL, OPENAI_API_KEY, SESSION_SECRET, etc."
echo ""
echo "  2. Configure web server (nginx/apache) to proxy to port 5000"
echo ""
echo "  3. Start the application:"
echo "     ssh $VPS_USER@$VPS_HOST"
echo "     sudo systemctl start lux-marketing"
echo "     sudo systemctl status lux-marketing"
echo ""
echo "  4. Set up SSL certificate for lux.lucifercruz.com"
echo ""
echo -e "${GREEN}✅ Your LUX Marketing app is ready for production!${NC}"

# Optional: Test the deployment
read -p "Would you like to test the deployment now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🧪 Testing deployment...${NC}"
    ssh $VPS_USER@$VPS_HOST "
        cd $VPS_PATH
        python3 -c 'import app; print(\"✅ Flask app imports successfully\")' 2>/dev/null || echo '⚠️  Check Python dependencies'
    "
fi