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
        """Deep validation with LIVE/DIE detection"""
        result = {
            'email': email,
            'timestamp': datetime.now().isoformat(),
            'format_valid': False,
            'has_mx': False,
            'mx_records': [],
            'smtp_reachable': False,
            'is_disposable': False,
            'fb_compatible': False,
            'can_receive_code': False,
            'status': 'UNKNOWN',
            'confidence': 0,
            'details': []
        }
        
        # Format validation
        if not self.validate_format(email):
            result['status'] = 'DIE'
            result['details'].append('Invalid format')
            return result
        
        result['format_valid'] = True
        
        # Extract domain
        try:
            local, domain = email.split('@')
        except:
            result['status'] = 'DIE'
            result['details'].append('Cannot extract domain')
            return result
        
        # MX Record check
        has_mx, mx_records = self.check_mx_record(domain)
        result['has_mx'] = has_mx
        result['mx_records'] = mx_records
        
        if not has_mx:
            result['status'] = 'DIE'
            result['details'].append('No MX records')
            return result
        
        result['details'].append(f'{len(mx_records)} MX records found')
        
        # SMTP connection check
        result['smtp_reachable'] = self.check_smtp_connection(domain)
        if result['smtp_reachable']:
            result['details'].append('SMTP server reachable')
        else:
            result['details'].append('SMTP server unreachable')
        
        # Disposable check
        result['is_disposable'] = self.check_disposable_email(domain)
        if result['is_disposable']:
            result['status'] = 'DIE'
            result['details'].append('Disposable email service')
            return result
        
        # Facebook compatibility
        result['fb_compatible'] = self.check_facebook_compatible(domain)
        
        # Determine if can receive Facebook code
        if result['fb_compatible'] and result['smtp_reachable']:
            result['can_receive_code'] = True
            result['details'].append('Can receive Facebook code')
        else:
            result['details'].append('Cannot receive Facebook code')
        
        # Determine LIVE/DIE status
        confidence = 0
        if result['format_valid']: confidence += 20
        if result['has_mx']: confidence += 30
        if result['smtp_reachable']: confidence += 30
        if result['fb_compatible']: confidence += 20
        
        result['confidence'] = confidence
        
        if confidence >= 80:
            result['status'] = 'LIVE'
        elif confidence >= 50:
            result['status'] = 'UNKNOWN'
        else:
            result['status'] = 'DIE'
        
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
