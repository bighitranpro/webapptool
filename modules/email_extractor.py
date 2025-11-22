"""
Email Extractor Module
Extract emails from text with various filtering options
"""

import re
from typing import List, Dict, Set
from datetime import datetime


class EmailExtractor:
    """Extract and filter emails from text"""
    
    def __init__(self):
        # Word boundary prevents trailing punctuation capture
        self.email_pattern = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
        self.stats = {
            'total_extracted': 0,
            'unique_emails': 0,
            'duplicates_removed': 0
        }
    
    def extract_emails(self, text: str) -> List[str]:
        """Extract all emails from text"""
        emails = re.findall(self.email_pattern, text)
        return emails
    
    def extract_unique_emails(self, text: str) -> List[str]:
        """Extract unique emails from text (case-insensitive)"""
        emails = self.extract_emails(text)
        # Case-insensitive deduplication
        unique_emails = self.remove_duplicates(emails)
        
        self.stats['total_extracted'] = len(emails)
        self.stats['unique_emails'] = len(unique_emails)
        self.stats['duplicates_removed'] = len(emails) - len(unique_emails)
        
        return unique_emails
    
    def filter_by_domain(self, emails: List[str], domains: List[str]) -> List[str]:
        """Filter emails by domain (exact match or ends with)"""
        filtered = []
        for email in emails:
            try:
                local, domain = email.split('@')
                domain_lower = domain.lower()
                # Exact match or domain ends with filter (e.g., "gmail.com" matches "mail.gmail.com")
                for d in domains:
                    d_lower = d.lower()
                    if domain_lower == d_lower or domain_lower.endswith('.' + d_lower):
                        filtered.append(email)
                        break
            except:
                continue
        return filtered
    
    def filter_by_pattern(self, emails: List[str], pattern: str) -> List[str]:
        """Filter emails by regex pattern"""
        try:
            compiled_pattern = re.compile(pattern)
            return [e for e in emails if compiled_pattern.search(e)]
        except:
            return emails
    
    def remove_duplicates(self, emails: List[str]) -> List[str]:
        """Remove duplicate emails while preserving order"""
        seen = set()
        result = []
        for email in emails:
            email_lower = email.lower()
            if email_lower not in seen:
                seen.add(email_lower)
                result.append(email)
        return result
    
    def categorize_by_domain(self, emails: List[str]) -> Dict:
        """Categorize emails by domain"""
        categories = {}
        
        for email in emails:
            try:
                local, domain = email.split('@')
                if domain not in categories:
                    categories[domain] = []
                categories[domain].append(email)
            except:
                continue
        
        return categories
    
    def extract_and_process(self, text: str, remove_dups: bool = True,
                          filter_domains: List[str] = None,
                          filter_pattern: str = None) -> Dict:
        """
        Extract and process emails with various options
        
        Args:
            text: Input text containing emails
            remove_dups: Remove duplicate emails
            filter_domains: List of domains to filter by
            filter_pattern: Regex pattern to filter by
        
        Returns:
            Dict with extracted emails and statistics
        """
        # Extract emails
        emails = self.extract_emails(text)
        
        # Remove duplicates if requested
        if remove_dups:
            emails = self.remove_duplicates(emails)
        
        # Filter by domain if provided
        if filter_domains:
            emails = self.filter_by_domain(emails, filter_domains)
        
        # Filter by pattern if provided
        if filter_pattern:
            emails = self.filter_by_pattern(emails, filter_pattern)
        
        # Categorize
        categories = self.categorize_by_domain(emails)
        
        return {
            'success': True,
            'total_emails': len(emails),
            'emails': emails,
            'categories': categories,
            'domain_count': len(categories),
            'stats': self.stats,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_statistics(self, emails: List[str]) -> Dict:
        """Get detailed statistics about emails"""
        total = len(emails)
        domains = {}
        
        for email in emails:
            try:
                local, domain = email.split('@')
                domains[domain] = domains.get(domain, 0) + 1
            except:
                continue
        
        return {
            'total_emails': total,
            'unique_domains': len(domains),
            'domain_distribution': domains,
            'most_common_domain': max(domains.items(), key=lambda x: x[1])[0] if domains else None,
            'timestamp': datetime.now().isoformat()
        }
