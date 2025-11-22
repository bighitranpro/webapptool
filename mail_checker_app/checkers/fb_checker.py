"""
Facebook Checker - Kiểm tra email có liên kết với tài khoản Facebook không
"""
import requests
import time
from typing import Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed


class FacebookChecker:
    """Kiểm tra email có liên kết Facebook account không"""
    
    def __init__(self, timeout=10, delay=0.5):
        self.timeout = timeout
        self.delay = delay  # Delay giữa các request để tránh rate limit
        self.session = requests.Session()
        
        # Headers giống browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://www.facebook.com',
            'Connection': 'keep-alive',
            'Referer': 'https://www.facebook.com/login/identify/',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
        }
    
    def check_facebook_single(self, email: str) -> Dict:
        """
        Kiểm tra 1 email có liên kết Facebook không
        
        Facebook identify endpoint trả về:
        - Nếu có tài khoản: redirect hoặc thông báo tìm thấy
        - Nếu không có: thông báo không tìm thấy
        
        Returns:
            dict: {
                'email': str,
                'has_facebook': bool,
                'confidence': float (0.0-1.0),
                'response_text': str,
                'error': str or None
            }
        """
        result = {
            'email': email,
            'has_facebook': False,
            'confidence': 0.0,
            'response_text': '',
            'error': None
        }
        
        # Delay to avoid rate limiting
        time.sleep(self.delay)
        
        try:
            # POST to Facebook identify endpoint
            url = 'https://www.facebook.com/login/identify/'
            
            data = {
                'email': email,
                'did_submit': 'Search',
            }
            
            response = self.session.post(
                url,
                headers=self.headers,
                data=data,
                timeout=self.timeout,
                allow_redirects=True
            )
            
            response_text = response.text.lower()
            result['response_text'] = response_text[:500]  # Lưu 500 ký tự đầu
            
            # Phân tích response
            # Các dấu hiệu cho thấy CÓ tài khoản Facebook
            found_indicators = [
                'recover your account',
                'reset your password',
                'we found your account',
                'choose a password',
                'identify yourself',
                'security check',
                'enter your password',
                'profile picture',
                'your account'
            ]
            
            # Các dấu hiệu cho thấy KHÔNG có tài khoản
            not_found_indicators = [
                'no search results',
                'could not find',
                'couldn\'t find',
                'no account',
                'not found',
                'no results',
                'please try again',
                'enter a different'
            ]
            
            found_count = sum(1 for indicator in found_indicators if indicator in response_text)
            not_found_count = sum(1 for indicator in not_found_indicators if indicator in response_text)
            
            # Quyết định dựa trên indicators
            if found_count > not_found_count:
                result['has_facebook'] = True
                result['confidence'] = min(found_count / len(found_indicators), 1.0)
            elif not_found_count > 0:
                result['has_facebook'] = False
                result['confidence'] = min(not_found_count / len(not_found_indicators), 1.0)
            else:
                # Không rõ ràng - check status code
                if response.status_code == 200:
                    # Nếu có form reset password trong response
                    if 'password' in response_text and 'reset' in response_text:
                        result['has_facebook'] = True
                        result['confidence'] = 0.6
                    else:
                        result['confidence'] = 0.3
                else:
                    result['confidence'] = 0.2
            
            # Check rate limiting
            if 'rate limit' in response_text or response.status_code == 429:
                result['error'] = 'Rate limited by Facebook'
                result['confidence'] = 0.0
            
        except requests.exceptions.Timeout:
            result['error'] = 'Request timeout'
        except requests.exceptions.ConnectionError:
            result['error'] = 'Connection error'
        except Exception as e:
            result['error'] = f'Exception: {str(e)}'
        
        return result
    
    def check_facebook_bulk(self, emails: List[str], max_workers=3) -> List[Dict]:
        """
        Kiểm tra nhiều email (giới hạn workers thấp để tránh rate limit)
        
        Args:
            emails: Danh sách email
            max_workers: Số workers (nên giữ thấp, 3-5)
        
        Returns:
            List of result dicts
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_email = {
                executor.submit(self.check_facebook_single, email): email 
                for email in emails
            }
            
            for future in as_completed(future_to_email):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    email = future_to_email[future]
                    results.append({
                        'email': email,
                        'has_facebook': False,
                        'confidence': 0.0,
                        'response_text': '',
                        'error': f'Exception: {str(e)}'
                    })
        
        return results


def check_email_facebook(email: str) -> Dict:
    """Helper function để check 1 email"""
    checker = FacebookChecker()
    return checker.check_facebook_single(email)


def check_emails_facebook(emails: List[str], max_workers=3) -> List[Dict]:
    """Helper function để check nhiều email"""
    checker = FacebookChecker()
    return checker.check_facebook_bulk(emails, max_workers=max_workers)


if __name__ == '__main__':
    # Test
    print("=== Testing Facebook Checker ===\n")
    print("NOTE: This test will make real requests to Facebook")
    print("Rate limiting may occur\n")
    
    test_emails = [
        'test@gmail.com',
        'nonexistent99999@gmail.com'
    ]
    
    checker = FacebookChecker(delay=1.0)  # 1 second delay between requests
    
    print("Testing single email check:")
    for email in test_emails[:1]:  # Test only 1 email to avoid rate limit
        print(f"\nChecking: {email}")
        result = checker.check_facebook_single(email)
        print(f"  Has Facebook: {result['has_facebook']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        if result['error']:
            print(f"  Error: {result['error']}")
        print(f"  Response (first 200 chars): {result['response_text'][:200]}...")
