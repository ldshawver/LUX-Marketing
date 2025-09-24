# LUX Marketing VPS Deployment Guide

## Quick Deployment

### 1. Run the Deployment Script
```bash
# Make the script executable
chmod +x deploy_to_vps.sh

# Run the deployment
./deploy_to_vps.sh
```

### 2. Complete Post-Deployment Setup
```bash
# SSH into your VPS
ssh root@194.195.92.52

# Update API keys in environment file
nano /etc/environment

# Replace with your actual keys:
# OPENAI_API_KEY=sk-your-actual-openai-key
# Add other keys as needed

# Start the application
systemctl start lux-marketing
systemctl status lux-marketing

# Setup SSL certificate
apt install certbot python3-certbot-nginx -y
certbot --nginx -d lux.lucifercruz.com -d www.lux.lucifercruz.com
```

## Manual Setup (Alternative)

### Step 1: Prepare VPS
```bash
ssh root@194.195.92.52

# Update system
apt update && apt upgrade -y

# Install dependencies
apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib

# Create application user
useradd -m -s /bin/bash luxapp
mkdir -p /var/www/lux-marketing
chown luxapp:www-data /var/www/lux-marketing
```

### Step 2: Upload Application
```bash
# From your local machine (in the LUX Marketing directory):
rsync -avz --progress \
    --exclude='.git*' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='venv*' \
    --exclude='tmp' \
    ./ root@194.195.92.52:/var/www/lux-marketing/
```

### Step 3: Setup Python Environment
```bash
# SSH back to VPS
ssh root@194.195.92.52

cd /var/www/lux-marketing

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install flask gunicorn flask-sqlalchemy flask-login flask-wtf
pip install psycopg2-binary msal openai requests twilio apscheduler
pip install email-validator itsdangerous werkzeug jinja2
```

### Step 4: Setup Database
```bash
# Create PostgreSQL database and user
sudo -u postgres psql -c "CREATE DATABASE lux_marketing;"
sudo -u postgres psql -c "CREATE USER luxuser WITH PASSWORD 'luxpass123';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE lux_marketing TO luxuser;"
```

### Step 5: Configure Environment
```bash
# Create environment variables file
cat > /etc/environment << 'EOF'
DATABASE_URL=postgresql://luxuser:luxpass123@localhost/lux_marketing
SESSION_SECRET=lux-super-secret-key-production-2024
OPENAI_API_KEY=your-openai-key-here
FLASK_ENV=production
FLASK_DEBUG=False
EOF
```

### Step 6: Create Systemd Service
```bash
# Create service file
tee /etc/systemd/system/lux-marketing.service > /dev/null << 'EOF'
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
EOF
```

### Step 7: Create Gunicorn Configuration
```bash
cd /var/www/lux-marketing

tee gunicorn.conf.py > /dev/null << 'EOF'
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
tmp_upload_dir = None
EOF
```

### Step 8: Configure Nginx
```bash
# Create Nginx site configuration
tee /etc/nginx/sites-available/lux-marketing > /dev/null << 'EOF'
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
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/lux-marketing /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and restart nginx
nginx -t
systemctl restart nginx
systemctl enable nginx
```

### Step 9: Start Services
```bash
# Set up logging directory
mkdir -p /var/log/lux-marketing
chown luxapp:www-data /var/log/lux-marketing

# Set permissions
chown -R luxapp:www-data /var/www/lux-marketing
chmod -R 755 /var/www/lux-marketing

# Enable and start services
systemctl daemon-reload
systemctl enable lux-marketing
systemctl start lux-marketing
```

## Testing Your Deployment

### 1. Check Service Status
```bash
systemctl status lux-marketing
systemctl status nginx
systemctl status postgresql
```

### 2. Check Logs
```bash
# Application logs
journalctl -u lux-marketing -f

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Application-specific logs
tail -f /var/log/lux-marketing/access.log
tail -f /var/log/lux-marketing/error.log
```

### 3. Test Application Access
```bash
# Test local access (on VPS)
curl -I http://127.0.0.1:8000

# Test nginx proxy (on VPS)
curl -I http://localhost

# Test from external (your local machine)
curl -I http://194.195.92.52
```

### 4. Database Connection Test
```bash
# On VPS, test database connection
cd /var/www/lux-marketing
source venv/bin/activate
python3 -c "
import os
os.environ['DATABASE_URL'] = 'postgresql://luxuser:luxpass123@localhost/lux_marketing'
from app import app, db
with app.app_context():
    db.create_all()
    print('✅ Database connection successful!')
"
```

## SSL Certificate Setup

### Install Certbot
```bash
apt install certbot python3-certbot-nginx -y
```

### Get SSL Certificate
```bash
# Make sure your domain points to your VPS IP first
certbot --nginx -d lux.lucifercruz.com -d www.lux.lucifercruz.com

# Auto-renewal (already set up by certbot)
systemctl enable certbot.timer
```

## Troubleshooting

### Common Issues:

1. **Service won't start**:
   ```bash
   journalctl -u lux-marketing --no-pager -l
   ```

2. **Permission errors**:
   ```bash
   chown -R luxapp:www-data /var/www/lux-marketing
   chmod -R 755 /var/www/lux-marketing
   ```

3. **Database connection issues**:
   ```bash
   sudo -u postgres psql lux_marketing
   \du  # Check users
   \l   # Check databases
   ```

4. **Nginx errors**:
   ```bash
   nginx -t  # Test config
   tail -f /var/log/nginx/error.log
   ```

### Restart Services:
```bash
systemctl restart lux-marketing
systemctl restart nginx
systemctl restart postgresql
```

## Production Optimizations

### 1. Firewall Setup
```bash
ufw enable
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
```

### 2. Log Rotation
```bash
tee /etc/logrotate.d/lux-marketing > /dev/null << 'EOF'
/var/log/lux-marketing/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 luxapp www-data
    postrotate
        systemctl reload lux-marketing
    endscript
}
EOF
```

### 3. Performance Monitoring
```bash
# Install htop for monitoring
apt install htop

# Monitor processes
htop

# Monitor disk usage
df -h

# Monitor memory usage
free -m
```

Your LUX Marketing platform should now be live at: https://lux.lucifercruz.com