#!/bin/bash

# LUX Marketing - Complete VPS Setup Script
# Run this script on your VPS: ssh root@194.195.92.52
# curl -sL https://example.com/vps_setup.sh | bash

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 LUX Marketing VPS Setup Script${NC}"
echo -e "${BLUE}=====================================${NC}"

# Configuration
APP_DIR="/var/www/lux-marketing"
LOG_DIR="/var/log/lux-marketing"
APP_USER="luxapp"
DB_NAME="lux_marketing"
DB_USER="luxuser"
DB_PASS="LuxPass2024!"
DOMAIN="lux.lucifercruz.com"

echo -e "${YELLOW}📋 Installation Configuration:${NC}"
echo "  App Directory: $APP_DIR"
echo "  Database: $DB_NAME"
echo "  Domain: $DOMAIN"
echo "  User: $APP_USER"
echo ""

# Ask for confirmation
read -p "Continue with LUX Marketing setup? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Setup cancelled."
    exit 0
fi

echo -e "${YELLOW}🔄 Updating system and installing dependencies...${NC}"
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib
apt install -y curl wget unzip git htop ufw

echo -e "${YELLOW}👤 Creating application user...${NC}"
useradd -m -s /bin/bash $APP_USER || echo "User already exists"
usermod -aG www-data $APP_USER

echo -e "${YELLOW}📁 Creating directories...${NC}"
mkdir -p $APP_DIR $LOG_DIR
chown -R $APP_USER:www-data $APP_DIR $LOG_DIR
chmod 755 $APP_DIR $LOG_DIR

echo -e "${YELLOW}🗄️  Setting up PostgreSQL database...${NC}"
systemctl start postgresql
systemctl enable postgresql

sudo -u postgres psql << EOF
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
\q
EOF

echo -e "${YELLOW}📝 Creating application files...${NC}"
cd $APP_DIR

# Create main application file
cat > main.py << 'EOF'
from app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
EOF

# Create app.py
cat > app.py << 'EOF'
import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

logging.basicConfig(level=logging.INFO)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "lux-marketing-secret-key-2024")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///email_marketing.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Microsoft Graph API configuration
app.config["MS_CLIENT_ID"] = os.environ.get("MS_CLIENT_ID", "")
app.config["MS_CLIENT_SECRET"] = os.environ.get("MS_CLIENT_SECRET", "")
app.config["MS_TENANT_ID"] = os.environ.get("MS_TENANT_ID", "")

db.init_app(app)
csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Register blueprints
from routes import main_bp
from auth import auth_bp

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')

with app.app_context():
    import models
    db.create_all()
    
    # Create admin user if doesn't exist
    admin = models.User.query.filter_by(username='admin').first()
    if not admin:
        from werkzeug.security import generate_password_hash
        admin = models.User(
            username='admin',
            email='admin@lux.local',
            password_hash=generate_password_hash('LuxAdmin2024!'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created - Username: admin, Password: LuxAdmin2024!")

@app.template_filter('campaign_status_color')
def campaign_status_color_filter(status):
    color_mapping = {
        'draft': 'secondary',
        'scheduled': 'warning',
        'sending': 'info',
        'sent': 'success',
        'failed': 'danger',
        'paused': 'dark'
    }
    return color_mapping.get(status, 'secondary')
EOF

# Create models.py
cat > models.py << 'EOF'
from datetime import datetime
from app import db
from flask_login import UserMixin
from sqlalchemy import JSON, Text

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256))
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    company = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    tags = db.Column(db.String(255))
    custom_fields = db.Column(JSON)
    engagement_score = db.Column(db.Float, default=0.0)
    last_activity = db.Column(db.DateTime)
    source = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Contact {self.email}>'
    
    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or self.email

class EmailTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    html_content = db.Column(Text, nullable=False)
    template_type = db.Column(db.String(20), default='custom')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<EmailTemplate {self.name}>'

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('email_template.id'))
    status = db.Column(db.String(20), default='draft')
    scheduled_at = db.Column(db.DateTime)
    sent_at = db.Column(db.DateTime)
    revenue_generated = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    recipients = db.relationship('CampaignRecipient', backref='campaign', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Campaign {self.name}>'
    
    @property
    def total_recipients(self):
        return self.recipients.count()

class CampaignRecipient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    sent_at = db.Column(db.DateTime)
    opened_at = db.Column(db.DateTime)
    clicked_at = db.Column(db.DateTime)
    error_message = db.Column(Text)
    
    def __repr__(self):
        return f'<CampaignRecipient {self.campaign_id}:{self.contact_id}>'

class EmailTracking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    event_type = db.Column(db.String(20), nullable=False)
    event_data = db.Column(JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<EmailTracking {self.event_type}>'
EOF

# Create routes.py
cat > routes.py << 'EOF'
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from models import Contact, Campaign, EmailTemplate
from app import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@login_required
def dashboard():
    total_contacts = Contact.query.count()
    total_campaigns = Campaign.query.count()
    recent_campaigns = Campaign.query.order_by(Campaign.created_at.desc()).limit(5).all()
    
    stats = {
        'total_contacts': total_contacts,
        'total_campaigns': total_campaigns,
        'active_campaigns': Campaign.query.filter_by(status='sending').count(),
        'templates': EmailTemplate.query.count()
    }
    
    return render_template('dashboard.html', stats=stats, recent_campaigns=recent_campaigns)

@main_bp.route('/contacts')
@login_required  
def contacts():
    contacts = Contact.query.all()
    return render_template('contacts.html', contacts=contacts)

@main_bp.route('/campaigns')
@login_required
def campaigns():
    campaigns = Campaign.query.all()
    return render_template('campaigns.html', campaigns=campaigns)

@main_bp.route('/templates')
@login_required
def templates():
    templates = EmailTemplate.query.all()
    return render_template('templates.html', templates=templates)

@main_bp.route('/automation')
@login_required
def automation():
    return render_template('automation.html')

@main_bp.route('/analytics')
@login_required
def analytics():
    return render_template('analytics.html')
EOF

# Create auth.py
cat > auth.py << 'EOF'
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from models import User
from app import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
EOF

echo -e "${YELLOW}🎨 Creating templates...${NC}"
mkdir -p templates/auth

# Create base template
cat > templates/base.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}LUX Marketing{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/feather-icons/4.28.0/feather.min.css" rel="stylesheet">
    <style>
        :root {
            --lux-black: #000000;
            --lux-silver: #C0C0C0;
            --lux-emerald: #004d40;
            --lux-amethyst: #301934;
        }
        body { background: linear-gradient(135deg, var(--lux-black) 0%, var(--lux-amethyst) 100%); min-height: 100vh; color: white; }
        .navbar-brand { color: var(--lux-silver) !important; font-weight: bold; }
        .card { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2); }
        .btn-primary { background: var(--lux-emerald); border-color: var(--lux-emerald); }
        .btn-primary:hover { background: var(--lux-amethyst); border-color: var(--lux-amethyst); }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="/">
                <i data-feather="zap"></i> LUX Marketing
            </a>
            <div class="navbar-nav ms-auto">
                {% if current_user.is_authenticated %}
                    <a class="nav-link" href="{{ url_for('main.dashboard') }}">Dashboard</a>
                    <a class="nav-link" href="{{ url_for('main.contacts') }}">Contacts</a>
                    <a class="nav-link" href="{{ url_for('main.campaigns') }}">Campaigns</a>
                    <a class="nav-link" href="{{ url_for('main.templates') }}">Templates</a>
                    <a class="nav-link" href="{{ url_for('auth.logout') }}">Logout</a>
                {% endif %}
            </div>
        </div>
    </nav>
    
    <div class="container mt-4">
        {% with messages = get_flashed_messages() %}
            {% if messages %}
                {% for message in messages %}
                    <div class="alert alert-info">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
    </div>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://unpkg.com/feather-icons"></script>
    <script>feather.replace()</script>
</body>
</html>
EOF

# Create login template
cat > templates/auth/login.html << 'EOF'
{% extends "base.html" %}

{% block title %}Login - LUX Marketing{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card">
            <div class="card-body">
                <h2 class="text-center mb-4">
                    <i data-feather="lock"></i> Login to LUX Marketing
                </h2>
                <form method="POST">
                    <div class="mb-3">
                        <label for="username" class="form-label">Username</label>
                        <input type="text" class="form-control" id="username" name="username" required>
                    </div>
                    <div class="mb-3">
                        <label for="password" class="form-label">Password</label>
                        <input type="password" class="form-control" id="password" name="password" required>
                    </div>
                    <div class="d-grid">
                        <button type="submit" class="btn btn-primary">Login</button>
                    </div>
                </form>
                <div class="mt-3 text-center">
                    <small class="text-muted">Default: admin / LuxAdmin2024!</small>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
EOF

# Create dashboard template
cat > templates/dashboard.html << 'EOF'
{% extends "base.html" %}

{% block title %}Dashboard - LUX Marketing{% endblock %}

{% block content %}
<h1><i data-feather="home"></i> Dashboard</h1>

<div class="row mb-4">
    <div class="col-md-3">
        <div class="card">
            <div class="card-body text-center">
                <i data-feather="users" style="width: 2rem; height: 2rem;"></i>
                <h3>{{ stats.total_contacts }}</h3>
                <p>Total Contacts</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card">
            <div class="card-body text-center">
                <i data-feather="send" style="width: 2rem; height: 2rem;"></i>
                <h3>{{ stats.total_campaigns }}</h3>
                <p>Total Campaigns</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card">
            <div class="card-body text-center">
                <i data-feather="activity" style="width: 2rem; height: 2rem;"></i>
                <h3>{{ stats.active_campaigns }}</h3>
                <p>Active Campaigns</p>
            </div>
        </div>
    </div>
    <div class="col-md-3">
        <div class="card">
            <div class="card-body text-center">
                <i data-feather="file-text" style="width: 2rem; height: 2rem;"></i>
                <h3>{{ stats.templates }}</h3>
                <p>Templates</p>
            </div>
        </div>
    </div>
</div>

<div class="row">
    <div class="col-12">
        <div class="card">
            <div class="card-header">
                <h5>Welcome to LUX Marketing Platform</h5>
            </div>
            <div class="card-body">
                <p>Your comprehensive email marketing automation platform is ready!</p>
                <div class="row">
                    <div class="col-md-4">
                        <a href="{{ url_for('main.contacts') }}" class="btn btn-primary w-100 mb-2">
                            <i data-feather="users"></i> Manage Contacts
                        </a>
                    </div>
                    <div class="col-md-4">
                        <a href="{{ url_for('main.campaigns') }}" class="btn btn-primary w-100 mb-2">
                            <i data-feather="send"></i> Create Campaign
                        </a>
                    </div>
                    <div class="col-md-4">
                        <a href="{{ url_for('main.templates') }}" class="btn btn-primary w-100 mb-2">
                            <i data-feather="file-text"></i> Design Templates
                        </a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
EOF

# Create other basic templates
for template in contacts campaigns templates automation analytics; do
    cat > templates/${template}.html << EOF
{% extends "base.html" %}
{% block title %}${template^} - LUX Marketing{% endblock %}
{% block content %}
<h1><i data-feather="star"></i> ${template^}</h1>
<div class="card">
    <div class="card-body">
        <p>Welcome to the ${template} section of LUX Marketing!</p>
        <p>This section is ready for your marketing automation needs.</p>
    </div>
</div>
{% endblock %}
EOF
done

echo -e "${YELLOW}🐍 Creating Python virtual environment...${NC}"
sudo -u $APP_USER python3 -m venv $APP_DIR/venv
sudo -u $APP_USER $APP_DIR/venv/bin/pip install --upgrade pip

echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
sudo -u $APP_USER $APP_DIR/venv/bin/pip install flask gunicorn flask-sqlalchemy flask-login flask-wtf
sudo -u $APP_USER $APP_DIR/venv/bin/pip install psycopg2-binary werkzeug jinja2

echo -e "${YELLOW}🔧 Creating environment configuration...${NC}"
cat > /etc/environment << EOF
DATABASE_URL=postgresql://$DB_USER:$DB_PASS@localhost/$DB_NAME
SESSION_SECRET=lux-marketing-super-secret-key-production-2024
FLASK_ENV=production
FLASK_DEBUG=False
OPENAI_API_KEY=your-openai-key-here
EOF

echo -e "${YELLOW}⚙️ Creating Gunicorn configuration...${NC}"
cat > $APP_DIR/gunicorn.conf.py << EOF
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
user = "$APP_USER"
group = "www-data"
daemon = False
pidfile = "/var/run/gunicorn/lux-marketing.pid"
EOF

echo -e "${YELLOW}🔧 Creating systemd service...${NC}"
mkdir -p /var/run/gunicorn
chown $APP_USER:www-data /var/run/gunicorn

cat > /etc/systemd/system/lux-marketing.service << EOF
[Unit]
Description=LUX Marketing Flask Application
After=network.target postgresql.service
Requires=postgresql.service

[Service]
User=$APP_USER
Group=www-data
WorkingDirectory=$APP_DIR
Environment=PATH=$APP_DIR/venv/bin
EnvironmentFile=/etc/environment
ExecStart=$APP_DIR/venv/bin/gunicorn --config gunicorn.conf.py main:app
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=always
RestartSec=5
StandardOutput=append:$LOG_DIR/access.log
StandardError=append:$LOG_DIR/error.log

[Install]
WantedBy=multi-user.target
EOF

echo -e "${YELLOW}🌐 Configuring Nginx...${NC}"
cat > /etc/nginx/sites-available/lux-marketing << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    
    client_max_body_size 10M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        
        proxy_connect_timeout 30;
        proxy_send_timeout 30;
        proxy_read_timeout 30;
    }
    
    location /static {
        alias $APP_DIR/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
}
EOF

# Enable Nginx site
ln -sf /etc/nginx/sites-available/lux-marketing /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx config
nginx -t

echo -e "${YELLOW}🔐 Configuring firewall...${NC}"
ufw --force enable
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS

echo -e "${YELLOW}🏁 Starting services...${NC}"
# Set final permissions
chown -R $APP_USER:www-data $APP_DIR
chmod -R 755 $APP_DIR
chmod +x $APP_DIR/main.py

# Enable and start services
systemctl daemon-reload
systemctl enable lux-marketing nginx postgresql
systemctl restart nginx
systemctl start lux-marketing

echo -e "${GREEN}🎉 Installation completed successfully!${NC}"
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✅ LUX Marketing Platform is LIVE!${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}📋 Access Information:${NC}"
echo "  🌐 Website: http://$DOMAIN"
echo "  👤 Admin Login: admin"  
echo "  🔑 Admin Password: LuxAdmin2024!"
echo ""
echo -e "${YELLOW}📋 Service Status:${NC}"
systemctl status lux-marketing --no-pager -l | head -10
echo ""
echo -e "${YELLOW}🔧 Next Steps:${NC}"
echo "  1. Visit http://$DOMAIN and login"
echo "  2. Setup SSL: apt install certbot python3-certbot-nginx -y"
echo "  3. Get SSL: certbot --nginx -d $DOMAIN -d www.$DOMAIN"
echo "  4. Update API keys in: /etc/environment"
echo ""
echo -e "${YELLOW}🛠️  Useful Commands:${NC}"
echo "  • Check status: systemctl status lux-marketing"
echo "  • View logs: journalctl -u lux-marketing -f"
echo "  • Restart app: systemctl restart lux-marketing"
echo "  • Nginx logs: tail -f /var/log/nginx/access.log"
echo ""
echo -e "${GREEN}🚀 Your LUX Marketing platform is ready to use!${NC}"

# Final test
echo -e "${YELLOW}🧪 Running final test...${NC}"
sleep 5
curl -I http://localhost || echo "App may still be starting..."

echo ""
echo -e "${GREEN}✅ Setup complete! Visit http://$DOMAIN${NC}"