"""
SMTP Checker - Kiểm tra email LIVE/DIE qua MX records và RCPT TO
"""
import dns.resolver
import socket
import smtplib
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List


class SMTPChecker:
    """Kiểm tra email có tồn tại không thông qua SMTP"""
    
    def __init__(self, timeout=10, from_email='verify@example.com'):
        self.timeout = timeout
        self.from_email = from_email
        self.dns_cache = {}
    
    def is_valid_email_format(self, email: str) -> bool:
        """Kiểm tra format email có hợp lệ không"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def get_mx_records(self, domain: str) -> List[str]:
        """Lấy MX records của domain"""
        if domain in self.dns_cache:
            return self.dns_cache[domain]
        
        try:
            mx_records = dns.resolver.resolve(domain, 'MX')
            mx_hosts = [str(r.exchange).rstrip('.') for r in mx_records]
            mx_hosts.sort(key=lambda x: dns.resolver.resolve(domain, 'MX')[0].preference)
            self.dns_cache[domain] = mx_hosts
            return mx_hosts
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers, Exception):
            return []
    
    def check_smtp_single(self, email: str) -> Dict:
        """
        Kiểm tra 1 email qua SMTP
        
        Returns:
            dict: {
                'email': str,
                'status': 'LIVE'|'DIE'|'UNKNOWN',
                'mx_records': list,
                'smtp_response': str,
                'error': str or None
            }
        """
        result = {
            'email': email,
            'status': 'UNKNOWN',
            'mx_records': [],
            'smtp_response': '',
            'error': None
        }
        
        # Validate format
        if not self.is_valid_email_format(email):
            result['status'] = 'DIE'
            result['error'] = 'Invalid email format'
            return result
        
        try:
            domain = email.split('@')[1]
        except IndexError:
            result['status'] = 'DIE'
            result['error'] = 'Cannot parse domain'
            return result
        
        # Get MX records
        mx_records = self.get_mx_records(domain)
        result['mx_records'] = mx_records
        
        if not mx_records:
            result['status'] = 'DIE'
            result['error'] = 'No MX records found'
            return result
        
        # Try to connect to SMTP server
        for mx in mx_records[:3]:  # Thử 3 MX servers đầu tiên
            try:
                # Connect with timeout
                smtp = smtplib.SMTP(timeout=self.timeout)
                smtp.connect(mx, 25)
                
                # HELO
                smtp.helo('example.com')
                
                # MAIL FROM
                smtp.mail(self.from_email)
                
                # RCPT TO - đây là bước quan trọng
                code, message = smtp.rcpt(email)
                
                smtp.quit()
                
                # Phân tích response code
                result['smtp_response'] = f"{code} {message.decode('utf-8', errors='ignore')}"
                
                if code == 250:
                    result['status'] = 'LIVE'
                elif code in [550, 551, 553]:  # Mailbox not found
                    result['status'] = 'DIE'
                    result['error'] = 'Mailbox does not exist'
                elif code in [450, 451, 452]:  # Temporary error
                    result['status'] = 'UNKNOWN'
                    result['error'] = 'Temporary error'
                else:
                    result['status'] = 'UNKNOWN'
                    result['error'] = f'Unexpected code: {code}'
                
                return result
                
            except smtplib.SMTPServerDisconnected:
                result['error'] = 'Server disconnected'
                continue
            except smtplib.SMTPConnectError:
                result['error'] = 'Cannot connect to SMTP server'
                continue
            except socket.timeout:
                result['error'] = 'Connection timeout'
                continue
            except Exception as e:
                result['error'] = f'SMTP error: {str(e)}'
                continue
        
        # Nếu thử hết MX records mà vẫn không được
        if result['status'] == 'UNKNOWN' and not result['error']:
            result['error'] = 'All MX servers failed'
        
        return result
    
    def check_smtp_bulk(self, emails: List[str], max_workers=10) -> List[Dict]:
        """
        Kiểm tra nhiều email cùng lúc bằng threading
        
        Args:
            emails: Danh sách email cần check
            max_workers: Số thread tối đa
        
        Returns:
            List of result dicts
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_email = {
                executor.submit(self.check_smtp_single, email): email 
                for email in emails
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_email):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    email = future_to_email[future]
                    results.append({
                        'email': email,
                        'status': 'UNKNOWN',
                        'mx_records': [],
                        'smtp_response': '',
                        'error': f'Exception: {str(e)}'
                    })
        
        return results


def check_email(email: str) -> Dict:
    """
    Helper function để check 1 email
    """
    checker = SMTPChecker()
    return checker.check_smtp_single(email)


def check_emails(emails: List[str], max_workers=10) -> List[Dict]:
    """
    Helper function để check nhiều email
    """
    checker = SMTPChecker()
    return checker.check_smtp_bulk(emails, max_workers=max_workers)


if __name__ == '__main__':
    # Test
    print("=== Testing SMTP Checker ===\n")
    
    test_emails = [
        'test@gmail.com',
        'nonexistent123456789@gmail.com',
        'invalid-email-format',
        'test@nonexistentdomain9999.com'
    ]
    
    checker = SMTPChecker()
    
    print("Testing single email checks:")
    for email in test_emails:
        print(f"\nChecking: {email}")
        result = checker.check_smtp_single(email)
        print(f"  Status: {result['status']}")
        print(f"  MX Records: {result['mx_records'][:2] if result['mx_records'] else 'None'}")
        print(f"  Response: {result['smtp_response']}")
        if result['error']:
            print(f"  Error: {result['error']}")
    
    print("\n\n=== Testing bulk check ===")
    results = checker.check_smtp_bulk(test_emails, max_workers=2)
    for r in results:
        print(f"{r['email']:<40} -> {r['status']}")
