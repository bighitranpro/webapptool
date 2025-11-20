"""
Database Module
SQLite database for storing email validation results and history
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import json
import os


class Database:
    """Database management for Email Tool Pro"""
    
    def __init__(self, db_path: str = 'email_tool.db'):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Table: validation_results
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS validation_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                status TEXT NOT NULL,
                confidence INTEGER,
                has_mx BOOLEAN,
                smtp_reachable BOOLEAN,
                is_disposable BOOLEAN,
                fb_compatible BOOLEAN,
                can_receive_code BOOLEAN,
                details TEXT,
                mx_records TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Index for faster email lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_email 
            ON validation_results(email)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_status 
            ON validation_results(status)
        ''')
        
        # Table: validation_sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS validation_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total_emails INTEGER,
                live_count INTEGER,
                die_count INTEGER,
                unknown_count INTEGER,
                can_receive_code_count INTEGER,
                processing_time REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table: generated_emails
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS generated_emails (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                email_type TEXT,
                domain TEXT,
                char_type TEXT,
                number_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table: email_lists
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_lists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                description TEXT,
                email_count INTEGER,
                emails TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Table: statistics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stat_type TEXT NOT NULL,
                stat_key TEXT NOT NULL,
                stat_value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print(f"✅ Database initialized: {self.db_path}")
    
    def save_validation_result(self, result: Dict) -> int:
        """Save email validation result"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO validation_results 
            (email, status, confidence, has_mx, smtp_reachable, is_disposable, 
             fb_compatible, can_receive_code, details, mx_records)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            result.get('email'),
            result.get('status'),
            result.get('confidence'),
            result.get('has_mx'),
            result.get('smtp_reachable'),
            result.get('is_disposable'),
            result.get('fb_compatible'),
            result.get('can_receive_code'),
            json.dumps(result.get('details', [])),
            json.dumps(result.get('mx_records', []))
        ))
        
        result_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return result_id
    
    def save_validation_session(self, stats: Dict) -> int:
        """Save validation session statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO validation_sessions 
            (total_emails, live_count, die_count, unknown_count, 
             can_receive_code_count, processing_time)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            stats.get('total', 0),
            stats.get('live', 0),
            stats.get('die', 0),
            stats.get('unknown', 0),
            stats.get('can_receive_code', 0),
            stats.get('processing_time', 0)
        ))
        
        session_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return session_id
    
    def get_validation_result(self, email: str) -> Optional[Dict]:
        """Get cached validation result for email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM validation_results 
            WHERE email = ? 
            ORDER BY created_at DESC 
            LIMIT 1
        ''', (email,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            columns = [desc[0] for desc in cursor.description]
            result = dict(zip(columns, row))
            
            # Parse JSON fields
            if result.get('details'):
                result['details'] = json.loads(result['details'])
            if result.get('mx_records'):
                result['mx_records'] = json.loads(result['mx_records'])
            
            return result
        
        return None
    
    def get_live_emails(self, limit: int = 100) -> List[Dict]:
        """Get LIVE emails from database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT email, confidence, fb_compatible, can_receive_code, created_at
            FROM validation_results 
            WHERE status = 'LIVE' 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                'email': row[0],
                'confidence': row[1],
                'fb_compatible': row[2],
                'can_receive_code': row[3],
                'created_at': row[4]
            })
        
        return results
    
    def get_die_emails(self, limit: int = 100) -> List[Dict]:
        """Get DIE emails from database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT email, details, created_at
            FROM validation_results 
            WHERE status = 'DIE' 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            details = json.loads(row[1]) if row[1] else []
            results.append({
                'email': row[0],
                'details': details,
                'created_at': row[2]
            })
        
        return results
    
    def get_statistics(self) -> Dict:
        """Get overall statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total validations
        cursor.execute('SELECT COUNT(*) FROM validation_results')
        total = cursor.fetchone()[0]
        
        # LIVE count
        cursor.execute("SELECT COUNT(*) FROM validation_results WHERE status = 'LIVE'")
        live = cursor.fetchone()[0]
        
        # DIE count
        cursor.execute("SELECT COUNT(*) FROM validation_results WHERE status = 'DIE'")
        die = cursor.fetchone()[0]
        
        # UNKNOWN count
        cursor.execute("SELECT COUNT(*) FROM validation_results WHERE status = 'UNKNOWN'")
        unknown = cursor.fetchone()[0]
        
        # Can receive code
        cursor.execute("SELECT COUNT(*) FROM validation_results WHERE can_receive_code = 1")
        can_receive = cursor.fetchone()[0]
        
        # Total sessions
        cursor.execute('SELECT COUNT(*) FROM validation_sessions')
        sessions = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total': total,
            'live': live,
            'die': die,
            'unknown': unknown,
            'can_receive_code': can_receive,
            'cannot_receive_code': total - can_receive,
            'sessions': sessions,
            'live_rate': round((live / total * 100) if total > 0 else 0, 2),
            'die_rate': round((die / total * 100) if total > 0 else 0, 2)
        }
    
    def save_generated_email(self, email: str, params: Dict) -> int:
        """Save generated email"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO generated_emails 
            (email, email_type, domain, char_type, number_type)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            email,
            params.get('email_type'),
            params.get('domain'),
            params.get('char_type'),
            params.get('number_type')
        ))
        
        email_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return email_id
    
    def save_email_list(self, name: str, emails: List[str], description: str = '') -> int:
        """Save email list"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO email_lists 
            (name, description, email_count, emails)
            VALUES (?, ?, ?, ?)
        ''', (
            name,
            description,
            len(emails),
            json.dumps(emails)
        ))
        
        list_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return list_id
    
    def get_email_lists(self) -> List[Dict]:
        """Get all saved email lists"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, description, email_count, created_at
            FROM email_lists 
            ORDER BY created_at DESC
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'email_count': row[3],
                'created_at': row[4]
            })
        
        return results
    
    def get_email_list(self, list_id: int) -> Optional[Dict]:
        """Get specific email list"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM email_lists WHERE id = ?
        ''', (list_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'email_count': row[3],
                'emails': json.loads(row[4]),
                'created_at': row[5]
            }
        
        return None
    
    def clear_old_data(self, days: int = 30):
        """Clear data older than specified days"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM validation_results 
            WHERE created_at < datetime('now', '-' || ? || ' days')
        ''', (days,))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted
    
    def get_recent_validations(self, limit: int = 50) -> List[Dict]:
        """Get recent validation results"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT email, status, confidence, can_receive_code, created_at
            FROM validation_results 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                'email': row[0],
                'status': row[1],
                'confidence': row[2],
                'can_receive_code': row[3],
                'created_at': row[4]
            })
        
        return results
    
    def search_emails(self, query: str) -> List[Dict]:
        """Search emails in database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT email, status, confidence, can_receive_code, created_at
            FROM validation_results 
            WHERE email LIKE ? 
            ORDER BY created_at DESC 
            LIMIT 100
        ''', (f'%{query}%',))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                'email': row[0],
                'status': row[1],
                'confidence': row[2],
                'can_receive_code': row[3],
                'created_at': row[4]
            })
        
        return results


# Global database instance
db = Database()


if __name__ == '__main__':
    # Test database
    print("Testing database...")
    
    # Test save validation result
    test_result = {
        'email': 'test@gmail.com',
        'status': 'LIVE',
        'confidence': 80,
        'has_mx': True,
        'smtp_reachable': True,
        'is_disposable': False,
        'fb_compatible': True,
        'can_receive_code': True,
        'details': ['MX records found', 'SMTP reachable'],
        'mx_records': ['smtp.gmail.com']
    }
    
    result_id = db.save_validation_result(test_result)
    print(f"✅ Saved validation result: {result_id}")
    
    # Test get statistics
    stats = db.get_statistics()
    print(f"✅ Statistics: {stats}")
    
    # Test get LIVE emails
    live_emails = db.get_live_emails(10)
    print(f"✅ LIVE emails: {len(live_emails)}")
    
    print("\n✅ Database is working perfectly!")
