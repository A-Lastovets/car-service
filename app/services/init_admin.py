# start script :  python -m app.services.init_admin

import asyncio
from sqlalchemy.orm import Session
from app.dependencies.database import SessionLocal
from app.models.user import User
from app.models.mechanic import Mechanic
from app.utils.password import get_password_hash

def create_initial_admin():
    """Create initial admin user if no admin exists"""
    db = SessionLocal()
    
    try:
        # Check if admin exists in users table
        admin_user = db.query(User).filter(User.role == "admin").first()
        if admin_user:
            print("✅ Admin user already exists in users table")
            return
        
        # Check if admin exists in mechanics table
        admin_mechanic = db.query(Mechanic).filter(Mechanic.role == "admin").first()
        if admin_mechanic:
            print("✅ Admin mechanic already exists in mechanics table")
            return
        
        # Create admin in users table (recommended)
        admin_user = User(
            name="Admin",
            email="admin@car-service.com",
            password=get_password_hash("admin123!"),
            role="admin"
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("✅ Initial admin user created successfully!")
        print(f"   Email: admin@car-service.com")
        print(f"   Password: admin123!")
        print("   ⚠️  Please change the password after first login!")
        
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
        db.rollback()
    finally:
        db.close()

def create_initial_admin_mechanic():
    """Create initial admin mechanic if needed"""
    db = SessionLocal()
    
    try:
        # Check if admin mechanic exists
        admin_mechanic = db.query(Mechanic).filter(Mechanic.role == "admin").first()
        if admin_mechanic:
            print("✅ Admin mechanic already exists")
            return
        
        # Create admin mechanic
        admin_mechanic = Mechanic(
            name="Admin Mechanic",
            birth_date="1990-01-01",  # Default date
            login="admin_mechanic",
            password=get_password_hash("admin123!"),
            role="admin",
            position="Head Mechanic"
        )
        
        db.add(admin_mechanic)
        db.commit()
        db.refresh(admin_mechanic)
        
        print("✅ Initial admin mechanic created successfully!")
        print(f"   Login: admin_mechanic")
        print(f"   Password: admin123!")
        print("   ⚠️  Please change the password after first login!")
        
    except Exception as e:
        print(f"❌ Error creating admin mechanic: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Creating initial admin...")
    create_initial_admin()
    print("\n🔧 Creating initial admin mechanic...")
    create_initial_admin_mechanic()
    print("\n✅ Initialization complete!") 