# start script :  python -m app.services.init_admin

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies.database import AsyncSessionLocal
from app.models.user import User
from app.models.mechanic import Mechanic
from app.utils.password import get_password_hash

async def create_initial_admin():
    """Create initial admin user if no admin exists"""
    async with AsyncSessionLocal() as db:
        try:
            # Check if admin exists in users table
            from sqlalchemy import select
            result = await db.execute(
                select(User).where(User.role == "admin")
            )
            admin_user = result.scalar_one_or_none()
            
            if admin_user:
                print("✅ Admin user already exists in users table")
                return
            
            # Create admin in users table
            admin_user = User(
                full_name="System Administrator",
                email="admin@example.com",
                hashed_password=get_password_hash("admin123"),
                role="admin",
                is_active=True
            )
            
            db.add(admin_user)
            await db.commit()
            await db.refresh(admin_user)
            
            print("✅ Initial admin user created successfully!")
            print(f"   Email: admin@example.com")
            print(f"   Password: admin123")
            print("   ⚠️  Please change the password after first login!")
            
        except Exception as e:
            print(f"❌ Error creating admin: {e}")
            await db.rollback()

async def create_initial_admin_mechanic():
    """Create initial admin mechanic if needed"""
    async with AsyncSessionLocal() as db:
        try:
            # Check if admin mechanic exists
            from sqlalchemy import select
            result = await db.execute(
                select(Mechanic).where(Mechanic.email == "mechanic@example.com")
            )
            admin_mechanic = result.scalar_one_or_none()
            
            if admin_mechanic:
                print("✅ Admin mechanic already exists")
                return
            
            # Create admin mechanic
            admin_mechanic = Mechanic(
                full_name="John Mechanic",
                email="mechanic@example.com",
                hashed_password=get_password_hash("mechanic123"),
                specialization="General Repair",
                is_active=True
            )
            
            db.add(admin_mechanic)
            await db.commit()
            await db.refresh(admin_mechanic)
            
            print("✅ Initial mechanic created successfully!")
            print(f"   Email: mechanic@example.com")
            print(f"   Password: mechanic123")
            print("   ⚠️  Please change the password after first login!")
            
        except Exception as e:
            print(f"❌ Error creating mechanic: {e}")
            await db.rollback()

def create_initial_admin_sync():
    """Synchronous wrapper for create_initial_admin"""
    asyncio.run(create_initial_admin())

def create_initial_admin_mechanic_sync():
    """Synchronous wrapper for create_initial_admin_mechanic"""
    asyncio.run(create_initial_admin_mechanic())

if __name__ == "__main__":
    print("🚀 Creating initial admin...")
    create_initial_admin_sync()
    print("\n🔧 Creating initial mechanic...")
    create_initial_admin_mechanic_sync()
    print("\n✅ Initialization complete!") 