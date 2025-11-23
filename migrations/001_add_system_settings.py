#!/usr/bin/env python3
"""
Migration: Add System Settings columns
Purpose: Add comprehensive system settings to system_settings table
Author: BIGHI Tool MMO
Date: 2024-11-23
"""

import sqlite3
import sys
from pathlib import Path

def run_migration(db_path: str = 'email_tool.db'):
    """Run the migration to add system settings columns"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # List of columns to add with their types and defaults
    columns_to_add = [
        # General Settings
        ("tool_name", "TEXT DEFAULT 'BIGHI Tool MMO'"),
        ("tool_description", "TEXT DEFAULT 'Professional Email & Facebook Tools Platform'"),
        ("logo_url", "TEXT"),
        ("favicon_url", "TEXT"),
        ("company_name", "TEXT DEFAULT 'BIGHI Agency'"),
        ("company_website", "TEXT DEFAULT 'https://bighi.agency'"),
        ("support_email", "TEXT DEFAULT 'support@bighi.agency'"),
        ("support_phone", "TEXT DEFAULT '+84 123 456 789'"),
        
        # Email Generator Settings
        ("default_email_count", "INTEGER DEFAULT 10"),
        ("max_email_count", "INTEGER DEFAULT 1000"),
        ("default_locale", "TEXT DEFAULT 'vi'"),
        ("default_persona", "TEXT DEFAULT 'personal'"),
        
        # Domain Settings
        ("allowed_domains", "TEXT DEFAULT 'gmail.com,yahoo.com,outlook.com'"),
        ("custom_domains", "TEXT"),
        
        # Generator Configuration
        ("generator_config", "TEXT"),  # JSON configuration
        
        # SMTP Settings
        ("smtp_host", "TEXT"),
        ("smtp_port", "INTEGER DEFAULT 587"),
        ("smtp_user", "TEXT"),
        ("smtp_password", "TEXT"),
        ("smtp_use_tls", "INTEGER DEFAULT 1"),
        
        # Notification Settings
        ("enable_email_notifications", "INTEGER DEFAULT 1"),
    ]
    
    try:
        # Check if system_settings table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='system_settings'
        """)
        
        if not cursor.fetchone():
            print("❌ Error: system_settings table does not exist")
            print("Please create the table first")
            return False
        
        # Get existing columns
        cursor.execute("PRAGMA table_info(system_settings)")
        existing_columns = {row[1] for row in cursor.fetchall()}
        
        added_count = 0
        skipped_count = 0
        
        # Add each column if it doesn't exist
        for column_name, column_definition in columns_to_add:
            if column_name not in existing_columns:
                try:
                    sql = f"ALTER TABLE system_settings ADD COLUMN {column_name} {column_definition}"
                    cursor.execute(sql)
                    print(f"✅ Added column: {column_name}")
                    added_count += 1
                except sqlite3.Error as e:
                    print(f"⚠️  Warning: Could not add {column_name}: {e}")
            else:
                print(f"⏭️  Skipped (already exists): {column_name}")
                skipped_count += 1
        
        conn.commit()
        
        # Insert default settings if no rows exist
        cursor.execute("SELECT COUNT(*) FROM system_settings")
        count = cursor.fetchone()[0]
        if count == 0:
            # Get column names (excluding auto-increment id if exists)
            cursor.execute("PRAGMA table_info(system_settings)")
            cols = cursor.fetchall()
            has_id = any(col[1] == 'id' for col in cols)
            
            if has_id:
                cursor.execute("INSERT INTO system_settings DEFAULT VALUES")
            else:
                # Just commit the alterations
                pass
            conn.commit()
            print("✅ Ensured default settings row exists")
        
        print(f"\n🎉 Migration completed successfully!")
        print(f"   - Added: {added_count} columns")
        print(f"   - Skipped: {skipped_count} columns (already exist)")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()

def verify_migration(db_path: str = 'email_tool.db'):
    """Verify the migration was successful"""
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        cursor.execute("PRAGMA table_info(system_settings)")
        columns = cursor.fetchall()
        
        print(f"\n📊 Current system_settings columns ({len(columns)} total):")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Verification failed: {e}")
        return False
        
    finally:
        conn.close()

if __name__ == '__main__':
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'email_tool.db'
    
    print("=" * 60)
    print("🔄 Running Migration: 001_add_system_settings")
    print("=" * 60)
    
    if run_migration(db_path):
        verify_migration(db_path)
        sys.exit(0)
    else:
        sys.exit(1)
