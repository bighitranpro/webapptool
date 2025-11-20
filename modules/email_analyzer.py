"""
Email Analyzer Module
Analyze email lists for patterns, statistics, and insights
"""

from typing import List, Dict
from datetime import datetime
from collections import Counter
import re


class EmailAnalyzer:
    """Analyze email lists for insights"""
    
    def __init__(self):
        self.analysis_types = {
            'domain': 'Phân tích domain',
            'pattern': 'Phân tích mẫu',
            'length': 'Phân tích độ dài',
            'character': 'Phân tích ký tự'
        }
    
    def analyze_domains(self, emails: List[str]) -> Dict:
        """Analyze domain distribution"""
        domains = []
        
        for email in emails:
            try:
                local, domain = email.split('@')
                domains.append(domain.lower())
            except:
                continue
        
        domain_counts = Counter(domains)
        total = len(domains)
        
        return {
            'total_domains': len(domain_counts),
            'domain_distribution': dict(domain_counts),
            'top_domains': domain_counts.most_common(10),
            'domain_percentages': {
                domain: round(count / total * 100, 2)
                for domain, count in domain_counts.items()
            },
            'most_common': domain_counts.most_common(1)[0] if domain_counts else None
        }
    
    def analyze_patterns(self, emails: List[str]) -> Dict:
        """Analyze common patterns in emails"""
        patterns = {
            'has_numbers': 0,
            'has_dots': 0,
            'has_underscores': 0,
            'has_hyphens': 0,
            'all_lowercase': 0,
            'all_uppercase': 0,
            'mixed_case': 0,
            'starts_with_number': 0,
            'ends_with_number': 0
        }
        
        for email in emails:
            try:
                local, domain = email.split('@')
                
                if any(c.isdigit() for c in local):
                    patterns['has_numbers'] += 1
                if '.' in local:
                    patterns['has_dots'] += 1
                if '_' in local:
                    patterns['has_underscores'] += 1
                if '-' in local:
                    patterns['has_hyphens'] += 1
                if local.islower():
                    patterns['all_lowercase'] += 1
                elif local.isupper():
                    patterns['all_uppercase'] += 1
                else:
                    patterns['mixed_case'] += 1
                if local and local[0].isdigit():
                    patterns['starts_with_number'] += 1
                if local and local[-1].isdigit():
                    patterns['ends_with_number'] += 1
                    
            except:
                continue
        
        total = len(emails)
        pattern_percentages = {
            key: round(value / total * 100, 2) if total > 0 else 0
            for key, value in patterns.items()
        }
        
        return {
            'patterns': patterns,
            'percentages': pattern_percentages,
            'total_analyzed': total
        }
    
    def analyze_length(self, emails: List[str]) -> Dict:
        """Analyze email length distribution"""
        lengths = [len(email) for email in emails]
        
        if not lengths:
            return {
                'min': 0,
                'max': 0,
                'avg': 0,
                'distribution': {}
            }
        
        # Group by length ranges
        distribution = {
            '0-10': 0,
            '11-20': 0,
            '21-30': 0,
            '31-40': 0,
            '40+': 0
        }
        
        for length in lengths:
            if length <= 10:
                distribution['0-10'] += 1
            elif length <= 20:
                distribution['11-20'] += 1
            elif length <= 30:
                distribution['21-30'] += 1
            elif length <= 40:
                distribution['31-40'] += 1
            else:
                distribution['40+'] += 1
        
        return {
            'min': min(lengths),
            'max': max(lengths),
            'avg': round(sum(lengths) / len(lengths), 2),
            'distribution': distribution,
            'total_analyzed': len(lengths)
        }
    
    def analyze_characters(self, emails: List[str]) -> Dict:
        """Analyze character usage in emails"""
        char_counts = {
            'letters': 0,
            'digits': 0,
            'dots': 0,
            'underscores': 0,
            'hyphens': 0,
            'other': 0
        }
        
        total_chars = 0
        
        for email in emails:
            try:
                local, domain = email.split('@')
                
                for char in local:
                    total_chars += 1
                    if char.isalpha():
                        char_counts['letters'] += 1
                    elif char.isdigit():
                        char_counts['digits'] += 1
                    elif char == '.':
                        char_counts['dots'] += 1
                    elif char == '_':
                        char_counts['underscores'] += 1
                    elif char == '-':
                        char_counts['hyphens'] += 1
                    else:
                        char_counts['other'] += 1
            except:
                continue
        
        percentages = {
            key: round(value / total_chars * 100, 2) if total_chars > 0 else 0
            for key, value in char_counts.items()
        }
        
        return {
            'counts': char_counts,
            'percentages': percentages,
            'total_characters': total_chars
        }
    
    def analyze_provider_distribution(self, emails: List[str]) -> Dict:
        """Analyze distribution by email provider"""
        providers = {
            'Gmail': ['gmail.com', 'googlemail.com'],
            'Yahoo': ['yahoo.com', 'yahoo.co.uk', 'yahoo.fr', 'yahoo.de'],
            'Outlook': ['outlook.com', 'hotmail.com', 'live.com'],
            'iCloud': ['icloud.com', 'me.com', 'mac.com'],
            'ProtonMail': ['protonmail.com', 'proton.me'],
            'Other': []
        }
        
        provider_counts = {provider: 0 for provider in providers.keys()}
        
        for email in emails:
            try:
                local, domain = email.split('@')
                domain = domain.lower()
                
                categorized = False
                for provider, domains in providers.items():
                    if domain in domains:
                        provider_counts[provider] += 1
                        categorized = True
                        break
                
                if not categorized:
                    provider_counts['Other'] += 1
                    
            except:
                continue
        
        total = len(emails)
        percentages = {
            provider: round(count / total * 100, 2) if total > 0 else 0
            for provider, count in provider_counts.items()
        }
        
        return {
            'distribution': provider_counts,
            'percentages': percentages,
            'total_analyzed': total
        }
    
    def full_analysis(self, emails: List[str]) -> Dict:
        """Perform complete analysis on email list"""
        return {
            'success': True,
            'total_emails': len(emails),
            'domains': self.analyze_domains(emails),
            'patterns': self.analyze_patterns(emails),
            'length': self.analyze_length(emails),
            'characters': self.analyze_characters(emails),
            'providers': self.analyze_provider_distribution(emails),
            'timestamp': datetime.now().isoformat()
        }
    
    def compare_lists(self, list1: List[str], list2: List[str]) -> Dict:
        """Compare two email lists"""
        set1 = set(e.lower() for e in list1)
        set2 = set(e.lower() for e in list2)
        
        return {
            'list1_size': len(list1),
            'list2_size': len(list2),
            'common': len(set1.intersection(set2)),
            'only_in_list1': len(set1 - set2),
            'only_in_list2': len(set2 - set1),
            'similarity': round(
                len(set1.intersection(set2)) / len(set1.union(set2)) * 100, 2
            ) if set1.union(set2) else 0,
            'timestamp': datetime.now().isoformat()
        }
