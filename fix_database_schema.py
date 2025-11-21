"""
Database Schema Migration Script
Adds missing VIP columns to users table
"""

import sqlite3
from datetime import datetime

def migrate_database():
    """Add missing VIP columns to users table"""
    conn = sqlite3.connect('email_tool.db')
    cursor = conn.cursor()
    
    print("🔧 Starting database migration...")
    
    # Check current schema
    cursor.execute("PRAGMA table_info(users)")
    existing_columns = [col[1] for col in cursor.fetchall()]
    print(f"📋 Existing columns: {existing_columns}")
    
    # Define columns to add
    columns_to_add = [
        ("vip_level", "INTEGER DEFAULT 0"),
        ("vip_expiry", "TIMESTAMP"),
        ("subscription_start", "TIMESTAMP"),
        ("total_validations", "INTEGER DEFAULT 0"),
        ("total_generations", "INTEGER DEFAULT 0"),
        ("daily_validations", "INTEGER DEFAULT 0"),
        ("daily_generations", "INTEGER DEFAULT 0"),
        ("last_reset_date", "TEXT")
    ]
    
    # Add missing columns
    for col_name, col_type in columns_to_add:
        if col_name not in existing_columns:
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
                print(f"✅ Added column: {col_name}")
            except sqlite3.OperationalError as e:
                print(f"⚠️  Column {col_name} might already exist: {e}")
    
    # Update existing admin user with VIP Enterprise level
    try:
        cursor.execute("""
            UPDATE users 
            SET vip_level = 3,
                vip_expiry = datetime('now', '+365 days'),
                subscription_start = datetime('now')
            WHERE username = 'admin'
        """)
        print("✅ Updated admin user with Enterprise VIP")
    except Exception as e:
        print(f"⚠️  Error updating admin: {e}")
    
    # Update all existing users to FREE tier if not set
    try:
        cursor.execute("""
            UPDATE users 
            SET vip_level = 0,
                vip_expiry = datetime('now', '+365 days'),
                subscription_start = datetime('now')
            WHERE vip_level IS NULL
        """)
        print("✅ Set FREE tier for existing users")
    except Exception as e:
        print(f"⚠️  Error updating users: {e}")
    
    conn.commit()
    
    # Verify changes
    cursor.execute("PRAGMA table_info(users)")
    new_columns = cursor.fetchall()
    print("\n📋 Updated schema:")
    for col in new_columns:
        print(f"  - {col[1]} ({col[2]})")
    
    conn.close()
    print("\n✅ Database migration completed!")

if __name__ == '__main__':
    migrate_database()
