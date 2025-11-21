"""
FB Email Linked Checker Module
Check if emails are linked to Facebook accounts with 6 different API methods
"""

import re
import random
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum


class CheckAPIType(Enum):
    """API Types for checking FB email links"""
    API_1 = "api1"  # Check được LK ẩn, hiện
    API_2 = "api2"  # Check được LK ẩn, hiện
    API_3 = "api3"  # Ko Check được LK ẩn
    API_4 = "api4"  # Ko Check được LK ẩn
    API_5 = "api5"  # Check được LK ẩn, hiện
    API_6 = "api6"  # Ko Check được LK ẩn
    RANDOM = "random"  # Random selection


class LinkedStatus(Enum):
    """Email link status"""
    LINKED = "LINKED"  # Email linked to FB (visible)
    HIDDEN_LINKED = "HIDDEN_LINKED"  # Email linked but hidden
    NOT_LINKED = "NOT_LINKED"  # Email not linked
    ERROR = "ERROR"  # Check failed


class ProxyType(Enum):
    """Supported proxy types"""
    HTTP = "http"
    SOCKS4 = "socks4"
    SOCKS5 = "socks5"
    TINSOFT = "tinsoft"
    TMPROXY = "tmproxy"
    SHOPLIKE = "shoplike"
    PROXYV6 = "proxyv6"
    PROXYFB = "proxyfb"
    WWPROXY = "wwproxy"


class FBLinkedChecker:
    """Facebook Email Linked Checker with 6 API methods"""
    
    def __init__(self):
        self.stats = {
            'total': 0,
            'linked': 0,
            'hidden_linked': 0,
            'not_linked': 0,
            'error': 0,
            'code6_count': 0,
            'code8_count': 0
        }
        
        self.results = {
            'linked': [],
            'hidden_linked': [],
            'not_linked': [],
            'error': []
        }
        
        # API capabilities
        self.api_can_check_hidden = {
            CheckAPIType.API_1: True,
            CheckAPIType.API_2: True,
            CheckAPIType.API_3: False,
            CheckAPIType.API_4: False,
            CheckAPIType.API_5: True,
            CheckAPIType.API_6: False
        }
    
    def validate_email_format(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def setup_proxy(self, proxy_config: Dict) -> Optional[Dict]:
        """Setup proxy configuration for requests"""
        if not proxy_config or not proxy_config.get('enabled'):
            return None
        
        proxy_type = proxy_config.get('type', 'http')
        proxy_host = proxy_config.get('host')
        proxy_port = proxy_config.get('port')
        proxy_auth = proxy_config.get('auth')
        
        if not proxy_host or not proxy_port:
            return None
        
        # Build proxy URL
        if proxy_auth:
            username = proxy_auth.get('username')
            password = proxy_auth.get('password')
            proxy_url = f"{proxy_type}://{username}:{password}@{proxy_host}:{proxy_port}"
        else:
            proxy_url = f"{proxy_type}://{proxy_host}:{proxy_port}"
        
        return {
            'http': proxy_url,
            'https': proxy_url
        }
    
    def check_via_api(self, email: str, api_type: CheckAPIType, proxy: Optional[Dict] = None) -> Dict:
        """
        Check email via specific API
        
        NOTE: This is SIMULATED implementation since we don't have real FB API access.
        In production, you would integrate with actual Facebook Graph API or other services.
        """
        result = {
            'email': email,
            'api_used': api_type.value,
            'status': LinkedStatus.NOT_LINKED.value,
            'linked': False,
            'hidden_linked': False,
            'code_length': None,
            'phone': None,
            'secondary_email': None,
            'account_info': {},
            'timestamp': datetime.now().isoformat(),
            'error': None
        }
        
        # Validate format first
        if not self.validate_email_format(email):
            result['status'] = LinkedStatus.ERROR.value
            result['error'] = 'Invalid email format'
            return result
        
        # Simulate API delay
        time.sleep(random.uniform(0.1, 0.3))
        
        # ============================================================
        # SIMULATED FB CHECK LOGIC
        # In real implementation, you would:
        # 1. Make HTTP request to FB API with proxy
        # 2. Parse response to determine link status
        # 3. Extract account information if linked
        # ============================================================
        
        # Simulate different outcomes based on email domain
        domain = email.split('@')[1].lower()
        
        # Simulate checking logic
        can_check_hidden = self.api_can_check_hidden.get(api_type, False)
        
        # Gmail/Yahoo/Hotmail more likely to be linked
        if domain in ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']:
            rand = random.random()
            
            if rand < 0.4:  # 40% linked
                result['status'] = LinkedStatus.LINKED.value
                result['linked'] = True
                result['code_length'] = random.choice([6, 8])
                
                # Simulate extracting info
                result['phone'] = f"+84{''.join([str(random.randint(0,9)) for _ in range(9)])}"
                result['secondary_email'] = f"{''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=8))}@gmail.com"
                result['account_info'] = {
                    'name': 'User Name',
                    'profile_url': f'https://facebook.com/{random.randint(100000000, 999999999)}'
                }
                
            elif rand < 0.6 and can_check_hidden:  # 20% hidden linked (only if API supports)
                result['status'] = LinkedStatus.HIDDEN_LINKED.value
                result['hidden_linked'] = True
                result['linked'] = True
                result['code_length'] = random.choice([6, 8])
                
            else:  # Not linked
                result['status'] = LinkedStatus.NOT_LINKED.value
        
        else:
            # Other domains less likely
            if random.random() < 0.2:
                result['status'] = LinkedStatus.LINKED.value
                result['linked'] = True
                result['code_length'] = random.choice([6, 8])
        
        # Update code stats
        if result['code_length'] == 6:
            self.stats['code6_count'] += 1
        elif result['code_length'] == 8:
            self.stats['code8_count'] += 1
        
        return result
    
    def bulk_check(self, emails: List[str], options: Dict) -> Dict:
        """
        Bulk check emails with threading support
        
        Options:
        - api_type: CheckAPIType enum or "random"
        - proxy_config: dict with proxy settings
        - max_workers: int (threading)
        - timeout: int (seconds)
        - start_from: int (index to start from)
        - check_code_68: bool (check code 6 or 8)
        """
        # Reset stats
        self.stats = {
            'total': len(emails),
            'linked': 0,
            'hidden_linked': 0,
            'not_linked': 0,
            'error': 0,
            'code6_count': 0,
            'code8_count': 0,
            'processing_time': 0
        }
        
        self.results = {
            'linked': [],
            'hidden_linked': [],
            'not_linked': [],
            'error': []
        }
        
        start_time = time.time()
        
        # Get options
        api_type_str = options.get('api_type', 'random')
        if api_type_str == 'random':
            api_type = CheckAPIType.RANDOM
        else:
            api_type = CheckAPIType(api_type_str)
        
        proxy_config = options.get('proxy_config')
        proxy = self.setup_proxy(proxy_config) if proxy_config else None
        
        start_from = options.get('start_from', 0)
        emails_to_check = emails[start_from:]
        
        # Process each email (in real implementation, use ThreadPoolExecutor)
        for email in emails_to_check:
            # Select API
            if api_type == CheckAPIType.RANDOM:
                selected_api = random.choice(list(CheckAPIType)[:-1])  # Exclude RANDOM
            else:
                selected_api = api_type
            
            # Check email
            result = self.check_via_api(email, selected_api, proxy)
            
            # Categorize result
            status = result['status']
            if status == LinkedStatus.LINKED.value:
                self.stats['linked'] += 1
                self.results['linked'].append(result)
            elif status == LinkedStatus.HIDDEN_LINKED.value:
                self.stats['hidden_linked'] += 1
                self.results['hidden_linked'].append(result)
            elif status == LinkedStatus.NOT_LINKED.value:
                self.stats['not_linked'] += 1
                self.results['not_linked'].append(result)
            elif status == LinkedStatus.ERROR.value:
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
    
    def check_code_type(self, emails: List[str], options: Dict) -> Dict:
        """
        Check CODE 6 or CODE 8 for emails
        Specialized function for code length detection
        """
        results = {
            'code6': [],
            'code8': [],
            'unknown': []
        }
        
        # Get API selection for code checking
        api_type_str = options.get('api_type', 'api1')
        
        for email in emails:
            if api_type_str == 'random':
                selected_api = random.choice([CheckAPIType.API_1, CheckAPIType.API_2])
            else:
                selected_api = CheckAPIType(api_type_str)
            
            result = self.check_via_api(email, selected_api)
            
            if result['code_length'] == 6:
                results['code6'].append(result)
            elif result['code_length'] == 8:
                results['code8'].append(result)
            else:
                results['unknown'].append(result)
        
        return {
            'success': True,
            'stats': {
                'total': len(emails),
                'code6': len(results['code6']),
                'code8': len(results['code8']),
                'unknown': len(results['unknown'])
            },
            'results': results
        }
