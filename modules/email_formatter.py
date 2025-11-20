"""
Email Formatter Module
Format emails in various ways (case conversion, sorting, etc.)
"""

from typing import List, Dict
from datetime import datetime
import re


class EmailFormatter:
    """Format and transform email lists"""
    
    def __init__(self):
        self.format_types = {
            'lowercase': 'Chữ thường',
            'uppercase': 'Chữ hoa',
            'titlecase': 'Chữ hoa đầu',
            'original': 'Giữ nguyên'
        }
        
        self.sort_types = {
            'alphabetical': 'A-Z',
            'reverse': 'Z-A',
            'domain': 'Theo domain',
            'length': 'Theo độ dài'
        }
    
    def to_lowercase(self, emails: List[str]) -> List[str]:
        """Convert all emails to lowercase"""
        return [e.lower() for e in emails]
    
    def to_uppercase(self, emails: List[str]) -> List[str]:
        """Convert all emails to uppercase"""
        return [e.upper() for e in emails]
    
    def to_titlecase(self, emails: List[str]) -> List[str]:
        """Convert emails to title case"""
        result = []
        for email in emails:
            try:
                local, domain = email.split('@')
                local = local.title()
                result.append(f"{local}@{domain.lower()}")
            except:
                result.append(email)
        return result
    
    def sort_alphabetical(self, emails: List[str], reverse: bool = False) -> List[str]:
        """Sort emails alphabetically"""
        return sorted(emails, reverse=reverse)
    
    def sort_by_domain(self, emails: List[str]) -> List[str]:
        """Sort emails by domain"""
        return sorted(emails, key=lambda e: e.split('@')[1] if '@' in e else e)
    
    def sort_by_length(self, emails: List[str], reverse: bool = False) -> List[str]:
        """Sort emails by length"""
        return sorted(emails, key=len, reverse=reverse)
    
    def add_prefix(self, emails: List[str], prefix: str) -> List[str]:
        """Add prefix to local part of emails"""
        result = []
        for email in emails:
            try:
                local, domain = email.split('@')
                result.append(f"{prefix}{local}@{domain}")
            except:
                result.append(email)
        return result
    
    def add_suffix(self, emails: List[str], suffix: str) -> List[str]:
        """Add suffix to local part of emails"""
        result = []
        for email in emails:
            try:
                local, domain = email.split('@')
                result.append(f"{local}{suffix}@{domain}")
            except:
                result.append(email)
        return result
    
    def replace_domain(self, emails: List[str], new_domain: str) -> List[str]:
        """Replace domain of all emails"""
        result = []
        for email in emails:
            try:
                local, domain = email.split('@')
                result.append(f"{local}@{new_domain}")
            except:
                result.append(email)
        return result
    
    def format_as_list(self, emails: List[str], separator: str = '\n') -> str:
        """Format emails as string with separator"""
        return separator.join(emails)
    
    def format_with_numbers(self, emails: List[str]) -> str:
        """Format emails with line numbers"""
        return '\n'.join([f"{i+1}. {email}" for i, email in enumerate(emails)])
    
    def format_emails(self, emails: List[str], 
                     case_format: str = 'lowercase',
                     sort_type: str = None,
                     prefix: str = None,
                     suffix: str = None,
                     new_domain: str = None) -> Dict:
        """
        Format emails with multiple options
        
        Args:
            emails: List of emails to format
            case_format: Case format (lowercase, uppercase, titlecase)
            sort_type: Sort type (alphabetical, reverse, domain, length)
            prefix: Prefix to add
            suffix: Suffix to add
            new_domain: New domain to replace
        
        Returns:
            Dict with formatted emails and statistics
        """
        formatted = emails.copy()
        
        # Apply case formatting
        if case_format == 'lowercase':
            formatted = self.to_lowercase(formatted)
        elif case_format == 'uppercase':
            formatted = self.to_uppercase(formatted)
        elif case_format == 'titlecase':
            formatted = self.to_titlecase(formatted)
        
        # Apply prefix/suffix
        if prefix:
            formatted = self.add_prefix(formatted, prefix)
        if suffix:
            formatted = self.add_suffix(formatted, suffix)
        
        # Replace domain
        if new_domain:
            formatted = self.replace_domain(formatted, new_domain)
        
        # Apply sorting
        if sort_type == 'alphabetical':
            formatted = self.sort_alphabetical(formatted)
        elif sort_type == 'reverse':
            formatted = self.sort_alphabetical(formatted, reverse=True)
        elif sort_type == 'domain':
            formatted = self.sort_by_domain(formatted)
        elif sort_type == 'length':
            formatted = self.sort_by_length(formatted)
        
        return {
            'success': True,
            'total': len(formatted),
            'emails': formatted,
            'formatted_text': self.format_as_list(formatted),
            'formatted_numbered': self.format_with_numbers(formatted),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_available_formats(self) -> Dict:
        """Get all available format options"""
        return {
            'case_formats': self.format_types,
            'sort_types': self.sort_types
        }
