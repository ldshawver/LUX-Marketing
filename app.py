import os
import logging
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///email_marketing.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# File upload configuration
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size
app.config["UPLOAD_FOLDER"] = "static/company_logos"

# Microsoft Graph API configuration
app.config["MS_CLIENT_ID"] = os.environ.get("MS_CLIENT_ID", "")
app.config["MS_CLIENT_SECRET"] = os.environ.get("MS_CLIENT_SECRET", "")
app.config["MS_TENANT_ID"] = os.environ.get("MS_TENANT_ID", "")

# Initialize extensions
db.init_app(app)

# Setup CSRF Protection  
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_CHECK_DEFAULT'] = True
app.config['WTF_CSRF_METHODS'] = ['POST', 'PUT', 'PATCH', 'DELETE']
app.config['WTF_CSRF_FIELD_NAME'] = 'csrf_token'
app.config['WTF_CSRF_TIME_LIMIT'] = None  # No time limit for CSRF tokens
app.config['WTF_CSRF_SSL_STRICT'] = False  # Allow non-HTTPS in development
csrf = CSRFProtect(app)

# Configure session cookie for iframe compatibility
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True  # Required when SameSite=None

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'  # type: ignore
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Register blueprints
from routes import main_bp
from auth import auth_bp
from user_management import user_bp
from advanced_config import advanced_config_bp

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(advanced_config_bp)

# Register Replit Auth blueprint if available
try:
    from replit_auth import make_replit_blueprint, is_replit_auth_enabled
    if is_replit_auth_enabled():
        replit_bp = make_replit_blueprint()
        if replit_bp:
            app.register_blueprint(replit_bp, url_prefix="/replit-auth")
            logging.info("Replit Auth blueprint registered successfully")
except Exception as e:
    logging.warning(f"Replit Auth not available: {e}")

# Root route - redirects to login
@app.route("/")
def index():
    return redirect(url_for("auth.login"))

with app.app_context():
    # Import models to ensure tables are created
    import models
    from error_logger import ErrorLog
    db.create_all()
    
    # Seed automation trigger library (idempotent)
    try:
        from services.automation_service import AutomationService
        AutomationService.seed_trigger_library()
        logging.info("Automation trigger library seeded successfully")
    except Exception as e:
        logging.error(f"Error seeding trigger library: {e}")
    
    # Initialize error logging
    try:
        from error_logger import setup_error_logging_handler
        setup_error_logging_handler()
        logging.info("Error logging system initialized successfully")
    except Exception as e:
        logging.error(f"Error initializing error logging: {e}")

# Add Jinja2 filters
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

# Initialize scheduler
from scheduler import init_scheduler
init_scheduler(app)

# Initialize AI Agent Scheduler
try:
    from agent_scheduler import initialize_agent_scheduler
    with app.app_context():
        agent_scheduler = initialize_agent_scheduler()
        if agent_scheduler:
            logging.info("AI Agent Scheduler initialized successfully")
except Exception as e:
    logging.error(f"Failed to initialize AI Agent Scheduler: {e}")
