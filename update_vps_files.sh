#!/bin/bash

# Update VPS with Current Replit Files
# Run this on your LOCAL machine

VPS_HOST="194.195.92.52"
VPS_USER="root"
VPS_PATH="/var/www/lux-marketing"

echo "🚀 Updating VPS with Current LUX Marketing Files"

# Create a script that will run on VPS to update files
cat > update_files.sh << 'EOF'
#!/bin/bash

# Stop service
systemctl stop lux-marketing 2>/dev/null || true

# Backup current files
mkdir -p /var/backups
cp -r /var/www/lux-marketing /var/backups/old-lux-$(date +%Y%m%d_%H%M%S) 2>/dev/null || true

cd /var/www/lux-marketing

# Update base.html with LUX branding
cat > templates/base.html << 'BASEHTML'
<!DOCTYPE html>
<html lang="en" data-bs-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}LUX Marketing{% endblock %}</title>
    
    <!-- Bootstrap CSS -->
    <link href="https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css" rel="stylesheet">
    
    <!-- Feather Icons -->
    <script src="https://unpkg.com/feather-icons"></script>
    
    <!-- Custom CSS -->
    <link rel="stylesheet" href="{{ url_for('static', filename='css/custom.css') }}">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container">
            <a class="navbar-brand" href="{{ url_for('main.dashboard') }}">
                <i data-feather="mail"></i>
                LUX Marketing
            </a>
            
            {% if current_user.is_authenticated %}
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('main.dashboard') }}">
                            <i data-feather="home"></i> Dashboard
                        </a>
                    </li>
                    
                    <!-- Email Marketing Dropdown -->
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="emailDropdown" role="button" data-bs-toggle="dropdown">
                            <i data-feather="mail"></i> Email Marketing
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="{{ url_for('main.campaigns') }}"><i data-feather="send"></i> Campaigns</a></li>
                            <li><a class="dropdown-item" href="{{ url_for('main.templates') }}"><i data-feather="file-text"></i> Templates</a></li>
                            <li><a class="dropdown-item" href="{{ url_for('main.drag_drop_editor') }}"><i data-feather="edit-3"></i> Drag & Drop Editor</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="{{ url_for('main.automation_dashboard') }}"><i data-feather="zap"></i> Automation</a></li>
                        </ul>
                    </li>
                    
                    <!-- Contacts & Forms -->
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="contactsDropdown" role="button" data-bs-toggle="dropdown">
                            <i data-feather="users"></i> Contacts & Forms
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="{{ url_for('main.contacts') }}"><i data-feather="users"></i> All Contacts</a></li>
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="{{ url_for('main.forms_dashboard') }}"><i data-feather="clipboard"></i> Web Forms</a></li>
                            <li><a class="dropdown-item" href="{{ url_for('main.landing_pages') }}"><i data-feather="globe"></i> Landing Pages</a></li>
                        </ul>
                    </li>
                    
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('main.analytics') }}">
                            <i data-feather="bar-chart"></i> Analytics
                        </a>
                    </li>
                    
                    <li class="nav-item">
                        <a class="nav-link" href="{{ url_for('main.lux_agent') }}">
                            <i data-feather="cpu"></i> LUX AI
                        </a>
                    </li>
                </ul>
                
                <ul class="navbar-nav">
                    <li class="nav-item dropdown">
                        <a class="nav-link dropdown-toggle" href="#" id="userDropdown" role="button" data-bs-toggle="dropdown">
                            <i data-feather="user"></i> {{ current_user.username }}
                        </a>
                        <ul class="dropdown-menu">
                            <li><a class="dropdown-item" href="{{ url_for('auth.user_profile') }}"><i data-feather="settings"></i> Profile</a></li>
                            {% if current_user.is_admin %}
                            <li><a class="dropdown-item" href="{{ url_for('user_management.manage_users') }}"><i data-feather="users"></i> Manage Users</a></li>
                            {% endif %}
                            <li><hr class="dropdown-divider"></li>
                            <li><a class="dropdown-item" href="{{ url_for('auth.logout') }}"><i data-feather="log-out"></i> Logout</a></li>
                        </ul>
                    </li>
                </ul>
            </div>
            {% endif %}
        </div>
    </nav>
    
    <div class="container-fluid mt-4">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'danger' if category == 'error' else category }} alert-dismissible fade show">
                        {{ message }}
                        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
    </div>
    
    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    
    <!-- Feather Icons -->
    <script>
        feather.replace();
    </script>
    
    <!-- Custom JS -->
    <script src="{{ url_for('static', filename='js/main.js') }}"></script>
</body>
</html>
BASEHTML

# Update login.html with LUX branding
cat > templates/login.html << 'LOGINHTML'
{% extends "base.html" %}

{% block title %}Login - LUX Marketing{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6 col-lg-4">
        <div class="card">
            <div class="card-body">
                <h2 class="card-title text-center mb-4">
                    <i data-feather="mail"></i>
                    LUX Marketing
                </h2>
                
                <form method="POST">
                    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
                    <div class="mb-3">
                        <label for="username" class="form-label">Username</label>
                        <div class="input-group">
                            <span class="input-group-text">
                                <i data-feather="user"></i>
                            </span>
                            <input type="text" class="form-control" id="username" name="username" required autofocus>
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <label for="password" class="form-label">Password</label>
                        <div class="input-group">
                            <span class="input-group-text">
                                <i data-feather="lock"></i>
                            </span>
                            <input type="password" class="form-control" id="password" name="password" required>
                        </div>
                    </div>
                    
                    <div class="mb-3 form-check">
                        <input type="checkbox" class="form-check-input" id="remember" name="remember">
                        <label class="form-check-label" for="remember">Remember me</label>
                    </div>
                    
                    <button type="submit" class="btn btn-primary w-100">
                        <i data-feather="log-in"></i>
                        Login
                    </button>
                </form>
                
                <div class="text-center mt-3">
                    <a href="{{ url_for('auth.forgot_password') }}" class="text-decoration-none">
                        <small>Forgot your password?</small>
                    </a>
                </div>
                
                <div class="text-center mt-2">
                    <small class="text-muted">
                        Need to create an admin account? 
                        <a href="{{ url_for('auth.register') }}" class="text-decoration-none">Register here</a>
                    </small>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
LOGINHTML

echo "✅ Templates updated with LUX branding"

# Set permissions
chown -R luxapp:www-data /var/www/lux-marketing
chmod -R 755 /var/www/lux-marketing

# Restart service
systemctl start lux-marketing
systemctl restart nginx

echo "🎉 LUX Marketing branding applied!"
echo "Visit: http://lux.lucifercruz.com"

# Verify the update
echo "📋 Verification - Login template now contains:"
grep -i "LUX Marketing" /var/www/lux-marketing/templates/login.html || echo "❌ Update failed"
EOF

# Upload and run the update script on VPS
echo "📤 Uploading update script to VPS..."
scp update_files.sh $VPS_USER@$VPS_HOST:/tmp/

echo "🔄 Running update on VPS..."
ssh $VPS_USER@$VPS_HOST "chmod +x /tmp/update_files.sh && /tmp/update_files.sh"

# Cleanup
rm update_files.sh

echo ""
echo "🎉 VPS Updated with LUX Marketing Branding!"
echo "Visit: http://lux.lucifercruz.com"
echo ""
echo "The login page should now show 'LUX Marketing' instead of old branding"