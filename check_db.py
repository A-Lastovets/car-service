import asyncio
import sqlite3
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.future import select
from app.models.mechanic import Mechanic
from app.models.user import User

async def check_database():
    # Check SQLite database directly
    print("=== Checking SQLite database directly ===")
    conn = sqlite3.connect('car_service.db')
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in database:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Check mechanics table
    print("\n=== Mechanics table structure ===")
    cursor.execute("PRAGMA table_info(mechanics);")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Check mechanics data
    print("\n=== Mechanics data ===")
    cursor.execute("SELECT * FROM mechanics;")
    mechanics = cursor.fetchall()
    for mechanic in mechanics:
        print(f"  {mechanic}")
    
    # Check users table
    print("\n=== Users table structure ===")
    cursor.execute("PRAGMA table_info(users);")
    columns = cursor.fetchall()
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
    
    # Check users data
    print("\n=== Users data ===")
    cursor.execute("SELECT * FROM users;")
    users = cursor.fetchall()
    for user in users:
        print(f"  {user}")
    
    conn.close()
    
    # Check with SQLAlchemy async
    print("\n=== Checking with SQLAlchemy async ===")
    engine = create_async_engine("sqlite+aiosqlite:///./car_service.db")
    
    async with engine.begin() as conn:
        # Check mechanics
        result = await conn.execute(select(Mechanic))
        mechanics = result.scalars().all()
        print(f"Found {len(mechanics)} mechanics:")
        for mechanic in mechanics:
            print(f"  ID: {mechanic.id}, Email: {mechanic.email}, Name: {mechanic.full_name}")
        
        # Check users
        result = await conn.execute(select(User))
        users = result.scalars().all()
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"  ID: {user.id}, Email: {user.email}, Name: {user.full_name}, Role: {user.role}")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_database()) 