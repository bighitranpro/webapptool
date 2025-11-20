"""
Email Deduplicator Module
Advanced duplicate removal with various strategies
"""

from typing import List, Dict, Tuple
from datetime import datetime
import re


class EmailDeduplicator:
    """Remove duplicates with advanced strategies"""
    
    def __init__(self):
        self.dedup_methods = {
            'exact': 'Trùng chính xác',
            'case_insensitive': 'Không phân biệt hoa thường',
            'normalize': 'Chuẩn hóa (bỏ dấu chấm Gmail)',
            'domain': 'Theo domain',
            'local_part': 'Theo local part'
        }
        
        self.stats = {
            'total_input': 0,
            'total_output': 0,
            'duplicates_removed': 0,
            'duplicate_rate': 0.0
        }
    
    def exact_dedup(self, emails: List[str]) -> List[str]:
        """Remove exact duplicates"""
        seen = set()
        result = []
        
        for email in emails:
            if email not in seen:
                seen.add(email)
                result.append(email)
        
        return result
    
    def case_insensitive_dedup(self, emails: List[str]) -> List[str]:
        """Remove duplicates ignoring case"""
        seen = set()
        result = []
        
        for email in emails:
            email_lower = email.lower()
            if email_lower not in seen:
                seen.add(email_lower)
                result.append(email)
        
        return result
    
    def normalize_gmail(self, email: str) -> str:
        """
        Normalize Gmail addresses
        - Remove dots from local part
        - Remove everything after + sign
        """
        try:
            local, domain = email.split('@')
            
            # Only normalize Gmail addresses
            if domain.lower() in ['gmail.com', 'googlemail.com']:
                # Remove dots
                local = local.replace('.', '')
                # Remove + aliases
                if '+' in local:
                    local = local.split('+')[0]
            
            return f"{local}@{domain}"
        except:
            return email
    
    def normalize_dedup(self, emails: List[str]) -> List[str]:
        """Remove duplicates after normalization"""
        seen = set()
        result = []
        
        for email in emails:
            normalized = self.normalize_gmail(email).lower()
            if normalized not in seen:
                seen.add(normalized)
                result.append(email)
        
        return result
    
    def find_duplicates(self, emails: List[str], 
                       method: str = 'case_insensitive') -> Dict:
        """Find and group duplicates"""
        duplicates = {}
        seen = {}
        
        for email in emails:
            if method == 'exact':
                key = email
            elif method == 'case_insensitive':
                key = email.lower()
            elif method == 'normalize':
                key = self.normalize_gmail(email).lower()
            else:
                key = email.lower()
            
            if key in seen:
                if key not in duplicates:
                    duplicates[key] = [seen[key]]
                duplicates[key].append(email)
            else:
                seen[key] = email
        
        return duplicates
    
    def get_duplicate_groups(self, emails: List[str],
                           method: str = 'case_insensitive') -> Dict:
        """Get groups of duplicate emails"""
        duplicates = self.find_duplicates(emails, method)
        
        return {
            'duplicate_groups': duplicates,
            'num_groups': len(duplicates),
            'total_duplicates': sum(len(group) - 1 for group in duplicates.values()),
            'affected_emails': sum(len(group) for group in duplicates.values())
        }
    
    def smart_dedup(self, emails: List[str], 
                   keep_strategy: str = 'first') -> List[str]:
        """
        Smart deduplication with keep strategy
        
        Args:
            keep_strategy: 'first', 'last', 'shortest', 'longest'
        """
        groups = {}
        
        for email in emails:
            key = email.lower()
            if key not in groups:
                groups[key] = []
            groups[key].append(email)
        
        result = []
        for key, group in groups.items():
            if len(group) == 1:
                result.append(group[0])
            else:
                if keep_strategy == 'first':
                    result.append(group[0])
                elif keep_strategy == 'last':
                    result.append(group[-1])
                elif keep_strategy == 'shortest':
                    result.append(min(group, key=len))
                elif keep_strategy == 'longest':
                    result.append(max(group, key=len))
                else:
                    result.append(group[0])
        
        return result
    
    def deduplicate(self, emails: List[str], 
                   method: str = 'case_insensitive',
                   keep_strategy: str = 'first') -> Dict:
        """
        Deduplicate emails with specified method
        
        Args:
            emails: List of emails to deduplicate
            method: Deduplication method
            keep_strategy: Strategy for keeping duplicates
        
        Returns:
            Dict with deduplicated results and statistics
        """
        self.stats['total_input'] = len(emails)
        
        if method == 'exact':
            deduplicated = self.exact_dedup(emails)
        elif method == 'case_insensitive':
            deduplicated = self.case_insensitive_dedup(emails)
        elif method == 'normalize':
            deduplicated = self.normalize_dedup(emails)
        elif method == 'smart':
            deduplicated = self.smart_dedup(emails, keep_strategy)
        else:
            deduplicated = self.case_insensitive_dedup(emails)
        
        self.stats['total_output'] = len(deduplicated)
        self.stats['duplicates_removed'] = (
            self.stats['total_input'] - self.stats['total_output']
        )
        self.stats['duplicate_rate'] = round(
            (self.stats['duplicates_removed'] / self.stats['total_input'] * 100)
            if self.stats['total_input'] > 0 else 0, 2
        )
        
        # Find duplicate groups
        duplicate_info = self.get_duplicate_groups(emails, method)
        
        return {
            'success': True,
            'emails': deduplicated,
            'stats': self.stats,
            'duplicate_info': duplicate_info,
            'method': method,
            'keep_strategy': keep_strategy,
            'timestamp': datetime.now().isoformat()
        }
    
    def compare_dedup_methods(self, emails: List[str]) -> Dict:
        """Compare results from different deduplication methods"""
        results = {}
        
        for method in ['exact', 'case_insensitive', 'normalize']:
            dedup_result = self.deduplicate(emails, method)
            results[method] = {
                'output_count': len(dedup_result['emails']),
                'duplicates_removed': dedup_result['stats']['duplicates_removed'],
                'duplicate_rate': dedup_result['stats']['duplicate_rate']
            }
        
        return {
            'comparison': results,
            'input_count': len(emails),
            'timestamp': datetime.now().isoformat()
        }
