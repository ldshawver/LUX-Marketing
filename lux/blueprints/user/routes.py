"""User management blueprint routes."""
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from lux.extensions import db
from lux.models.user import User
from lux.core.utils import validate_email

user_bp = Blueprint('user', __name__, template_folder='../../templates')


@user_bp.route('/profile')
@login_required
def profile():
    """User profile page."""
    return render_template('user_profile.html', user=current_user)


@user_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password."""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not all([current_password, new_password, confirm_password]):
            flash('All fields are required', 'error')
            return render_template('change_password.html')
        
        if not check_password_hash(current_user.password_hash, current_password):
            flash('Current password is incorrect', 'error')
            return render_template('change_password.html')
        
        if len(new_password) < 6:
            flash('New password must be at least 6 characters long', 'error')
            return render_template('change_password.html')
        
        if new_password != confirm_password:
            flash('New passwords do not match', 'error')
            return render_template('change_password.html')
        
        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        
        flash('Password updated successfully', 'success')
        return redirect(url_for('user.profile'))
    
    return render_template('change_password.html')


@user_bp.route('/manage-users')
@login_required
def manage_users():
    """Manage all users (admin function)."""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('manage_users.html', users=users)
