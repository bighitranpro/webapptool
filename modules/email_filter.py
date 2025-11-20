"""
Email Filter Module
Advanced filtering capabilities for email lists
"""

import re
from typing import List, Dict, Callable
from datetime import datetime


class EmailFilter:
    """Advanced email filtering"""
    
    def __init__(self):
        self.filter_stats = {
            'total_input': 0,
            'total_output': 0,
            'filtered_out': 0,
            'filter_rate': 0.0
        }
    
    def filter_by_domain(self, emails: List[str], domains: List[str], 
                        include: bool = True) -> List[str]:
        """Filter emails by domain (include or exclude)"""
        result = []
        domains_lower = [d.lower() for d in domains]
        
        for email in emails:
            try:
                local, domain = email.split('@')
                domain_match = domain.lower() in domains_lower
                
                if include and domain_match:
                    result.append(email)
                elif not include and not domain_match:
                    result.append(email)
            except:
                continue
        
        return result
    
    def filter_by_length(self, emails: List[str], min_length: int = 0, 
                        max_length: int = 999) -> List[str]:
        """Filter emails by length"""
        return [e for e in emails if min_length <= len(e) <= max_length]
    
    def filter_by_pattern(self, emails: List[str], pattern: str, 
                         include: bool = True) -> List[str]:
        """Filter emails by regex pattern"""
        try:
            compiled = re.compile(pattern)
            if include:
                return [e for e in emails if compiled.search(e)]
            else:
                return [e for e in emails if not compiled.search(e)]
        except:
            return emails
    
    def filter_by_local_part(self, emails: List[str], 
                           contains: str = None,
                           starts_with: str = None,
                           ends_with: str = None) -> List[str]:
        """Filter by local part characteristics"""
        result = []
        
        for email in emails:
            try:
                local, domain = email.split('@')
                
                if contains and contains not in local:
                    continue
                if starts_with and not local.startswith(starts_with):
                    continue
                if ends_with and not local.endswith(ends_with):
                    continue
                
                result.append(email)
            except:
                continue
        
        return result
    
    def filter_numeric(self, emails: List[str], 
                      has_numbers: bool = True) -> List[str]:
        """Filter emails that have/don't have numbers"""
        result = []
        
        for email in emails:
            contains_digit = any(c.isdigit() for c in email)
            
            if has_numbers and contains_digit:
                result.append(email)
            elif not has_numbers and not contains_digit:
                result.append(email)
        
        return result
    
    def filter_by_provider(self, emails: List[str], 
                          providers: List[str]) -> List[str]:
        """Filter by common email providers"""
        common_providers = {
            'gmail': ['gmail.com', 'googlemail.com'],
            'yahoo': ['yahoo.com', 'yahoo.co.uk', 'yahoo.fr'],
            'outlook': ['outlook.com', 'hotmail.com', 'live.com'],
            'icloud': ['icloud.com', 'me.com', 'mac.com'],
            'other': []
        }
        
        result = []
        for email in emails:
            try:
                local, domain = email.split('@')
                for provider in providers:
                    if provider in common_providers:
                        if domain in common_providers[provider]:
                            result.append(email)
                            break
            except:
                continue
        
        return result
    
    def filter_duplicates(self, emails: List[str], 
                         case_sensitive: bool = False) -> List[str]:
        """Remove duplicate emails"""
        if case_sensitive:
            return list(set(emails))
        else:
            seen = set()
            result = []
            for email in emails:
                email_lower = email.lower()
                if email_lower not in seen:
                    seen.add(email_lower)
                    result.append(email)
            return result
    
    def filter_invalid(self, emails: List[str]) -> List[str]:
        """Filter out invalid email formats"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return [e for e in emails if re.match(pattern, e)]
    
    def apply_filters(self, emails: List[str], filters: Dict) -> Dict:
        """
        Apply multiple filters to email list
        
        Args:
            emails: List of emails to filter
            filters: Dict of filter configurations
        
        Returns:
            Dict with filtered emails and statistics
        """
        self.filter_stats['total_input'] = len(emails)
        filtered = emails.copy()
        
        # Apply each filter
        if filters.get('remove_invalid'):
            filtered = self.filter_invalid(filtered)
        
        if filters.get('remove_duplicates'):
            filtered = self.filter_duplicates(filtered, 
                                            filters.get('case_sensitive', False))
        
        if filters.get('domains'):
            filtered = self.filter_by_domain(
                filtered, 
                filters['domains'],
                filters.get('include_domains', True)
            )
        
        if filters.get('min_length') or filters.get('max_length'):
            filtered = self.filter_by_length(
                filtered,
                filters.get('min_length', 0),
                filters.get('max_length', 999)
            )
        
        if filters.get('pattern'):
            filtered = self.filter_by_pattern(
                filtered,
                filters['pattern'],
                filters.get('include_pattern', True)
            )
        
        if filters.get('has_numbers') is not None:
            filtered = self.filter_numeric(filtered, filters['has_numbers'])
        
        if filters.get('providers'):
            filtered = self.filter_by_provider(filtered, filters['providers'])
        
        # Update stats
        self.filter_stats['total_output'] = len(filtered)
        self.filter_stats['filtered_out'] = (
            self.filter_stats['total_input'] - self.filter_stats['total_output']
        )
        self.filter_stats['filter_rate'] = (
            round((self.filter_stats['filtered_out'] / 
                   self.filter_stats['total_input'] * 100) 
                  if self.filter_stats['total_input'] > 0 else 0, 2)
        )
        
        return {
            'success': True,
            'emails': filtered,
            'stats': self.filter_stats,
            'timestamp': datetime.now().isoformat()
        }
