"""
Database Backup & Restore Manager
Bi Tool v2.1 - Admin Export/Import functionality
"""

import sqlite3
import json
import os
import zipfile
import io
from datetime import datetime
from pathlib import Path
import shutil

class BackupManager:
    """Manage database backups and restores"""
    
    def __init__(self, db_path='email_tool.db', backup_dir='backups'):
        self.db_path = db_path
        self.backup_dir = backup_dir
        
        # Create backup directory if it doesn't exist
        Path(self.backup_dir).mkdir(parents=True, exist_ok=True)
    
    def create_full_backup(self, include_metadata=True):
        """
        Create a complete database backup
        
        Returns:
            dict: Backup information
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"bitool_backup_{timestamp}"
        
        # Connect to database
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        backup_data = {
            'metadata': {
                'backup_name': backup_name,
                'timestamp': timestamp,
                'datetime': datetime.now().isoformat(),
                'database': self.db_path,
                'version': '2.1'
            },
            'tables': {}
        }
        
        try:
            # Get all table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = cursor.fetchall()
            
            for table in tables:
                table_name = table['name']
                
                # Get table schema
                cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                schema = cursor.fetchone()
                
                # Get all data from table
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                
                # Convert rows to dictionaries
                data = []
                for row in rows:
                    data.append(dict(row))
                
                backup_data['tables'][table_name] = {
                    'schema': schema['sql'] if schema else None,
                    'row_count': len(data),
                    'data': data
                }
            
            conn.close()
            
            # Save as JSON
            json_path = os.path.join(self.backup_dir, f"{backup_name}.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            # Create ZIP file
            zip_path = os.path.join(self.backup_dir, f"{backup_name}.zip")
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(json_path, f"{backup_name}.json")
                # Also include the raw database file
                if os.path.exists(self.db_path):
                    zipf.write(self.db_path, 'email_tool.db')
            
            # Clean up JSON file (keep only ZIP)
            if os.path.exists(json_path):
                os.remove(json_path)
            
            file_size = os.path.getsize(zip_path)
            
            return {
                'success': True,
                'backup_name': backup_name,
                'file_path': zip_path,
                'file_size': file_size,
                'table_count': len(backup_data['tables']),
                'timestamp': timestamp
            }
            
        except Exception as e:
            conn.close()
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_table_backup(self, table_names):
        """
        Create backup of specific tables
        
        Args:
            table_names: List of table names to backup
            
        Returns:
            dict: Backup information
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"bitool_partial_{timestamp}"
        
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        backup_data = {
            'metadata': {
                'backup_name': backup_name,
                'timestamp': timestamp,
                'datetime': datetime.now().isoformat(),
                'backup_type': 'partial',
                'tables': table_names
            },
            'tables': {}
        }
        
        try:
            for table_name in table_names:
                # Check if table exists
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                if not cursor.fetchone():
                    continue
                
                # Get table schema
                cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                schema = cursor.fetchone()
                
                # Get all data
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                
                data = [dict(row) for row in rows]
                
                backup_data['tables'][table_name] = {
                    'schema': schema['sql'] if schema else None,
                    'row_count': len(data),
                    'data': data
                }
            
            conn.close()
            
            # Save as JSON
            json_path = os.path.join(self.backup_dir, f"{backup_name}.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            file_size = os.path.getsize(json_path)
            
            return {
                'success': True,
                'backup_name': backup_name,
                'file_path': json_path,
                'file_size': file_size,
                'table_count': len(backup_data['tables'])
            }
            
        except Exception as e:
            conn.close()
            return {
                'success': False,
                'error': str(e)
            }
    
    def restore_from_backup(self, backup_file, restore_mode='replace'):
        """
        Restore database from backup
        
        Args:
            backup_file: Path to backup file (.zip or .json)
            restore_mode: 'replace' (overwrite), 'merge' (add new), 'append' (add all)
            
        Returns:
            dict: Restore result
        """
        try:
            # Read backup data
            if backup_file.endswith('.zip'):
                with zipfile.ZipFile(backup_file, 'r') as zipf:
                    # Find JSON file in ZIP
                    json_files = [f for f in zipf.namelist() if f.endswith('.json')]
                    if not json_files:
                        return {'success': False, 'error': 'No JSON file found in backup'}
                    
                    with zipf.open(json_files[0]) as f:
                        backup_data = json.load(f)
            else:
                with open(backup_file, 'r', encoding='utf-8') as f:
                    backup_data = json.load(f)
            
            # Connect to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            restored_tables = {}
            
            for table_name, table_data in backup_data.get('tables', {}).items():
                try:
                    if restore_mode == 'replace':
                        # Drop existing table
                        cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                        
                        # Recreate table
                        if table_data.get('schema'):
                            cursor.execute(table_data['schema'])
                    
                    elif restore_mode == 'merge':
                        # Create table if it doesn't exist
                        if table_data.get('schema'):
                            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                            if not cursor.fetchone():
                                cursor.execute(table_data['schema'])
                    
                    # Insert data
                    rows_inserted = 0
                    for row_data in table_data.get('data', []):
                        if not row_data:
                            continue
                        
                        columns = list(row_data.keys())
                        values = list(row_data.values())
                        
                        placeholders = ','.join(['?' for _ in columns])
                        columns_str = ','.join(columns)
                        
                        if restore_mode == 'merge':
                            # Use INSERT OR IGNORE for merge mode
                            sql = f"INSERT OR IGNORE INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                        else:
                            sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                        
                        try:
                            cursor.execute(sql, values)
                            rows_inserted += 1
                        except sqlite3.IntegrityError:
                            # Skip duplicate entries in merge mode
                            if restore_mode != 'merge':
                                raise
                    
                    restored_tables[table_name] = {
                        'rows_inserted': rows_inserted,
                        'total_rows': len(table_data.get('data', []))
                    }
                    
                except Exception as e:
                    restored_tables[table_name] = {
                        'error': str(e)
                    }
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'restored_tables': restored_tables,
                'restore_mode': restore_mode,
                'backup_info': backup_data.get('metadata', {})
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def list_backups(self):
        """
        List all available backups
        
        Returns:
            list: Backup files information
        """
        backups = []
        
        if not os.path.exists(self.backup_dir):
            return backups
        
        for filename in os.listdir(self.backup_dir):
            if filename.endswith(('.zip', '.json')):
                file_path = os.path.join(self.backup_dir, filename)
                file_size = os.path.getsize(file_path)
                file_mtime = os.path.getmtime(file_path)
                
                backups.append({
                    'filename': filename,
                    'file_path': file_path,
                    'file_size': file_size,
                    'created_at': datetime.fromtimestamp(file_mtime).isoformat(),
                    'file_type': 'zip' if filename.endswith('.zip') else 'json'
                })
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x['created_at'], reverse=True)
        
        return backups
    
    def delete_backup(self, filename):
        """
        Delete a backup file
        
        Args:
            filename: Backup filename
            
        Returns:
            bool: Success status
        """
        try:
            file_path = os.path.join(self.backup_dir, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False
    
    def export_as_json(self, table_names=None):
        """
        Export database as JSON (for API response)
        
        Args:
            table_names: List of tables to export (None = all tables)
            
        Returns:
            dict: Export data
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        export_data = {
            'metadata': {
                'exported_at': datetime.now().isoformat(),
                'version': '2.1'
            },
            'data': {}
        }
        
        try:
            if table_names is None:
                # Export all tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
                table_names = [row['name'] for row in cursor.fetchall()]
            
            for table_name in table_names:
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                export_data['data'][table_name] = [dict(row) for row in rows]
            
            conn.close()
            return export_data
            
        except Exception as e:
            conn.close()
            raise e
    
    def import_from_json(self, json_data, table_name, mode='append'):
        """
        Import data from JSON
        
        Args:
            json_data: List of dictionaries (rows)
            table_name: Target table name
            mode: 'append', 'replace', 'merge'
            
        Returns:
            dict: Import result
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if mode == 'replace':
                cursor.execute(f"DELETE FROM {table_name}")
            
            rows_inserted = 0
            errors = []
            
            for row_data in json_data:
                if not row_data:
                    continue
                
                columns = list(row_data.keys())
                values = list(row_data.values())
                
                placeholders = ','.join(['?' for _ in columns])
                columns_str = ','.join(columns)
                
                if mode == 'merge':
                    sql = f"INSERT OR REPLACE INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                else:
                    sql = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
                
                try:
                    cursor.execute(sql, values)
                    rows_inserted += 1
                except Exception as e:
                    errors.append(str(e))
            
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'rows_inserted': rows_inserted,
                'total_rows': len(json_data),
                'errors': errors if errors else None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_database_stats(self):
        """
        Get database statistics
        
        Returns:
            dict: Database statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = cursor.fetchall()
            
            stats = {
                'database_file': self.db_path,
                'database_size': os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0,
                'table_count': len(tables),
                'tables': {}
            }
            
            total_rows = 0
            
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                total_rows += row_count
                
                # Get table info
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                
                stats['tables'][table_name] = {
                    'row_count': row_count,
                    'column_count': len(columns),
                    'columns': [col[1] for col in columns]  # Column names
                }
            
            stats['total_rows'] = total_rows
            
            conn.close()
            
            return stats
            
        except Exception as e:
            return {
                'error': str(e)
            }

# Global backup manager instance
backup_manager = BackupManager()
