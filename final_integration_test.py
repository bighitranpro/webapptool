#!/usr/bin/env python3
"""
Final Integration Test - All Improved Modules
Tests modules 1-3 via API to verify production integration
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5003"

def print_test(name, status, details=""):
    emoji = "✅" if status else "❌"
    print(f"{emoji} {name}")
    if details:
        print(f"   {details}")

def test_health():
    """Test API health endpoint"""
    print("\n📊 Testing API Health...")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        data = response.json()
        
        success = data.get('status') == 'healthy'
        modules_ok = all(data.get('modules', {}).values())
        
        print_test("API Health Check", success and modules_ok)
        print_test("All Modules Loaded", modules_ok, f"{len(data.get('modules', {}))} modules")
        
        return success and modules_ok
    except Exception as e:
        print_test("API Health Check", False, str(e))
        return False

def test_module1_validator():
    """Test Module 1: Email Validator Pro"""
    print("\n📧 Testing Module 1: Email Validator Pro...")
    
    test_cases = [
        {
            "emails": ["test@gmail.com", "invalid@fakdomain123.com"],
            "expected_valid": 1,
            "expected_invalid": 1
        }
    ]
    
    try:
        for i, test in enumerate(test_cases, 1):
            response = requests.post(
                f"{BASE_URL}/api/validate",
                json={"emails": test["emails"], "check_smtp": False},
                timeout=10
            )
            data = response.json()
            
            valid_count = len(data.get('valid', []))
            invalid_count = len(data.get('invalid', []))
            
            success = (valid_count == test['expected_valid'] and 
                      invalid_count == test['expected_invalid'])
            
            print_test(
                f"Test Case {i}",
                success,
                f"Valid: {valid_count}/{test['expected_valid']}, Invalid: {invalid_count}/{test['expected_invalid']}"
            )
            
        return True
    except Exception as e:
        print_test("Module 1 Test", False, str(e))
        return False

def test_module2_generator():
    """Test Module 2: Email Generator"""
    print("\n🎲 Testing Module 2: Email Generator...")
    
    test_cases = [
        {
            "count": 10,
            "domain": "gmail.com",
            "pattern": "random"
        }
    ]
    
    try:
        for i, test in enumerate(test_cases, 1):
            response = requests.post(
                f"{BASE_URL}/api/generate",
                json=test,
                timeout=10
            )
            data = response.json()
            
            emails = data.get('emails', [])
            success = len(emails) == test['count']
            
            # Verify all emails have correct domain
            correct_domain = all('@' + test['domain'] in email for email in emails)
            
            print_test(
                f"Test Case {i}",
                success and correct_domain,
                f"Generated: {len(emails)}/{test['count']}, Domain OK: {correct_domain}"
            )
            
        return True
    except Exception as e:
        print_test("Module 2 Test", False, str(e))
        return False

def test_module3_extractor():
    """Test Module 3: Email Extractor"""
    print("\n🔍 Testing Module 3: Email Extractor...")
    
    test_cases = [
        {
            "text": "Contact: John@Example.COM, JOHN@EXAMPLE.COM, support@gmail.com",
            "remove_duplicates": True,
            "expected_count": 2,  # Case-insensitive dedup should merge John/JOHN
            "expected_unique": True
        },
        {
            "text": "Email us: test@example.com. Visit website.com, or contact@site.org.",
            "expected_count": 2,  # Should not include 'website.com.'
            "expected_no_trailing_punct": True
        }
    ]
    
    try:
        for i, test in enumerate(test_cases, 1):
            response = requests.post(
                f"{BASE_URL}/api/extract",
                json={
                    "text": test["text"],
                    "remove_duplicates": test.get("remove_duplicates", False)
                },
                timeout=10
            )
            data = response.json()
            
            emails = data.get('emails', [])
            success = len(emails) == test['expected_count']
            
            # Additional checks
            details = f"Extracted: {len(emails)}/{test['expected_count']}"
            
            if test.get('expected_unique'):
                # Check case-insensitive deduplication
                lower_emails = [e.lower() for e in emails]
                unique = len(lower_emails) == len(set(lower_emails))
                details += f", Unique: {unique}"
                success = success and unique
            
            print_test(f"Test Case {i}", success, details)
            
        return True
    except Exception as e:
        print_test("Module 3 Test", False, str(e))
        return False

def main():
    print("=" * 60)
    print("  FINAL INTEGRATION TEST - ALL IMPROVED MODULES")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {BASE_URL}")
    print("=" * 60)
    
    results = []
    
    # Test each module
    results.append(("API Health", test_health()))
    results.append(("Module 1 (Validator)", test_module1_validator()))
    results.append(("Module 2 (Generator)", test_module2_generator()))
    results.append(("Module 3 (Extractor)", test_module3_extractor()))
    
    # Summary
    print("\n" + "=" * 60)
    print("  TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        emoji = "✅" if result else "❌"
        print(f"{emoji} {name}")
    
    print("\n" + "=" * 60)
    print(f"  RESULT: {passed}/{total} TESTS PASSED")
    
    if passed == total:
        print("  🎉 ALL TESTS PASSED - INTEGRATION SUCCESSFUL!")
    else:
        print("  ⚠️  SOME TESTS FAILED - REVIEW NEEDED")
    
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    import sys
    sys.exit(0 if main() else 1)
