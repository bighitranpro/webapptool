"""
Email Validator Module
Advanced email validation with LIVE/DIE detection
"""

import re
import dns.resolver
import socket
from datetime import datetime
from typing import Dict, List, Tuple
import concurrent.futures
from collections import Counter


class EmailValidator:
    """Advanced email validation with LIVE/DIE detection"""
    
    def __init__(self):
        self.stats = {
            'total': 0,
            'live': 0,
            'die': 0,
            'unknown': 0,
            'can_receive_code': 0,
            'cannot_receive_code': 0
        }
        self.results = {
            'live': [],
            'die': [],
            'unknown': [],
            'can_receive': [],
            'cannot_receive': []
        }
    
    def validate_format(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def check_mx_record(self, domain: str) -> Tuple[bool, List[str]]:
        """Check MX records for domain"""
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            mx_list = [str(mx.exchange) for mx in mx_records]
            return True, mx_list
        except:
            return False, []
    
    def check_smtp_connection(self, domain: str, timeout: int = 5) -> bool:
        """Check if SMTP server is reachable"""
        try:
            has_mx, mx_records = self.check_mx_record(domain)
            if not has_mx or not mx_records:
                return False
            
            # Try to connect to first MX server
            mx_host = str(mx_records[0]).rstrip('.')
            socket.setdefaulttimeout(timeout)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((mx_host, 25))
            sock.close()
            return result == 0
        except:
            return False
    
    def is_trusted_provider(self, domain: str) -> bool:
        """Check if domain is from trusted email provider"""
        trusted_providers = [
            # Major providers
            'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com',
            'icloud.com', 'protonmail.com', 'mail.com', 'aol.com',
            # Business providers
            'zoho.com', 'gmx.com', 'yandex.com', 'mail.ru',
            # Regional providers
            'qq.com', '163.com', '126.com', 'sina.com',
            'naver.com', 'daum.net', 'hanmail.net'
        ]
        domain_lower = domain.lower()
        return any(domain_lower == provider or domain_lower.endswith('.' + provider) 
                  for provider in trusted_providers)
    
    def check_domain_reputation(self, domain: str) -> Dict:
        """Check domain reputation and trustworthiness"""
        result = {
            'is_trusted': False,
            'has_valid_mx': False,
            'mx_count': 0,
            'smtp_reachable': False,
            'is_disposable': False,
            'reputation_score': 0
        }
        
        # Check if trusted provider
        result['is_trusted'] = self.is_trusted_provider(domain)
        if result['is_trusted']:
            result['reputation_score'] += 40
        
        # Check MX records
        has_mx, mx_records = self.check_mx_record(domain)
        result['has_valid_mx'] = has_mx
        result['mx_count'] = len(mx_records) if has_mx else 0
        
        if has_mx:
            result['reputation_score'] += 30
            # Bonus for multiple MX records (redundancy)
            if result['mx_count'] >= 3:
                result['reputation_score'] += 10
        
        # Check disposable
        result['is_disposable'] = self.check_disposable_email(domain)
        if result['is_disposable']:
            result['reputation_score'] -= 50
        
        # Try SMTP (but don't penalize if fails - many providers block)
        result['smtp_reachable'] = self.check_smtp_connection(domain, timeout=3)
        if result['smtp_reachable']:
            result['reputation_score'] += 20
        
        return result
    
    def check_disposable_email(self, domain: str) -> bool:
        """Check if email is from disposable/temporary service"""
        disposable_domains = [
            'tempmail.com', 'guerrillamail.com', 'throwaway.email',
            '10minutemail.com', 'mailinator.com', 'trashmail.com',
            'maildrop.cc', 'temp-mail.org', 'yopmail.com', 'mailnesia.com'
        ]
        return any(disp in domain.lower() for disp in disposable_domains)
    
    def check_facebook_compatible(self, domain: str) -> bool:
        """Check if domain is compatible with Facebook"""
        trusted_providers = [
            'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com',
            'icloud.com', 'protonmail.com', 'mail.com', 'aol.com',
            'zoho.com', 'gmx.com', 'yandex.com'
        ]
        return domain.lower() in trusted_providers
    
    def validate_email_deep(self, email: str) -> Dict:
        """Deep validation with LIVE/DIE detection (Enhanced Algorithm)"""
        result = {
            'email': email,
            'timestamp': datetime.now().isoformat(),
            'format_valid': False,
            'has_mx': False,
            'mx_records': [],
            'smtp_reachable': False,
            'is_disposable': False,
            'is_trusted': False,
            'fb_compatible': False,
            'can_receive_code': False,
            'status': 'UNKNOWN',
            'confidence': 0,
            'reputation_score': 0,
            'details': []
        }
        
        # Format validation
        if not self.validate_format(email):
            result['status'] = 'DIE'
            result['confidence'] = 0
            result['details'].append('❌ Invalid email format')
            return result
        
        result['format_valid'] = True
        result['details'].append('✓ Valid format')
        
        # Extract domain
        try:
            local, domain = email.split('@')
        except:
            result['status'] = 'DIE'
            result['confidence'] = 0
            result['details'].append('❌ Cannot parse email')
            return result
        
        # Check domain reputation (comprehensive)
        reputation = self.check_domain_reputation(domain)
        
        result['has_mx'] = reputation['has_valid_mx']
        result['is_trusted'] = reputation['is_trusted']
        result['is_disposable'] = reputation['is_disposable']
        result['smtp_reachable'] = reputation['smtp_reachable']
        result['reputation_score'] = reputation['reputation_score']
        
        # MX Records
        if not reputation['has_valid_mx']:
            result['status'] = 'DIE'
            result['confidence'] = 0
            result['details'].append('❌ No MX records found')
            return result
        
        has_mx, mx_records = self.check_mx_record(domain)
        result['mx_records'] = mx_records
        result['details'].append(f'✓ {len(mx_records)} MX record(s) found')
        
        # Disposable email check
        if reputation['is_disposable']:
            result['status'] = 'DIE'
            result['confidence'] = 0
            result['details'].append('❌ Disposable/temporary email service')
            return result
        
        # Trusted provider bonus
        if reputation['is_trusted']:
            result['details'].append('✓ Trusted email provider')
        
        # SMTP check (informational only - not critical)
        if reputation['smtp_reachable']:
            result['details'].append('✓ SMTP server reachable')
        else:
            result['details'].append('⚠ SMTP check failed (may be blocked)')
        
        # Facebook compatibility
        result['fb_compatible'] = self.check_facebook_compatible(domain)
        
        # Can receive code logic (more lenient)
        if result['fb_compatible'] and result['has_mx']:
            # Trusted provider with MX = can likely receive code
            result['can_receive_code'] = True
            result['details'].append('✓ Can receive verification codes')
        else:
            result['details'].append('⚠ May not receive verification codes')
        
        # ============================================================
        # ENHANCED LIVE/DIE DETERMINATION ALGORITHM
        # ============================================================
        confidence = 0
        
        # Base checks
        if result['format_valid']: 
            confidence += 10
        
        if result['has_mx']: 
            confidence += 40  # Critical factor
        
        # Trusted provider = high confidence
        if result['is_trusted']: 
            confidence += 35  # Gmail/Yahoo/Outlook etc.
        
        # Multiple MX records = professional setup
        if len(result['mx_records']) >= 3:
            confidence += 10
        
        # SMTP reachable (bonus, but not required)
        if result['smtp_reachable']:
            confidence += 5
        
        result['confidence'] = min(confidence, 100)
        
        # Status determination
        if confidence >= 75:
            result['status'] = 'LIVE'
            result['details'].append(f'✅ LIVE - {confidence}% confidence')
        elif confidence >= 50:
            result['status'] = 'UNKNOWN'
            result['details'].append(f'❓ UNKNOWN - {confidence}% confidence')
        else:
            result['status'] = 'DIE'
            result['details'].append(f'❌ DIE - {confidence}% confidence')
        
        return result
    
    def bulk_validate(self, emails: List[str], max_workers: int = 10) -> Dict:
        """Bulk validate emails with threading"""
        self.stats = {
            'total': len(emails),
            'live': 0,
            'die': 0,
            'unknown': 0,
            'can_receive_code': 0,
            'cannot_receive_code': 0,
            'processing_time': 0
        }
        
        self.results = {
            'live': [],
            'die': [],
            'unknown': [],
            'can_receive': [],
            'cannot_receive': []
        }
        
        start_time = datetime.now()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_email = {
                executor.submit(self.validate_email_deep, email): email 
                for email in emails
            }
            
            for future in concurrent.futures.as_completed(future_to_email):
                result = future.result()
                
                # Update stats
                status = result['status']
                if status == 'LIVE':
                    self.stats['live'] += 1
                    self.results['live'].append(result)
                elif status == 'DIE':
                    self.stats['die'] += 1
                    self.results['die'].append(result)
                else:
                    self.stats['unknown'] += 1
                    self.results['unknown'].append(result)
                
                # Can receive code stats
                if result['can_receive_code']:
                    self.stats['can_receive_code'] += 1
                    self.results['can_receive'].append(result)
                else:
                    self.stats['cannot_receive_code'] += 1
                    self.results['cannot_receive'].append(result)
        
        end_time = datetime.now()
        self.stats['processing_time'] = (end_time - start_time).total_seconds()
        
        return {
            'stats': self.stats,
            'results': self.results,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_dashboard_data(self) -> Dict:
        """Get formatted data for dashboard"""
        return {
            'summary': {
                'total': self.stats['total'],
                'live': self.stats['live'],
                'die': self.stats['die'],
                'unknown': self.stats['unknown'],
                'live_rate': round((self.stats['live'] / self.stats['total'] * 100) if self.stats['total'] > 0 else 0, 2),
                'die_rate': round((self.stats['die'] / self.stats['total'] * 100) if self.stats['total'] > 0 else 0, 2)
            },
            'facebook_code': {
                'can_receive': self.stats['can_receive_code'],
                'cannot_receive': self.stats['cannot_receive_code'],
                'success_rate': round((self.stats['can_receive_code'] / self.stats['total'] * 100) if self.stats['total'] > 0 else 0, 2)
            },
            'lists': {
                'live_emails': [r['email'] for r in self.results['live']],
                'die_emails': [r['email'] for r in self.results['die']],
                'can_receive_emails': [r['email'] for r in self.results['can_receive']],
                'cannot_receive_emails': [r['email'] for r in self.results['cannot_receive']]
            },
            'processing_time': self.stats.get('processing_time', 0)
        }
