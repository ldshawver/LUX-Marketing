import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///email_marketing.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Microsoft Graph API configuration
app.config["MS_CLIENT_ID"] = os.environ.get("MS_CLIENT_ID", "")
app.config["MS_CLIENT_SECRET"] = os.environ.get("MS_CLIENT_SECRET", "")
app.config["MS_TENANT_ID"] = os.environ.get("MS_TENANT_ID", "")

# Initialize extensions
db.init_app(app)

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

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp, url_prefix='/auth')

with app.app_context():
    # Import models to ensure tables are created
    import models
    db.create_all()
    
    # Create default admin user if it doesn't exist
    from models import User
    from werkzeug.security import generate_password_hash
    
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin_user = User()  # type: ignore
        admin_user.username = 'admin'
        admin_user.email = 'admin@example.com'
        admin_user.password_hash = generate_password_hash('admin123')
        db.session.add(admin_user)
        db.session.commit()
        logging.info("Created default admin user: admin/admin123")

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
