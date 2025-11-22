"""
Email Checker Integrated Module
Combines Email Generation, SMTP Validation, Facebook Check, and Country Prediction
"""

import sys
import os

# Add mail_checker_app to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'mail_checker_app'))

from checkers.email_generator import generate_emails, get_email_info
from checkers.smtp_checker import SMTPChecker
from checkers.fb_checker import FacebookChecker
from checkers.geo_locator import GeoLocator
from utils.exporter import ResultExporter
from datetime import datetime
from typing import List, Dict
import threading


class EmailCheckerIntegrated:
    """
    Integrated Email Checker with all features:
    - Generate realistic emails
    - Check SMTP Live/Die
    - Check Facebook linkage
    - Predict country
    - Export results
    """
    
    def __init__(self):
        self.smtp_checker = SMTPChecker(timeout=10)
        self.fb_checker = FacebookChecker(timeout=10, delay=0.5)
        self.geo_locator = GeoLocator()
        self.exporter = ResultExporter(output_dir='mail_checker_app/results')
        
        # Progress tracking
        self.current_check = {
            'is_running': False,
            'current': 0,
            'total': 0,
            'results': [],
            'status': 'idle'
        }
        self.lock = threading.Lock()
    
    def generate_emails(self, count: int = 10, mix_ratio: float = 0.7) -> Dict:
        """
        Generate email addresses
        
        Args:
            count: Number of emails to generate
            mix_ratio: Ratio of Vietnamese emails (0.0-1.0)
        
        Returns:
            dict: {
                'success': bool,
                'emails': list,
                'count': int,
                'error': str or None
            }
        """
        try:
            if count < 1 or count > 1000:
                return {
                    'success': False,
                    'emails': [],
                    'count': 0,
                    'error': 'Count must be between 1 and 1000'
                }
            
            if mix_ratio < 0 or mix_ratio > 1:
                return {
                    'success': False,
                    'emails': [],
                    'count': 0,
                    'error': 'Mix ratio must be between 0.0 and 1.0'
                }
            
            emails = generate_emails(count=count, mix_ratio=mix_ratio)
            
            return {
                'success': True,
                'emails': emails,
                'count': len(emails),
                'error': None
            }
        
        except Exception as e:
            return {
                'success': False,
                'emails': [],
                'count': 0,
                'error': str(e)
            }
    
    def calculate_overall_score(self, smtp_result: Dict, fb_result: Dict, geo_result: Dict) -> float:
        """Calculate overall score (0.0-1.0)"""
        score = 0.0
        
        # SMTP status (40%)
        if smtp_result.get('status') == 'LIVE':
            score += 0.40
        elif smtp_result.get('status') == 'UNKNOWN':
            score += 0.20
        
        # Facebook (30%)
        if fb_result.get('has_facebook'):
            score += 0.30 * fb_result.get('confidence', 0.5)
        
        # Country confidence (30%)
        score += 0.30 * geo_result.get('confidence', 0.0)
        
        return round(score, 2)
    
    def check_single_email(self, email: str) -> Dict:
        """
        Check a single email completely
        
        Returns:
            dict: Complete result with all checks
        """
        # Check SMTP
        smtp_result = self.smtp_checker.check_smtp_single(email)
        
        # Check Facebook (only if SMTP is LIVE or UNKNOWN)
        fb_result = {'has_facebook': False, 'confidence': 0.0, 'error': 'Skipped'}
        if smtp_result['status'] in ['LIVE', 'UNKNOWN']:
            fb_result = self.fb_checker.check_facebook_single(email)
        
        # Predict country
        geo_result = self.geo_locator.analyze_email(email)
        
        # Calculate score
        score = self.calculate_overall_score(smtp_result, fb_result, geo_result)
        
        return {
            'email': email,
            'smtp_status': smtp_result['status'],
            'smtp_error': smtp_result.get('error', ''),
            'mx_records': smtp_result.get('mx_records', []),
            'has_facebook': fb_result.get('has_facebook', False),
            'fb_confidence': fb_result.get('confidence', 0.0),
            'fb_error': fb_result.get('error', ''),
            'country': geo_result['country'],
            'country_confidence': geo_result['confidence'],
            'score': score,
            'checked_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def check_emails_batch(self, emails: List[str], callback=None) -> List[Dict]:
        """
        Check multiple emails with progress tracking
        
        Args:
            emails: List of email addresses
            callback: Optional callback function(progress_info)
        
        Returns:
            list: Results
        """
        results = []
        total = len(emails)
        
        with self.lock:
            self.current_check = {
                'is_running': True,
                'current': 0,
                'total': total,
                'results': [],
                'status': 'running'
            }
        
        try:
            for i, email in enumerate(emails):
                result = self.check_single_email(email)
                results.append(result)
                
                with self.lock:
                    self.current_check['current'] = i + 1
                    self.current_check['results'].append(result)
                
                # Call callback if provided
                if callback:
                    callback({
                        'current': i + 1,
                        'total': total,
                        'result': result
                    })
            
            with self.lock:
                self.current_check['status'] = 'completed'
        
        except Exception as e:
            with self.lock:
                self.current_check['status'] = f'error: {str(e)}'
        
        finally:
            with self.lock:
                self.current_check['is_running'] = False
        
        return results
    
    def get_progress(self) -> Dict:
        """Get current checking progress"""
        with self.lock:
            return {
                'is_running': self.current_check['is_running'],
                'current': self.current_check['current'],
                'total': self.current_check['total'],
                'status': self.current_check['status'],
                'results': self.current_check['results'].copy()
            }
    
    def export_results(self, results: List[Dict], filename: str = None) -> Dict:
        """
        Export results to CSV
        
        Returns:
            dict: {
                'success': bool,
                'filepath': str,
                'filename': str,
                'stats': dict,
                'error': str or None
            }
        """
        try:
            if not results:
                return {
                    'success': False,
                    'filepath': '',
                    'filename': '',
                    'stats': {},
                    'error': 'No results to export'
                }
            
            filepath = self.exporter.export_detailed_csv(results, filename)
            stats = self.exporter.get_export_stats(results)
            
            return {
                'success': True,
                'filepath': filepath,
                'filename': os.path.basename(filepath),
                'stats': stats,
                'error': None
            }
        
        except Exception as e:
            return {
                'success': False,
                'filepath': '',
                'filename': '',
                'stats': {},
                'error': str(e)
            }
    
    def get_stats(self, results: List[Dict]) -> Dict:
        """Get statistics from results"""
        if not results:
            return {}
        
        return self.exporter.get_export_stats(results)


if __name__ == '__main__':
    # Test
    print("=== Testing Email Checker Integrated ===\n")
    
    checker = EmailCheckerIntegrated()
    
    # Test 1: Generate emails
    print("Test 1: Generate emails")
    gen_result = checker.generate_emails(count=3, mix_ratio=0.7)
    if gen_result['success']:
        print(f"✓ Generated {gen_result['count']} emails")
        print(f"  Emails: {gen_result['emails']}")
    else:
        print(f"✗ Error: {gen_result['error']}")
    
    print("\nTest 2: Check emails")
    if gen_result['success'] and gen_result['emails']:
        results = checker.check_emails_batch(gen_result['emails'][:2])
        print(f"✓ Checked {len(results)} emails")
        for r in results:
            print(f"  {r['email']} -> SMTP: {r['smtp_status']}, Country: {r['country']}, Score: {r['score']}")
    
    print("\nTest 3: Get stats")
    if results:
        stats = checker.get_stats(results)
        print(f"✓ Stats:")
        print(f"  Total: {stats.get('total', 0)}")
        print(f"  SMTP Live: {stats.get('smtp_live', 0)}")
        print(f"  Has Facebook: {stats.get('has_facebook', 0)}")
    
    print("\n✓ All tests completed!")
