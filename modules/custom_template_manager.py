"""
Custom Template Manager
Allows users to create, edit, delete custom email templates
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from database import Database


class CustomTemplateManager:
    """
    Manage custom user-created email templates
    """
    
    def __init__(self):
        self.db = Database()
        self._ensure_table()
    
    def _ensure_table(self):
        """Create custom_templates table if not exists"""
        query = """
        CREATE TABLE IF NOT EXISTS custom_templates (
            id TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT,
            pattern TEXT NOT NULL,
            variables TEXT,
            tags TEXT,
            examples TEXT,
            created_at TEXT,
            updated_at TEXT,
            is_public INTEGER DEFAULT 0,
            usage_count INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
        self.db.execute_query(query)
    
    def create_template(
        self,
        user_id: int,
        name: str,
        pattern: str,
        description: str = '',
        category: str = 'custom',
        variables: List[str] = None,
        tags: List[str] = None,
        examples: List[str] = None,
        is_public: bool = False
    ) -> Dict:
        """
        Create a new custom template
        
        Args:
            user_id: ID of user creating template
            name: Template name
            pattern: Email pattern (e.g., "{firstname}.{lastname}@{domain}")
            description: Template description
            category: Category (default: custom)
            variables: List of variable names
            tags: List of tags
            examples: Example emails
            is_public: Make template public for all users
        
        Returns:
            dict: Created template info
        """
        template_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        # Auto-detect variables from pattern if not provided
        if variables is None:
            import re
            variables = re.findall(r'\{(\w+)\}', pattern)
        
        query = """
        INSERT INTO custom_templates 
        (id, user_id, name, description, category, pattern, variables, tags, examples, created_at, updated_at, is_public)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        self.db.execute_query(query, (
            template_id,
            user_id,
            name,
            description,
            category,
            pattern,
            json.dumps(variables),
            json.dumps(tags or []),
            json.dumps(examples or []),
            now,
            now,
            1 if is_public else 0
        ))
        
        return {
            'success': True,
            'template_id': template_id,
            'message': 'Template created successfully'
        }
    
    def get_template(self, template_id: str, user_id: Optional[int] = None) -> Optional[Dict]:
        """
        Get template by ID
        
        Args:
            template_id: Template ID
            user_id: Optional user ID for permission check
        
        Returns:
            dict: Template data or None
        """
        query = """
        SELECT * FROM custom_templates 
        WHERE id = ? AND (is_public = 1 OR user_id = ?)
        """
        
        result = self.db.fetch_one(query, (template_id, user_id or 0))
        
        if result:
            return self._format_template(result)
        return None
    
    def list_templates(self, user_id: Optional[int] = None, category: Optional[str] = None) -> List[Dict]:
        """
        List all accessible templates for user
        
        Args:
            user_id: User ID (optional)
            category: Filter by category (optional)
        
        Returns:
            list: List of templates
        """
        query = """
        SELECT * FROM custom_templates 
        WHERE (is_public = 1 OR user_id = ?)
        """
        params = [user_id or 0]
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY created_at DESC"
        
        results = self.db.fetch_all(query, tuple(params))
        
        return [self._format_template(r) for r in results]
    
    def update_template(
        self,
        template_id: str,
        user_id: int,
        updates: Dict
    ) -> Dict:
        """
        Update template (only owner can update)
        
        Args:
            template_id: Template ID
            user_id: User ID
            updates: Dict of fields to update
        
        Returns:
            dict: Update result
        """
        # Check ownership
        template = self.get_template(template_id)
        if not template or template['user_id'] != user_id:
            return {
                'success': False,
                'message': 'Template not found or access denied'
            }
        
        # Build update query
        allowed_fields = ['name', 'description', 'category', 'pattern', 'variables', 'tags', 'examples', 'is_public']
        update_fields = []
        params = []
        
        for field, value in updates.items():
            if field in allowed_fields:
                if field in ['variables', 'tags', 'examples']:
                    value = json.dumps(value)
                elif field == 'is_public':
                    value = 1 if value else 0
                
                update_fields.append(f"{field} = ?")
                params.append(value)
        
        if not update_fields:
            return {
                'success': False,
                'message': 'No valid fields to update'
            }
        
        # Add updated_at
        update_fields.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        
        # Add template_id
        params.append(template_id)
        
        query = f"""
        UPDATE custom_templates 
        SET {', '.join(update_fields)}
        WHERE id = ?
        """
        
        self.db.execute_query(query, tuple(params))
        
        return {
            'success': True,
            'message': 'Template updated successfully'
        }
    
    def delete_template(self, template_id: str, user_id: int) -> Dict:
        """
        Delete template (only owner can delete)
        
        Args:
            template_id: Template ID
            user_id: User ID
        
        Returns:
            dict: Delete result
        """
        # Check ownership
        template = self.get_template(template_id)
        if not template or template['user_id'] != user_id:
            return {
                'success': False,
                'message': 'Template not found or access denied'
            }
        
        query = "DELETE FROM custom_templates WHERE id = ?"
        self.db.execute_query(query, (template_id,))
        
        return {
            'success': True,
            'message': 'Template deleted successfully'
        }
    
    def increment_usage(self, template_id: str):
        """Increment usage count for template"""
        query = "UPDATE custom_templates SET usage_count = usage_count + 1 WHERE id = ?"
        self.db.execute_query(query, (template_id,))
    
    def _format_template(self, row: tuple) -> Dict:
        """Format database row to template dict"""
        return {
            'id': row[0],
            'user_id': row[1],
            'name': row[2],
            'description': row[3],
            'category': row[4],
            'pattern': row[5],
            'variables': json.loads(row[6]) if row[6] else [],
            'tags': json.loads(row[7]) if row[7] else [],
            'examples': json.loads(row[8]) if row[8] else [],
            'created_at': row[9],
            'updated_at': row[10],
            'is_public': bool(row[11]),
            'usage_count': row[12]
        }


# Global instance
_custom_template_manager = None

def get_custom_template_manager():
    """Get global custom template manager instance"""
    global _custom_template_manager
    if _custom_template_manager is None:
        _custom_template_manager = CustomTemplateManager()
    return _custom_template_manager
