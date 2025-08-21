#!/bin/bash

# Email Marketing Automation App - Deployment Script for Debian 12
# Run this script as root or with sudo

set -e

APP_NAME="email-marketing"
APP_USER="email-marketing"
APP_DIR="/opt/$APP_NAME"
VENV_DIR="$APP_DIR/venv"
LOG_DIR="/var/log/$APP_NAME"

echo "=== Email Marketing App Deployment Script ==="
echo "Setting up application on Debian 12..."

# Update system packages
echo "Updating system packages..."
apt update && apt upgrade -y

# Install required system packages
echo "Installing system dependencies..."
apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib supervisor git curl

# Create application user
echo "Creating application user..."
if ! id "$APP_USER" &>/dev/null; then
    adduser --system --group --home "$APP_DIR" --disabled-password "$APP_USER"
fi

# Create directories
echo "Creating directories..."
mkdir -p "$APP_DIR" "$LOG_DIR"
chown "$APP_USER:$APP_USER" "$APP_DIR" "$LOG_DIR"

# Setup PostgreSQL database
echo "Setting up PostgreSQL database..."
sudo -u postgres psql -c "CREATE USER $APP_USER WITH PASSWORD 'secure_password_change_me';" || true
sudo -u postgres psql -c "CREATE DATABASE ${APP_NAME}_db OWNER $APP_USER;" || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ${APP_NAME}_db TO $APP_USER;" || true

# Copy application files (assumes files are in current directory)
echo "Copying application files..."
cp -r ./* "$APP_DIR/"
chown -R "$APP_USER:$APP_USER" "$APP_DIR"

# Create Python virtual environment
echo "Setting up Python virtual environment..."
sudo -u "$APP_USER" python3 -m venv "$VENV_DIR"
sudo -u "$APP_USER" "$VENV_DIR/bin/pip" install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
sudo -u "$APP_USER" "$VENV_DIR/bin/pip" install -r "$APP_DIR/deploy_requirements.txt"

# Create environment configuration
echo "Creating environment configuration..."
cat > "$APP_DIR/.env" << EOL
# Production Environment Configuration
FLASK_ENV=production
DATABASE_URL=postgresql://$APP_USER:secure_password_change_me@localhost/${APP_NAME}_db
SESSION_SECRET=$(openssl rand -hex 32)

# Microsoft Graph API Configuration (Update these with your values)
MS_CLIENT_ID=your_client_id_here
MS_CLIENT_SECRET=your_client_secret_here
MS_TENANT_ID=your_tenant_id_here

# OpenAI Configuration (Optional)
OPENAI_API_KEY=your_openai_api_key_here
EOL

chown "$APP_USER:$APP_USER" "$APP_DIR/.env"
chmod 600 "$APP_DIR/.env"

echo "=== IMPORTANT: Update the .env file with your actual credentials ==="
echo "Edit $APP_DIR/.env and add your:"
echo "  - Microsoft Graph API credentials"
echo "  - OpenAI API key (optional)"
echo "  - Change the PostgreSQL password"
echo ""

# Create systemd service
echo "Creating systemd service..."
cat > /etc/systemd/system/$APP_NAME.service << EOL
[Unit]
Description=Email Marketing Automation App
After=network.target postgresql.service

[Service]
Type=exec
User=$APP_USER
Group=$APP_USER
WorkingDirectory=$APP_DIR
Environment=PATH=$VENV_DIR/bin
EnvironmentFile=$APP_DIR/.env
ExecStart=$VENV_DIR/bin/gunicorn --config gunicorn.conf.py wsgi:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOL

# Configure Nginx
echo "Configuring Nginx..."
cat > /etc/nginx/sites-available/$APP_NAME << EOL
server {
    listen 80;
    server_name your_domain.com www.your_domain.com;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Static files
    location /static {
        alias $APP_DIR/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Application
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://127.0.0.1:5000/health;
    }
}
EOL

# Enable Nginx site
ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

# Initialize database
echo "Initializing database..."
cd "$APP_DIR"
sudo -u "$APP_USER" bash -c "source $VENV_DIR/bin/activate && source .env && python3 -c 'from app import app, db; app.app_context().push(); db.create_all()'"

# Enable and start services
echo "Starting services..."
systemctl daemon-reload
systemctl enable $APP_NAME
systemctl start $APP_NAME
systemctl enable nginx
systemctl restart nginx

echo ""
echo "=== Deployment Complete! ==="
echo ""
echo "Your email marketing app is now running!"
echo ""
echo "Next steps:"
echo "1. Update $APP_DIR/.env with your API credentials"
echo "2. Update /etc/nginx/sites-available/$APP_NAME with your domain"
echo "3. Restart services: systemctl restart $APP_NAME nginx"
echo "4. Set up SSL certificate with certbot (recommended)"
echo ""
echo "Default admin login:"
echo "  Username: admin"
echo "  Password: admin123"
echo ""
echo "Service management:"
echo "  Start: systemctl start $APP_NAME"
echo "  Stop: systemctl stop $APP_NAME"
echo "  Restart: systemctl restart $APP_NAME"
echo "  Status: systemctl status $APP_NAME"
echo "  Logs: journalctl -u $APP_NAME -f"
echo ""
echo "Application logs: $LOG_DIR/"
echo ""