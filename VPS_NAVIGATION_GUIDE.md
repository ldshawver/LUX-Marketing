# LUX Marketing - VPS Deployment & Navigation Guide

## 📁 App File Structure & Locations

### Root Directory Files (Main Entry Points)
```
/
├── main.py                 ← Flask app entry point (gunicorn loads this)
├── app.py                  ← Flask app initialization & configuration
├── wsgi.py                 ← WSGI configuration for production
├── requirements.txt        ← Python dependencies
└── models.py              ← Database models
```

### Core Application Directories
```
/routes.py                 ← Main routes (dashboard, tiles, CRM, etc.)
/auth.py                   ← Login/authentication routes
/user_management.py        ← User management routes
/advanced_config.py        ← Configuration routes

/static/                   ← Static files (CSS, JS, images)
  ├── css/custom.css       ← Main styles
  ├── js/main.js           ← Frontend JavaScript
  └── company_logos/       ← User-uploaded logos

/templates/                ← HTML templates
  ├── login.html           ← Login page template
  ├── dashboard.html       ← Main dashboard template
  ├── base.html            ← Base template
  └── [other templates]

/agents/                   ← AI Agents
  ├── base_agent.py        ← Base agent class
  ├── app_agent.py         ← Application intelligence agent
  └── [other agents]

/services/                 ← Business logic services
  ├── automation_service.py
  ├── secret_vault.py
  └── [other services]

/lux/                      ← LUX CRM system
  ├── crm_core.py
  └── [CRM files]
```

---

## 🔐 Login Flow & Access

### Step 1: Access Login Page
```
URL: https://your-vps.com/auth/login
OR: https://your-vps.com/
```
- Root URL "/" automatically redirects to login
- Login is at `/auth/login` endpoint

### Step 2: Login Credentials Required
- Email/Username (from database - create user first)
- Password (hashed in database)

**First Time Setup - Create Admin User:**
```python
python3 << 'EOF'
from app import app, db
from models import User, Company

with app.app_context():
    # Create admin company
    admin_company = Company(name="Admin Company")
    db.session.add(admin_company)
    db.session.flush()
    
    # Create admin user
    admin_user = User(
        email="admin@lux.com",
        username="admin",
        password_hash="hashed_password",
        is_admin=True,
        company_id=admin_company.id
    )
    admin_user.set_password("your_password_here")
    db.session.add(admin_user)
    db.session.commit()
    print("✓ Admin user created successfully")
EOF
```

---

## 📊 Navigation After Login

### Main Dashboard (Entry Point After Login)
```
URL: https://your-vps.com/dashboard
View: 9 interactive tiles with LUX brand colors (purple, cyan, pink, blue)
```

### Dashboard Tiles & Navigation

| Tile | URL | Function |
|------|-----|----------|
| **Email Hub** | `/email` | Manage email campaigns |
| **SMS Marketing** | `/sms` | SMS campaign management |
| **Social Media** | `/social` | Social media management |
| **Campaign Hub** | `/campaigns` | Create & manage campaigns |
| **Analytics** | `/analytics` | Performance tracking & reports |
| **Marketing Calendar** | `/calendar` | Schedule & plan campaigns |
| **Automations & Agents** | `/automations` | AI agents & automations |
| **LUX CRM** | `/crm` | Customer relationship management |
| **Ads Management** | `/ads` | Advertising campaigns |

### Main Routes After Login
```
/dashboard                 → Main dashboard with tiles
/email                     → Email campaign management
/campaigns                 → Campaign management
/automations              → AI agents dashboard
/crm                      → Customer relationship system
/contacts                 → Contact management
/analytics                → Analytics & reporting
/settings                 → Account settings
/user/profile             → User profile management
/agents                   → View all AI agents
/agents/reports           → Agent reports & metrics
```

---

## 🚀 VPS Deployment Steps

### 1. Prerequisites
```bash
# Install Python 3.11+
python3 --version

# Install pip and venv
sudo apt update
sudo apt install python3-pip python3-venv

# Install PostgreSQL (optional - for production)
sudo apt install postgresql postgresql-contrib
```

### 2. Clone & Setup App
```bash
# Clone repository
git clone <your-repo-url> /opt/lux-marketing
cd /opt/lux-marketing

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Create `.env` file in root directory:
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/lux_marketing

# Session
SESSION_SECRET=your-secret-key-here

# OpenAI (for AI agents)
OPENAI_API_KEY=sk-...

# Microsoft 365 (if using)
MS365_CLIENT_ID=...
MS365_CLIENT_SECRET=...
MS365_TENANT_ID=...

# Other API keys (Google Ads, Twitter, etc.)
# ... add as needed
```

### 4. Initialize Database
```bash
cd /opt/lux-marketing
source venv/bin/activate

python3 << 'EOF'
from app import app, db
with app.app_context():
    db.create_all()
    print("✓ Database initialized")
EOF
```

### 5. Run with Gunicorn (Production)
```bash
# Install gunicorn
pip install gunicorn

# Run application
gunicorn --bind 0.0.0.0:5000 \
         --workers 4 \
         --worker-class sync \
         --timeout 120 \
         main:app
```

### 6. Setup Nginx (Reverse Proxy)
```bash
# Install Nginx
sudo apt install nginx

# Create config file
sudo nano /etc/nginx/sites-available/lux-marketing

# Add this config:
```
```nginx
server {
    listen 80;
    server_name your-vps.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /opt/lux-marketing/static/;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/lux-marketing /etc/nginx/sites-enabled/

# Test & restart
sudo nginx -t
sudo systemctl restart nginx
```

### 7. Setup SSL with Let's Encrypt (Optional but Recommended)
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot certonly --nginx -d your-vps.com

# Auto-renew
sudo systemctl enable certbot.timer
```

---

## ⚠️ Common VPS Issues & Solutions

### Issue 1: "Connection refused" on port 5000
**Solution:**
```bash
# Check if app is running
ps aux | grep gunicorn

# Check port is listening
sudo netstat -tlnp | grep 5000

# Restart application
sudo systemctl restart lux-marketing
```

### Issue 2: Database connection errors
**Solution:**
```bash
# Verify DATABASE_URL environment variable
echo $DATABASE_URL

# Test database connection
psql $DATABASE_URL -c "SELECT 1"

# Check PostgreSQL is running
sudo systemctl status postgresql
```

### Issue 3: Static files not loading (CSS/JS not visible)
**Solution:**
```bash
# Make sure static files are served
# In Nginx config, ensure:
location /static/ {
    alias /opt/lux-marketing/static/;
}

# Restart Nginx
sudo systemctl restart nginx
```

### Issue 4: Gunicorn worker crashes
**Solution:**
```bash
# Check logs
journalctl -u lux-marketing -n 50

# Increase timeout in gunicorn
gunicorn --timeout 300 main:app

# Check Python version compatibility
python3 --version  # Should be 3.11+
```

---

## 🔄 Systemd Service Setup (Auto-start on VPS reboot)

Create `/etc/systemd/system/lux-marketing.service`:
```ini
[Unit]
Description=LUX Marketing Application
After=network.target postgresql.service

[Service]
Type=notify
User=www-data
WorkingDirectory=/opt/lux-marketing
Environment="PATH=/opt/lux-marketing/venv/bin"
Environment="DATABASE_URL=postgresql://user:password@localhost/lux_marketing"
Environment="OPENAI_API_KEY=sk-..."
Environment="SESSION_SECRET=your-secret"
ExecStart=/opt/lux-marketing/venv/bin/gunicorn \
    --bind 0.0.0.0:5000 \
    --workers 4 \
    --timeout 120 \
    main:app
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable & start:
```bash
sudo systemctl enable lux-marketing
sudo systemctl start lux-marketing
sudo systemctl status lux-marketing
```

---

## 📋 Verification Checklist

- [ ] Python 3.11+ installed
- [ ] Virtual environment created & activated
- [ ] Dependencies installed from requirements.txt
- [ ] Database initialized (PostgreSQL or SQLite)
- [ ] Environment variables configured in .env
- [ ] Admin user created in database
- [ ] Gunicorn running on port 5000
- [ ] Nginx reverse proxy configured
- [ ] Static files being served correctly
- [ ] Login page accessible at /auth/login
- [ ] Dashboard accessible after login at /dashboard
- [ ] All 9 dashboard tiles loading
- [ ] AI agents initialized and running

---

## 🎯 Quick Start Summary

```bash
# 1. SSH into VPS
ssh user@your-vps.com

# 2. Navigate to app directory
cd /opt/lux-marketing

# 3. Activate virtual environment
source venv/bin/activate

# 4. Start application
gunicorn --bind 0.0.0.0:5000 main:app

# 5. Access in browser
# → https://your-vps.com/auth/login
# → Login with credentials
# → Navigate to dashboard
# → Click on tiles to access features
```

---

## 📞 Support URLs

After Deployment:
- **Login**: `https://your-vps.com/auth/login`
- **Dashboard**: `https://your-vps.com/dashboard`
- **Automations**: `https://your-vps.com/automations`
- **CRM**: `https://your-vps.com/crm`
- **Settings**: `https://your-vps.com/settings`

All routes redirect to login if not authenticated.
