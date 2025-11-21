"""
Email Pass 2FA Checker Module
Check if email:password accounts have 2FA enabled and linked pages
"""

import re
import random
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum


class CheckAPI(Enum):
    """API types for 2FA checking"""
    API_1 = "api1"
    API_2 = "api2"
    RANDOM = "random"


class AccountStatus(Enum):
    """Account check status"""
    HIT_2FA = "HIT_2FA"  # Has 2FA enabled
    HAS_PAGE = "HAS_PAGE"  # Has linked page
    NOT_HIT = "NOT_HIT"  # No 2FA
    ERROR = "ERROR"  # Login failed


class EmailPass2FAChecker:
    """Check email:password for 2FA and page status"""
    
    def __init__(self):
        self.stats = {
            'total': 0,
            'hit_2fa': 0,
            'has_page': 0,
            'not_hit': 0,
            'error': 0,
            'checked': 0
        }
        
        self.results = {
            'hit_2fa': [],
            'has_page': [],
            'not_hit': [],
            'error': []
        }
    
    def parse_email_pass(self, line: str) -> Optional[Tuple[str, str]]:
        """Parse email:password format"""
        if ':' not in line:
            return None
        
        parts = line.strip().split(':', 1)
        if len(parts) != 2:
            return None
        
        email, password = parts
        
        # Validate email format
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return None
        
        return (email.strip(), password.strip())
    
    def validate_password_pattern(self, password: str, pattern: str) -> bool:
        """
        Validate password ends with specific pattern
        Pattern format: 1|@|.|#|*|5|*|!|?
        """
        if not pattern:
            return True
        
        try:
            # Convert pattern to regex
            pattern_chars = pattern.split('|')
            regex_pattern = ''.join([re.escape(c) if c != '*' else '.' for c in pattern_chars])
            regex_pattern = regex_pattern + '$'  # Must end with this pattern
            
            return bool(re.search(regex_pattern, password))
        except:
            return True
    
    def check_account_2fa(self, email: str, password: str, api_type: CheckAPI, 
                          proxy: Optional[Dict] = None) -> Dict:
        """
        Check if account has 2FA enabled and linked pages
        
        NOTE: This is SIMULATED because we don't have real FB credentials.
        In production, you would:
        1. Use Facebook Graph API with app credentials
        2. Or use selenium/playwright for automated login
        3. Check for 2FA challenge page
        4. Query for linked pages
        """
        result = {
            'email': email,
            'password': password,  # In real app, don't store plaintext!
            'api_used': api_type.value,
            'status': AccountStatus.NOT_HIT.value,
            'has_2fa': False,
            'has_page': False,
            'page_count': 0,
            'page_ids': [],
            'timestamp': datetime.now().isoformat(),
            'error': None
        }
        
        # Simulate API delay
        time.sleep(random.uniform(0.2, 0.5))
        
        # ============================================================
        # SIMULATED 2FA CHECK LOGIC
        # In real implementation:
        # 1. Login to FB with email:password
        # 2. Check if 2FA challenge appears
        # 3. Query user's pages
        # 4. Return results
        # ============================================================
        
        # Simulate checking
        domain = email.split('@')[1].lower()
        
        # Gmail/Yahoo more likely to have 2FA
        if domain in ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']:
            rand = random.random()
            
            if rand < 0.15:  # 15% have 2FA
                result['status'] = AccountStatus.HIT_2FA.value
                result['has_2fa'] = True
                
                # Some also have pages
                if random.random() < 0.3:  # 30% of 2FA accounts have pages
                    result['has_page'] = True
                    result['page_count'] = random.randint(1, 5)
                    result['page_ids'] = [
                        str(random.randint(100000000000, 999999999999)) 
                        for _ in range(result['page_count'])
                    ]
                
            elif rand < 0.25:  # 10% just have pages
                result['status'] = AccountStatus.HAS_PAGE.value
                result['has_page'] = True
                result['page_count'] = random.randint(1, 3)
                result['page_ids'] = [
                    str(random.randint(100000000000, 999999999999)) 
                    for _ in range(result['page_count'])
                ]
                
            elif rand < 0.35:  # 10% login error
                result['status'] = AccountStatus.ERROR.value
                result['error'] = 'Login failed - Invalid credentials or locked'
                
            else:  # Rest are not hit
                result['status'] = AccountStatus.NOT_HIT.value
        
        else:
            # Other domains lower chance
            if random.random() < 0.05:
                result['status'] = AccountStatus.HIT_2FA.value
                result['has_2fa'] = True
            elif random.random() < 0.15:
                result['status'] = AccountStatus.ERROR.value
                result['error'] = 'Login failed'
            else:
                result['status'] = AccountStatus.NOT_HIT.value
        
        return result
    
    def bulk_check(self, accounts: List[str], options: Dict) -> Dict:
        """
        Bulk check email:password accounts
        
        Options:
        - api_type: "api1" | "api2" | "random"
        - password_pattern: str (e.g., "1|@|.|#|*|5|*|!|?")
        - validate_pattern: bool
        - proxy_config: dict
        - max_workers: int
        - start_from: int
        """
        # Reset stats
        self.stats = {
            'total': len(accounts),
            'hit_2fa': 0,
            'has_page': 0,
            'not_hit': 0,
            'error': 0,
            'checked': 0,
            'processing_time': 0
        }
        
        self.results = {
            'hit_2fa': [],
            'has_page': [],
            'not_hit': [],
            'error': []
        }
        
        start_time = time.time()
        
        # Get options
        api_type_str = options.get('api_type', 'api1')
        if api_type_str == 'random':
            api_type = CheckAPI.RANDOM
        else:
            api_type = CheckAPI(api_type_str)
        
        password_pattern = options.get('password_pattern', '')
        validate_pattern = options.get('validate_pattern', False)
        start_from = options.get('start_from', 0)
        
        accounts_to_check = accounts[start_from:]
        
        for line in accounts_to_check:
            # Parse email:password
            parsed = self.parse_email_pass(line)
            if not parsed:
                # Invalid format
                self.stats['error'] += 1
                self.results['error'].append({
                    'raw': line,
                    'error': 'Invalid format (expected email:password)'
                })
                continue
            
            email, password = parsed
            
            # Validate password pattern if enabled
            if validate_pattern and password_pattern:
                if not self.validate_password_pattern(password, password_pattern):
                    self.stats['not_hit'] += 1
                    self.results['not_hit'].append({
                        'email': email,
                        'password': password,
                        'status': 'NOT_HIT',
                        'reason': 'Password pattern mismatch'
                    })
                    self.stats['checked'] += 1
                    continue
            
            # Select API
            if api_type == CheckAPI.RANDOM:
                selected_api = random.choice([CheckAPI.API_1, CheckAPI.API_2])
            else:
                selected_api = api_type
            
            # Check account
            result = self.check_account_2fa(email, password, selected_api)
            
            self.stats['checked'] += 1
            
            # Categorize result
            status = result['status']
            if status == AccountStatus.HIT_2FA.value:
                self.stats['hit_2fa'] += 1
                self.results['hit_2fa'].append(result)
                
                # Also count pages if has both
                if result['has_page']:
                    self.stats['has_page'] += 1
                    self.results['has_page'].append(result)
                    
            elif status == AccountStatus.HAS_PAGE.value:
                self.stats['has_page'] += 1
                self.results['has_page'].append(result)
                
            elif status == AccountStatus.NOT_HIT.value:
                self.stats['not_hit'] += 1
                self.results['not_hit'].append(result)
                
            elif status == AccountStatus.ERROR.value:
                self.stats['error'] += 1
                self.results['error'].append(result)
        
        end_time = time.time()
        self.stats['processing_time'] = round(end_time - start_time, 2)
        
        return {
            'success': True,
            'stats': self.stats,
            'results': self.results,
            'timestamp': datetime.now().isoformat()
        }
