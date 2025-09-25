#!/bin/bash

# Direct Sync Deployment - No downloads needed
# Run this on your LOCAL machine to sync current Replit files to VPS

VPS_HOST="194.195.92.52"
VPS_USER="root"
VPS_PATH="/var/www/lux-marketing"

echo "🚀 Direct Sync Deployment to VPS"
echo "Checking what's currently on VPS vs what should be there..."

# First, let's check what login template is currently on VPS
echo "📋 Current VPS login template:"
ssh $VPS_USER@$VPS_HOST "head -20 $VPS_PATH/templates/login.html 2>/dev/null || echo 'File not found'"

echo ""
echo "This should show 'LUX Marketing' branding if deployment worked..."
echo ""
read -p "Press Enter to continue with force sync..."

# Force clear and redeploy
ssh $VPS_USER@$VPS_HOST << 'EOF'
    set -e
    
    echo "🛑 Stopping services..."
    systemctl stop lux-marketing 2>/dev/null || true
    systemctl stop nginx 2>/dev/null || true
    
    echo "📁 Backing up and clearing deployment directory..."
    if [ -d "/var/www/lux-marketing" ]; then
        cp -r /var/www/lux-marketing /var/backups/lux-old-$(date +%Y%m%d_%H%M%S) 2>/dev/null || true
    fi
    
    # Completely clear the directory
    rm -rf /var/www/lux-marketing
    mkdir -p /var/www/lux-marketing
    chown luxapp:www-data /var/www/lux-marketing
    
    echo "✅ VPS directory cleared and ready for new files"
EOF

echo ""
echo "📤 Now we need to get your current files to VPS..."
echo ""
echo "OPTION 1 - Use the tar file you downloaded:"
echo "If you have current-lux-replit.tar.gz on your local machine:"
echo "scp current-lux-replit.tar.gz $VPS_USER@$VPS_HOST:/tmp/"
echo ""
echo "OPTION 2 - Download directly to VPS (if you have the Replit URL):"
echo "ssh $VPS_USER@$VPS_HOST 'cd /tmp && wget https://YOUR-REPL-URL.replit.dev/current-lux-replit.tar.gz'"
echo ""
read -p "Which option? (1 or 2): " option

if [ "$option" = "1" ]; then
    echo "📤 Uploading tar file to VPS..."
    if [ -f "current-lux-replit.tar.gz" ]; then
        scp current-lux-replit.tar.gz $VPS_USER@$VPS_HOST:/tmp/
        echo "✅ File uploaded"
    else
        echo "❌ current-lux-replit.tar.gz not found in current directory"
        echo "Please download it from Replit first, then run this script from the same directory"
        exit 1
    fi
elif [ "$option" = "2" ]; then
    echo "Enter your Replit workspace URL (e.g., https://your-repl.replit.dev):"
    read repl_url
    ssh $VPS_USER@$VPS_HOST "cd /tmp && wget $repl_url/current-lux-replit.tar.gz"
else
    echo "Invalid option"
    exit 1
fi

# Extract and setup on VPS
echo "🔧 Extracting and setting up on VPS..."
ssh $VPS_USER@$VPS_HOST << 'EOF'
    set -e
    cd /var/www/lux-marketing
    
    echo "📦 Extracting files..."
    tar xzf /tmp/current-lux-replit.tar.gz
    
    echo "🔐 Setting permissions..."
    chown -R luxapp:www-data /var/www/lux-marketing
    chmod -R 755 /var/www/lux-marketing
    
    echo "🐍 Setting up Python environment..."
    sudo -u luxapp python3 -m venv venv
    sudo -u luxapp venv/bin/pip install flask gunicorn flask-sqlalchemy flask-login flask-wtf
    sudo -u luxapp venv/bin/pip install psycopg2-binary msal openai requests twilio apscheduler
    sudo -u luxapp venv/bin/pip install email-validator itsdangerous werkzeug jinja2
    
    echo "📁 Creating required directories..."
    mkdir -p static/uploads instance logs
    chown -R luxapp:www-data static/uploads instance logs
    
    echo "🗄️ Initializing database..."
    sudo -u luxapp -H bash -c "
        cd /var/www/lux-marketing
        source venv/bin/activate
        export DATABASE_URL='postgresql://luxuser:LuxPass2024!@localhost/lux_marketing'
        export SESSION_SECRET='lux-secret-2024'
        python3 -c \"
from app import app, db
with app.app_context():
    db.create_all()
    print('Database initialized')
\"
    "
    
    echo "🔄 Starting services..."
    systemctl start nginx
    systemctl start lux-marketing
    
    echo "✅ Deployment complete!"
    echo ""
    echo "📋 Verifying login template has LUX branding:"
    grep -i "lux marketing" /var/www/lux-marketing/templates/login.html || echo "⚠️ LUX branding not found!"
    
    echo ""
    echo "📋 Current template files:"
    ls -la /var/www/lux-marketing/templates/ | grep -E "(login|automation|forms)"
    
    # Cleanup
    rm -f /tmp/current-lux-replit.tar.gz
EOF

echo ""
echo "🎉 Direct sync deployment complete!"
echo "Visit: http://lux.lucifercruz.com"
echo ""
echo "The login page should now show 'LUX Marketing' branding"