"""
Quick Email Validator Module
Fast validation for common email providers without SMTP checks
"""

import re
from typing import Dict, Optional


class QuickValidator:
    """
    Quick validation for common email providers
    Validates format without SMTP connection for speed
    """
    
    def __init__(self):
        # Common domain configurations
        self.common_domains = {
            'gmail.com': {
                'min_length': 6,
                'max_length': 30,
                'pattern': r'^[a-zA-Z0-9][a-zA-Z0-9.]*[a-zA-Z0-9]$',
                'disallowed_patterns': [
                    r'\.\.', # consecutive dots
                    r'^\.',  # starting with dot
                    r'\.$'   # ending with dot
                ],
                'trust_score': 85,
                'description': 'Gmail format validation'
            },
            'yahoo.com': {
                'min_length': 4,
                'max_length': 32,
                'pattern': r'^[a-zA-Z][a-zA-Z0-9._-]*$',
                'disallowed_patterns': [
                    r'\.\.', # consecutive dots
                    r'__',   # consecutive underscores
                ],
                'trust_score': 80,
                'description': 'Yahoo format validation'
            },
            'outlook.com': {
                'min_length': 1,
                'max_length': 64,
                'pattern': r'^[a-zA-Z0-9][a-zA-Z0-9._-]*$',
                'disallowed_patterns': [
                    r'\.\.', # consecutive dots
                    r'__',   # consecutive underscores
                ],
                'trust_score': 80,
                'description': 'Outlook format validation'
            },
            'hotmail.com': {
                'min_length': 1,
                'max_length': 64,
                'pattern': r'^[a-zA-Z0-9][a-zA-Z0-9._-]*$',
                'disallowed_patterns': [
                    r'\.\.', # consecutive dots
                    r'__',   # consecutive underscores
                ],
                'trust_score': 80,
                'description': 'Hotmail format validation'
            },
            'icloud.com': {
                'min_length': 3,
                'max_length': 20,
                'pattern': r'^[a-zA-Z][a-zA-Z0-9._]*$',
                'disallowed_patterns': [
                    r'\.\.', # consecutive dots
                ],
                'trust_score': 75,
                'description': 'iCloud format validation'
            },
            'protonmail.com': {
                'min_length': 1,
                'max_length': 40,
                'pattern': r'^[a-zA-Z0-9][a-zA-Z0-9._-]*$',
                'disallowed_patterns': [
                    r'\.\.', # consecutive dots
                ],
                'trust_score': 75,
                'description': 'ProtonMail format validation'
            },
            'aol.com': {
                'min_length': 3,
                'max_length': 32,
                'pattern': r'^[a-zA-Z][a-zA-Z0-9._-]*$',
                'disallowed_patterns': [
                    r'\.\.', # consecutive dots
                ],
                'trust_score': 75,
                'description': 'AOL format validation'
            },
            'mail.com': {
                'min_length': 2,
                'max_length': 64,
                'pattern': r'^[a-zA-Z0-9][a-zA-Z0-9._-]*$',
                'disallowed_patterns': [
                    r'\.\.', # consecutive dots
                ],
                'trust_score': 70,
                'description': 'Mail.com format validation'
            }
        }
    
    def can_quick_validate(self, domain: str) -> bool:
        """Check if domain can be quick validated"""
        return domain.lower() in self.common_domains
    
    def quick_validate(self, email: str) -> Optional[Dict]:
        """
        Quick validate email without SMTP
        
        Returns:
            Dict with validation result or None if not a common domain
        """
        try:
            # Parse email
            if '@' not in email:
                return None
            
            local_part, domain = email.rsplit('@', 1)
            domain = domain.lower()
            
            # Check if common domain
            if domain not in self.common_domains:
                return None
            
            config = self.common_domains[domain]
            
            # Length check
            if not (config['min_length'] <= len(local_part) <= config['max_length']):
                return {
                    'status': 'DIE',
                    'score': 25.0,
                    'reason': f'Invalid length for {domain} (must be {config["min_length"]}-{config["max_length"]} chars)',
                    'quick_validated': True,
                    'smtp_skipped': True,
                    'confidence': 25.0,
                    'risk_level': 'high'
                }
            
            # Pattern check
            if not re.match(config['pattern'], local_part):
                return {
                    'status': 'DIE',
                    'score': 25.0,
                    'reason': f'Invalid format for {domain}',
                    'quick_validated': True,
                    'smtp_skipped': True,
                    'confidence': 25.0,
                    'risk_level': 'high'
                }
            
            # Disallowed patterns check
            for disallowed in config['disallowed_patterns']:
                if re.search(disallowed, local_part):
                    return {
                        'status': 'DIE',
                        'score': 25.0,
                        'reason': f'Invalid characters or pattern for {domain}',
                        'quick_validated': True,
                        'smtp_skipped': True,
                        'confidence': 25.0,
                        'risk_level': 'high'
                    }
            
            # All checks passed - format is valid
            return {
                'status': 'LIVE',
                'score': config['trust_score'],
                'reason': f'Valid format for {domain} (quick validation)',
                'quick_validated': True,
                'smtp_skipped': True,
                'confidence': config['trust_score'],
                'risk_level': 'low' if config['trust_score'] >= 80 else 'medium',
                'details': [
                    f'✓ Format valid for {domain}',
                    f'✓ Length OK ({len(local_part)} chars)',
                    f'✓ Pattern matched',
                    '⚠ SMTP verification skipped (quick mode)'
                ]
            }
            
        except Exception as e:
            # If any error, return None to fall back to full validation
            return None
    
    def get_supported_domains(self) -> list:
        """Get list of supported domains for quick validation"""
        return list(self.common_domains.keys())
    
    def get_domain_info(self, domain: str) -> Optional[Dict]:
        """Get configuration info for a domain"""
        return self.common_domains.get(domain.lower())
