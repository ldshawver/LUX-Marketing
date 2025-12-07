"""
Migration script for shared company architecture.
This script:
1. Creates the user_company_access table if it doesn't exist
2. Adds default_company_id column to users table if it doesn't exist
3. Backfills existing user-company relationships into UserCompanyAccess
4. Gives all existing users access to all companies as 'viewer' (admin users get 'admin' role)
5. Sets first company as default for users without a default
"""

from app import app, db
from models import User, Company, UserCompanyAccess, user_company
from sqlalchemy import text, inspect


def migrate():
    with app.app_context():
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        print("Starting shared company migration...")
        
        if 'user_company_access' not in existing_tables:
            print("Creating user_company_access table...")
            db.create_all()
            print("Table created successfully")
        else:
            print("user_company_access table already exists")
        
        user_columns = [col['name'] for col in inspector.get_columns('user')]
        if 'default_company_id' not in user_columns:
            print("Adding default_company_id column to users...")
            try:
                db.session.execute(text(
                    "ALTER TABLE \"user\" ADD COLUMN default_company_id INTEGER REFERENCES company(id)"
                ))
                db.session.commit()
                print("Column added successfully")
            except Exception as e:
                db.session.rollback()
                print(f"Column may already exist: {e}")
        else:
            print("default_company_id column already exists")
        
        print("\nBackfilling user-company access records...")
        
        all_users = User.query.all()
        all_companies = Company.query.filter_by(is_active=True).all()
        
        print(f"Found {len(all_users)} users and {len(all_companies)} companies")
        
        existing_access = db.session.execute(
            db.select(user_company)
        ).fetchall()
        
        existing_map = {}
        for record in existing_access:
            key = (record.user_id, record.company_id)
            existing_map[key] = record.is_default
        
        created_count = 0
        for user in all_users:
            for company in all_companies:
                existing = UserCompanyAccess.query.filter_by(
                    user_id=user.id,
                    company_id=company.id
                ).first()
                
                if not existing:
                    if user.is_admin:
                        role = 'admin'
                    elif (user.id, company.id) in existing_map:
                        role = 'editor'
                    else:
                        role = 'viewer'
                    
                    is_default = existing_map.get((user.id, company.id), False)
                    
                    access = UserCompanyAccess(
                        user_id=user.id,
                        company_id=company.id,
                        role=role,
                        is_default=is_default
                    )
                    db.session.add(access)
                    created_count += 1
        
        if created_count > 0:
            db.session.commit()
            print(f"Created {created_count} access records")
        else:
            print("No new access records needed")
        
        print("\nSetting default companies for users without one...")
        updated_count = 0
        for user in all_users:
            if not user.default_company_id and all_companies:
                default_access = UserCompanyAccess.query.filter_by(
                    user_id=user.id,
                    is_default=True
                ).first()
                
                if default_access:
                    user.default_company_id = default_access.company_id
                else:
                    user.default_company_id = all_companies[0].id
                updated_count += 1
        
        if updated_count > 0:
            db.session.commit()
            print(f"Set default company for {updated_count} users")
        else:
            print("All users already have default companies")
        
        print("\n=== Migration Complete ===")
        print(f"Total users: {len(all_users)}")
        print(f"Total companies: {len(all_companies)}")
        print(f"Total access records: {UserCompanyAccess.query.count()}")


if __name__ == '__main__':
    migrate()
