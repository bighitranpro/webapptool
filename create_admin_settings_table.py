"""
Migration script to create admin_settings table
"""
import sqlite3
import json
from datetime import datetime

def create_admin_settings_table():
    conn = sqlite3.connect('email_tool.db')
    cursor = conn.cursor()
    
    # Create admin_settings table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            theme_config TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Create index
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_admin_settings_user_id 
        ON admin_settings(user_id)
    ''')
    
    # Insert default theme for admin (user_id=1)
    default_theme = {
        "theme_mode": "dark",
        "primary_color": "#ffd700",
        "secondary_color": "#00d9ff",
        "accent_color": "#ff6b35",
        "background_color": "#0a0e27",
        "text_color": "#ffffff",
        "font_family": "Inter",
        "font_size_base": "16px",
        "sidebar_width": "280px",
        "border_radius": "12px",
        "animation_speed": "0.3s"
    }
    
    try:
        cursor.execute('''
            INSERT INTO admin_settings (user_id, theme_config)
            VALUES (?, ?)
        ''', (1, json.dumps(default_theme)))
        print("✅ Inserted default theme for admin")
    except sqlite3.IntegrityError:
        print("ℹ️  Default theme already exists")
    
    conn.commit()
    conn.close()
    print("✅ Admin settings table created successfully")

if __name__ == "__main__":
    create_admin_settings_table()
