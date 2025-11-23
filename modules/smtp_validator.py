"""
SMTP Validation Module
Real SMTP validation to check if email mailbox actually exists
"""

import smtplib
import dns.resolver
import socket
import re
from typing import Dict, List, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import time


class SMTPValidator:
    """
    Advanced SMTP email validation
    Checks if email addresses actually exist via SMTP
    """
    
    def __init__(self, timeout: int = 10, max_workers: int = 5):
        """
        Initialize SMTP validator
        
        Args:
            timeout: Connection timeout in seconds
            max_workers: Max parallel connections
        """
        self.timeout = timeout
        self.max_workers = max_workers
        self.from_email = 'verify@example.com'
    
    def validate_email(self, email: str) -> Dict:
        """
        Validate single email via SMTP
        
        Args:
            email: Email address to validate
        
        Returns:
            dict: Validation result with status and details
        """
        result = {
            'email': email,
            'valid': False,
            'status': 'UNKNOWN',
            'smtp_check': False,
            'mx_records': [],
            'error': None,
            'deliverable': False,
            'reason': None
        }
        
        try:
            # Step 1: Format validation
            if not self._validate_format(email):
                result['reason'] = 'Invalid email format'
                result['status'] = 'INVALID'
                return result
            
            # Step 2: Extract domain
            domain = email.split('@')[1]
            
            # Step 3: Get MX records
            mx_records = self._get_mx_records(domain)
            if not mx_records:
                result['reason'] = 'No MX records found'
                result['status'] = 'INVALID'
                return result
            
            result['mx_records'] = mx_records
            
            # Step 4: SMTP verification
            smtp_result = self._verify_smtp(email, mx_records[0])
            result.update(smtp_result)
            
            # Step 5: Determine final status
            if result['smtp_check']:
                if result['deliverable']:
                    result['status'] = 'VALID'
                    result['valid'] = True
                else:
                    result['status'] = 'INVALID'
            else:
                result['status'] = 'UNKNOWN'
                result['reason'] = result.get('error', 'SMTP check failed')
            
        except Exception as e:
            result['error'] = str(e)
            result['reason'] = f'Validation error: {str(e)}'
        
        return result
    
    def _validate_format(self, email: str) -> bool:
        """Basic email format validation"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def _get_mx_records(self, domain: str) -> List[str]:
        """Get MX records for domain"""
        try:
            records = dns.resolver.resolve(domain, 'MX')
            mx_records = [str(r.exchange).rstrip('.') for r in records]
            # Sort by priority
            return sorted(mx_records)
        except Exception as e:
            return []
    
    def _verify_smtp(self, email: str, mx_host: str) -> Dict:
        """
        Verify email via SMTP
        
        Args:
            email: Email to verify
            mx_host: MX server hostname
        
        Returns:
            dict: SMTP verification result
        """
        result = {
            'smtp_check': False,
            'deliverable': False,
            'error': None
        }
        
        try:
            # Connect to SMTP server
            server = smtplib.SMTP(timeout=self.timeout)
            server.set_debuglevel(0)
            
            # Connect
            server.connect(mx_host)
            server.helo('mail.example.com')
            
            # Set sender
            server.mail(self.from_email)
            
            # Check recipient
            code, message = server.rcpt(email)
            
            # Check response code
            if code == 250:
                result['deliverable'] = True
                result['smtp_check'] = True
            elif code == 550:
                # Mailbox not found
                result['smtp_check'] = True
                result['deliverable'] = False
                result['error'] = 'Mailbox does not exist'
            else:
                result['smtp_check'] = True
                result['error'] = f'SMTP code {code}: {message.decode()}'
            
            server.quit()
            
        except smtplib.SMTPServerDisconnected:
            result['error'] = 'Server disconnected'
        except smtplib.SMTPConnectError:
            result['error'] = 'Cannot connect to SMTP server'
        except socket.timeout:
            result['error'] = 'Connection timeout'
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def bulk_validate(self, emails: List[str]) -> Dict:
        """
        Validate multiple emails in parallel
        
        Args:
            emails: List of emails to validate
        
        Returns:
            dict: Bulk validation results
        """
        start_time = time.time()
        
        results = {
            'valid': [],
            'invalid': [],
            'unknown': []
        }
        
        stats = {
            'total': len(emails),
            'valid': 0,
            'invalid': 0,
            'unknown': 0,
            'smtp_checked': 0
        }
        
        # Validate in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_email = {
                executor.submit(self.validate_email, email): email 
                for email in emails
            }
            
            for future in as_completed(future_to_email):
                try:
                    result = future.result()
                    
                    if result['status'] == 'VALID':
                        results['valid'].append(result)
                        stats['valid'] += 1
                    elif result['status'] == 'INVALID':
                        results['invalid'].append(result)
                        stats['invalid'] += 1
                    else:
                        results['unknown'].append(result)
                        stats['unknown'] += 1
                    
                    if result['smtp_check']:
                        stats['smtp_checked'] += 1
                        
                except Exception as e:
                    # Handle any errors
                    results['unknown'].append({
                        'email': future_to_email[future],
                        'status': 'ERROR',
                        'error': str(e)
                    })
                    stats['unknown'] += 1
        
        stats['processing_time'] = time.time() - start_time
        stats['emails_per_second'] = stats['total'] / stats['processing_time'] if stats['processing_time'] > 0 else 0
        
        return {
            'success': True,
            'stats': stats,
            'results': results
        }
    
    def quick_validate(self, email: str) -> bool:
        """
        Quick validation - format and MX only
        Faster but less accurate
        
        Args:
            email: Email to validate
        
        Returns:
            bool: True if email looks valid
        """
        if not self._validate_format(email):
            return False
        
        try:
            domain = email.split('@')[1]
            mx_records = self._get_mx_records(domain)
            return len(mx_records) > 0
        except:
            return False


# Global instance
_smtp_validator = None

def get_smtp_validator(timeout: int = 10, max_workers: int = 5):
    """Get global SMTP validator instance"""
    global _smtp_validator
    if _smtp_validator is None:
        _smtp_validator = SMTPValidator(timeout=timeout, max_workers=max_workers)
    return _smtp_validator
