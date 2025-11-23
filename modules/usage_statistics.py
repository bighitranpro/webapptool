"""
Usage Statistics Module
Track and analyze application usage
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List
from database import Database


class UsageStatistics:
    """Track application usage statistics"""
    
    def __init__(self):
        self.db = Database()
        self._ensure_tables()
    
    def _ensure_tables(self):
        """Create statistics tables"""
        query = """
        CREATE TABLE IF NOT EXISTS usage_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action_type TEXT,
            action_data TEXT,
            timestamp TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
        self.db.execute_query(query)
    
    def log_action(self, user_id: int, action_type: str, action_data: Dict = None):
        """Log user action"""
        query = "INSERT INTO usage_stats (user_id, action_type, action_data, timestamp) VALUES (?, ?, ?, ?)"
        self.db.execute_query(query, (
            user_id,
            action_type,
            json.dumps(action_data or {}),
            datetime.now().isoformat()
        ))
    
    def get_stats(self, user_id: int = None, days: int = 30) -> Dict:
        """Get usage statistics"""
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        query = """
        SELECT action_type, COUNT(*) as count
        FROM usage_stats
        WHERE timestamp >= ? AND (? IS NULL OR user_id = ?)
        GROUP BY action_type
        """
        
        results = self.db.fetch_all(query, (start_date, user_id, user_id))
        
        return {
            'success': True,
            'period_days': days,
            'stats': [{'action': r[0], 'count': r[1]} for r in results]
        }


def get_usage_statistics():
    return UsageStatistics()
