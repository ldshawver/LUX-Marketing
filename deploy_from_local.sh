#!/bin/bash

# LUX Marketing Local to VPS Deployment Script
# For deploying from local zip file to VPS

set -e  # Exit on any error

# Configuration
LOCAL_ZIP="/Users/lukeshawver/Downloads/LUX-Email-Marketing-Bot (4).zip"
EXTRACT_DIR="/tmp/lux-marketing-deploy"
VPS_HOST="194.195.92.52"
VPS_USER="root"
VPS_PATH="/var/www/lux-marketing"
DOMAIN="lux.lucifercruz.com"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 LUX Marketing Local to VPS Deployment${NC}"
echo "=============================================="

# Check if zip file exists
if [ ! -f "$LOCAL_ZIP" ]; then
    echo -e "${RED}❌ Error: Zip file not found at: $LOCAL_ZIP${NC}"
    echo "Please check the file path and try again."
    exit 1
fi

echo -e "${YELLOW}📋 Deployment Configuration:${NC}"
echo "  Local Zip: $LOCAL_ZIP"
echo "  VPS Host: $VPS_HOST"
echo "  VPS User: $VPS_USER"
echo "  VPS Path: $VPS_PATH"
echo "  Domain: $DOMAIN"
echo ""

# Ask for confirmation
read -p "Continue with deployment? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled."
    exit 0
fi

echo -e "${YELLOW}📦 Extracting zip file locally...${NC}"
rm -rf "$EXTRACT_DIR" 2>/dev/null || true
mkdir -p "$EXTRACT_DIR"
unzip -q "$LOCAL_ZIP" -d "$EXTRACT_DIR"

# Find the actual extracted directory
EXTRACTED_PATH=$(find "$EXTRACT_DIR" -type d -name "*LUX*" -o -name "*lux*" -o -name "*marketing*" | head -1)
if [ -z "$EXTRACTED_PATH" ]; then
    # If no specific directory found, use first subdirectory
    EXTRACTED_PATH=$(find "$EXTRACT_DIR" -mindepth 1 -maxdepth 1 -type d | head -1)
fi

if [ -z "$EXTRACTED_PATH" ]; then
    echo -e "${RED}❌ Error: Could not find extracted files${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Files extracted to: $EXTRACTED_PATH${NC}"

echo -e "${YELLOW}🔍 Testing VPS connection...${NC}"
if ! ssh -o ConnectTimeout=10 $VPS_USER@$VPS_HOST "echo 'Connection successful'"; then
    echo -e "${RED}❌ Cannot connect to VPS${NC}"
    echo "Please check your SSH connection to: $VPS_USER@$VPS_HOST"
    exit 1
fi

echo -e "${GREEN}✅ VPS connection successful${NC}"

echo -e "${YELLOW}💾 Creating backup of existing deployment...${NC}"
ssh $VPS_USER@$VPS_HOST "
    if [ -d '$VPS_PATH' ]; then
        mkdir -p /var/backups
        cp -r $VPS_PATH /var/backups/lux-marketing-backup-\$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
        echo 'Backup created'
    else
        echo 'No existing deployment found'
    fi
"

echo -e "${YELLOW}📁 Creating deployment directory on VPS...${NC}"
ssh $VPS_USER@$VPS_HOST "
    mkdir -p $VPS_PATH
    rm -rf $VPS_PATH/* 2>/dev/null || true
"

echo -e "${YELLOW}📤 Uploading files to VPS...${NC}"
rsync -avz --progress \
    --exclude='*.zip' \
    --exclude='.git*' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.DS_Store' \
    --exclude='node_modules' \
    --exclude='venv*' \
    --exclude='.env*' \
    --exclude='instance' \
    --exclude='*.log' \
    --exclude='tmp' \
    "$EXTRACTED_PATH/" $VPS_USER@$VPS_HOST:$VPS_PATH/

echo -e "${GREEN}✅ Files uploaded successfully${NC}"

echo -e "${YELLOW}🔧 Setting up VPS environment...${NC}"
ssh $VPS_USER@$VPS_HOST << 'EOF'
    cd /var/www/lux-marketing
    
    # Update system
    apt update
    apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib unzip
    
    # Create application user
    useradd -m -s /bin/bash luxapp || echo 'User already exists'
    usermod -aG www-data luxapp
    
    # Set permissions
    chown -R luxapp:www-data /var/www/lux-marketing
    chmod -R 755 /var/www/lux-marketing
    
    # Create directories
    mkdir -p logs static/uploads instance /var/log/lux-marketing
    chown luxapp:www-data /var/log/lux-marketing
    
    # Setup PostgreSQL
    sudo -u postgres psql -c "CREATE DATABASE lux_marketing;" 2>/dev/null || echo 'Database exists'
    sudo -u postgres psql -c "CREATE USER luxuser WITH PASSWORD 'luxpass123';" 2>/dev/null || echo 'User exists'
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE lux_marketing TO luxuser;" 2>/dev/null || true
    
    # Create virtual environment as luxapp user
    sudo -u luxapp python3 -m venv /var/www/lux-marketing/venv
    sudo -u luxapp /var/www/lux-marketing/venv/bin/pip install --upgrade pip
    
    # Install dependencies
    sudo -u luxapp /var/www/lux-marketing/venv/bin/pip install flask gunicorn flask-sqlalchemy flask-login flask-wtf
    sudo -u luxapp /var/www/lux-marketing/venv/bin/pip install psycopg2-binary msal openai requests twilio apscheduler
    sudo -u luxapp /var/www/lux-marketing/venv/bin/pip install email-validator itsdangerous werkzeug jinja2
    
    echo "Environment setup completed"
EOF

echo -e "${YELLOW}⚙️ Configuring production services...${NC}"
ssh $VPS_USER@$VPS_HOST << 'EOF'
    cd /var/www/lux-marketing
    
    # Create environment file
    cat > /etc/environment << 'ENVEOF'
DATABASE_URL=postgresql://luxuser:luxpass123@localhost/lux_marketing
SESSION_SECRET=lux-super-secret-key-production-2024
OPENAI_API_KEY=your-openai-key-here
FLASK_ENV=production
FLASK_DEBUG=False
ENVEOF
    
    # Create Gunicorn config
    cat > gunicorn.conf.py << 'CONFEOF'
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
user = "luxapp"
group = "www-data"
CONFEOF
    
    # Create systemd service
    cat > /etc/systemd/system/lux-marketing.service << 'SERVICEEOF'
[Unit]
Description=LUX Marketing Flask Application
After=network.target postgresql.service
Requires=postgresql.service

[Service]
User=luxapp
Group=www-data
WorkingDirectory=/var/www/lux-marketing
Environment=PATH=/var/www/lux-marketing/venv/bin
EnvironmentFile=/etc/environment
ExecStart=/var/www/lux-marketing/venv/bin/gunicorn --config gunicorn.conf.py main:app
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=5
StandardOutput=append:/var/log/lux-marketing/access.log
StandardError=append:/var/log/lux-marketing/error.log

[Install]
WantedBy=multi-user.target
SERVICEEOF

    # Create Nginx config
    cat > /etc/nginx/sites-available/lux-marketing << 'NGINXEOF'
server {
    listen 80;
    server_name lux.lucifercruz.com www.lux.lucifercruz.com;
    
    client_max_body_size 10M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
    
    location /static {
        alias /var/www/lux-marketing/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
}
NGINXEOF
    
    # Enable services
    ln -sf /etc/nginx/sites-available/lux-marketing /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    nginx -t
    systemctl daemon-reload
    systemctl enable lux-marketing nginx postgresql
    systemctl restart nginx
    
    echo "Services configured"
EOF

echo -e "${YELLOW}🗑️  Cleaning up temporary files...${NC}"
rm -rf "$EXTRACT_DIR"

echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo ""
echo -e "${YELLOW}📋 Next steps:${NC}"
echo ""
echo "1. SSH into your VPS and start the application:"
echo "   ssh root@194.195.92.52"
echo "   systemctl start lux-marketing"
echo "   systemctl status lux-marketing"
echo ""
echo "2. Update API keys (replace with your real keys):"
echo "   nano /etc/environment"
echo ""
echo "3. Setup SSL certificate:"
echo "   apt install certbot python3-certbot-nginx -y"
echo "   certbot --nginx -d lux.lucifercruz.com -d www.lux.lucifercruz.com"
echo ""
echo "4. Your site will be available at:"
echo "   http://lux.lucifercruz.com"
echo "   https://lux.lucifercruz.com (after SSL)"
echo ""
echo -e "${GREEN}✅ LUX Marketing platform is ready!${NC}"