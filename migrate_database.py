#!/usr/bin/env python3
"""
Simple database migration script for LUX Email Marketing App
Adds missing columns to existing database
"""

import os
import sqlite3
from app import app, db
from models import User

def migrate_database():
    """Add missing columns to existing database"""
    print("🔄 Starting database migration...")
    
    with app.app_context():
        # Check if we're using SQLite
        db_url = app.config["SQLALCHEMY_DATABASE_URI"]
        if db_url.startswith('sqlite'):
            # Extract SQLite database path
            db_path = db_url.replace('sqlite:///', '')
            
            # Connect directly to SQLite to add missing columns
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            try:
                # Check if is_admin column exists
                cursor.execute("PRAGMA table_info(user)")
                columns = [column[1] for column in cursor.fetchall()]
                
                if 'is_admin' not in columns:
                    print("➕ Adding is_admin column to user table...")
                    cursor.execute("ALTER TABLE user ADD COLUMN is_admin BOOLEAN DEFAULT 0")
                    
                    # Update admin user to be admin
                    cursor.execute("UPDATE user SET is_admin = 1 WHERE username = 'admin'")
                    print("✅ Admin user updated with admin privileges")
                
                conn.commit()
                print("✅ Database migration completed successfully!")
                
            except Exception as e:
                print(f"❌ Error during migration: {e}")
                conn.rollback()
                return False
            finally:
                conn.close()
        
        else:
            # For PostgreSQL or other databases, use SQLAlchemy
            try:
                # Try to create all tables (this will add missing columns)
                db.create_all()
                print("✅ Database tables updated successfully!")
                
                # Update admin user
                admin = User.query.filter_by(username='admin').first()
                if admin:
                    admin.is_admin = True
                    db.session.commit()
                    print("✅ Admin user updated with admin privileges")
                
            except Exception as e:
                print(f"❌ Error during PostgreSQL migration: {e}")
                return False
    
    return True

if __name__ == "__main__":
    migrate_database()