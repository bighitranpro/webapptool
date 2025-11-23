"""
Ultra Email Generator Test Suite
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Comprehensive test coverage for EmailGeneratorUltra
"""

import unittest
import time
import threading
from modules.email_generator_ultra import (
    EmailGeneratorUltra,
    DomainRotator,
    RealisticNamePool,
    CryptoNumberGenerator,
    UniqueSessionCache,
    RFC5322Validator,
    get_ultra_generator
)


class TestDomainRotator(unittest.TestCase):
    """Test domain rotation logic"""
    
    def test_domain_rotation_distribution(self):
        """Test even distribution of domains"""
        domains = ['gmail.com', 'yahoo.com', 'outlook.com']
        rotator = DomainRotator(domains)
        
        results = []
        for _ in range(300):
            results.append(rotator.get_next())
        
        # Check each domain is used
        for domain in domains:
            self.assertIn(domain, results)
        
        # Check usage is somewhat even (within 20% variance)
        stats = rotator.get_stats()
        counts = list(stats['usage_distribution'].values())
        avg = sum(counts) / len(counts)
        for count in counts:
            variance = abs(count - avg) / avg
            self.assertLess(variance, 0.3, "Domain distribution variance too high")
    
    def test_no_consecutive_same_domain(self):
        """Test that same domain doesn't repeat consecutively often"""
        rotator = DomainRotator(['gmail.com', 'yahoo.com', 'outlook.com'])
        
        consecutive_same = 0
        prev = None
        for _ in range(100):
            current = rotator.get_next()
            if current == prev:
                consecutive_same += 1
            prev = current
        
        # Should have very few consecutive same domains (<20%)
        self.assertLess(consecutive_same, 20)
    
    def test_thread_safety(self):
        """Test domain rotator in multi-threaded environment"""
        rotator = DomainRotator()
        results = []
        results_lock = threading.Lock()
        
        def worker():
            for _ in range(100):
                domain = rotator.get_next()
                with results_lock:
                    results.append(domain)
        
        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Should have 500 total domains
        self.assertEqual(len(results), 500)


class TestRealisticNamePool(unittest.TestCase):
    """Test realistic name generation"""
    
    def test_pattern_variety(self):
        """Test that different patterns are generated"""
        patterns = set()
        for _ in range(100):
            pattern_type, _ = RealisticNamePool.get_realistic_pattern()
            patterns.add(pattern_type)
        
        # Should have at least 5 different patterns
        self.assertGreaterEqual(len(patterns), 5)
    
    def test_realistic_names(self):
        """Test that generated names are from predefined pools"""
        for _ in range(50):
            _, base = RealisticNamePool.get_realistic_pattern()
            
            # Should contain at least one name component
            has_first = any(name in base for name in RealisticNamePool.FIRST_NAMES)
            has_last = any(name in base for name in RealisticNamePool.LAST_NAMES)
            has_modifier = any(mod in base for mod in RealisticNamePool.MODIFIERS)
            
            self.assertTrue(has_first or has_last or has_modifier)


class TestCryptoNumberGenerator(unittest.TestCase):
    """Test cryptographic number generation"""
    
    def test_year_suffix_range(self):
        """Test year suffix is in valid range"""
        for _ in range(50):
            year_str = CryptoNumberGenerator.get_realistic_suffix('year')
            year = int(year_str)
            self.assertGreaterEqual(year, 1975)
            self.assertLessEqual(year, 2006)
    
    def test_short_suffix_range(self):
        """Test short suffix is in valid range"""
        for _ in range(50):
            short_str = CryptoNumberGenerator.get_realistic_suffix('short')
            short = int(short_str)
            self.assertGreaterEqual(short, 1)
            self.assertLessEqual(short, 999)
    
    def test_date_suffix_format(self):
        """Test date suffix has correct format"""
        for _ in range(50):
            date_str = CryptoNumberGenerator.get_realistic_suffix('date')
            self.assertEqual(len(date_str), 4)
            self.assertTrue(date_str.isdigit())
    
    def test_random_digits(self):
        """Test random digit generation"""
        for length in [2, 3, 4, 5]:
            digits = CryptoNumberGenerator.get_random_digits(length)
            self.assertEqual(len(digits), length)
            self.assertTrue(digits.isdigit())


class TestUniqueSessionCache(unittest.TestCase):
    """Test unique email caching"""
    
    def test_uniqueness_check(self):
        """Test basic uniqueness checking"""
        cache = UniqueSessionCache()
        
        email = "test@gmail.com"
        self.assertTrue(cache.is_unique(email))
        self.assertFalse(cache.is_unique(email))  # Second time should fail
    
    def test_collision_counting(self):
        """Test collision counting"""
        cache = UniqueSessionCache()
        
        email = "test@gmail.com"
        cache.is_unique(email)
        cache.is_unique(email)
        cache.is_unique(email)
        
        self.assertEqual(cache.collision_count, 2)
    
    def test_thread_safety(self):
        """Test cache thread safety"""
        cache = UniqueSessionCache()
        unique_count = [0]
        lock = threading.Lock()
        
        def worker():
            count = 0
            for i in range(100):
                email = f"test{i}@gmail.com"
                if cache.is_unique(email):
                    count += 1
            
            with lock:
                unique_count[0] += count
        
        threads = [threading.Thread(target=worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Each email should be unique exactly once
        self.assertEqual(unique_count[0], 100)
    
    def test_cache_size(self):
        """Test cache size tracking"""
        cache = UniqueSessionCache()
        
        for i in range(100):
            cache.is_unique(f"test{i}@gmail.com")
        
        self.assertEqual(cache.size(), 100)


class TestRFC5322Validator(unittest.TestCase):
    """Test RFC-5322 validation"""
    
    def test_valid_emails(self):
        """Test that valid emails pass validation"""
        valid_emails = [
            'test@gmail.com',
            'user.name@example.com',
            'firstname.lastname@company.co.uk',
            'user_123@test-domain.com',
            'a@b.co',
            'test.email.with.multiple.dots@example.com'
        ]
        
        for email in valid_emails:
            self.assertTrue(
                RFC5322Validator.validate(email),
                f"{email} should be valid"
            )
    
    def test_invalid_emails(self):
        """Test that invalid emails fail validation"""
        invalid_emails = [
            '',  # Empty
            'notanemail',  # No @
            '@example.com',  # No local part
            'test@',  # No domain
            'test..user@gmail.com',  # Consecutive dots
            '.test@gmail.com',  # Leading dot
            'test.@gmail.com',  # Trailing dot
            'test@domain',  # No TLD
            'a' * 65 + '@gmail.com',  # Local part too long
            'test@' + 'a' * 254 + '.com',  # Domain too long
        ]
        
        for email in invalid_emails:
            self.assertFalse(
                RFC5322Validator.validate(email),
                f"{email} should be invalid"
            )
    
    def test_length_limits(self):
        """Test RFC-5322 length limits"""
        # Max total length
        too_long = 'a' * 255 + '@gmail.com'
        self.assertFalse(RFC5322Validator.validate(too_long))
        
        # Max local part (64 is max, so 65 should fail)
        long_local = 'a' * 65 + '@gmail.com'
        self.assertFalse(RFC5322Validator.validate(long_local))
        
        # Exactly 64 should be valid
        exact_64 = 'a' * 64 + '@gmail.com'
        self.assertTrue(RFC5322Validator.validate(exact_64))
        
        # Valid length
        valid = 'a' * 50 + '@gmail.com'
        self.assertTrue(RFC5322Validator.validate(valid))


class TestEmailGeneratorUltra(unittest.TestCase):
    """Test ultra high-performance generator"""
    
    def setUp(self):
        """Create fresh generator for each test"""
        self.generator = EmailGeneratorUltra()
    
    def test_generate_single(self):
        """Test single email generation"""
        result = self.generator.generate_single()
        
        self.assertIn('email', result)
        self.assertIn('is_valid', result)
        self.assertIn('generation_time_ms', result)
        self.assertTrue(result['is_valid'])
        self.assertTrue('@' in result['email'])
    
    def test_generation_speed(self):
        """Test that generation meets <1ms target"""
        result = self.generator.generate_single()
        
        # Should be < 1ms
        self.assertLess(
            result['generation_time_ms'], 
            1.0,
            f"Generation took {result['generation_time_ms']}ms (target: <1ms)"
        )
    
    def test_batch_generation(self):
        """Test batch generation"""
        count = 100
        result = self.generator.generate_batch(count)
        
        self.assertEqual(result['count'], count)
        self.assertEqual(len(result['emails']), count)
        self.assertTrue(result['performance']['target_met'])
    
    def test_batch_uniqueness(self):
        """Test that batch generates unique emails"""
        count = 1000
        result = self.generator.generate_batch(count)
        
        emails = result['emails']
        unique_emails = set(emails)
        
        # Should have no duplicates
        self.assertEqual(len(emails), len(unique_emails))
        self.assertEqual(result['quality']['duplicates_avoided'], 0)
    
    def test_large_batch_performance(self):
        """Test performance with 10,000 emails"""
        count = 10000
        start = time.perf_counter()
        result = self.generator.generate_batch(count)
        end = time.perf_counter()
        
        total_time_s = end - start
        avg_time_ms = (total_time_s * 1000) / count
        
        self.assertEqual(result['count'], count)
        self.assertLess(avg_time_ms, 1.0, f"Avg time {avg_time_ms}ms exceeds 1ms target")
        
        # Should complete in reasonable time
        self.assertLess(total_time_s, 20, "10K emails should complete in <20s")
    
    def test_rfc5322_compliance(self):
        """Test all generated emails are RFC-5322 compliant"""
        result = self.generator.generate_batch(100)
        
        for email in result['emails']:
            self.assertTrue(
                RFC5322Validator.validate(email),
                f"{email} is not RFC-5322 compliant"
            )
    
    def test_domain_distribution(self):
        """Test domain rotation works correctly"""
        result = self.generator.generate_batch(100)
        
        domains = [email.split('@')[1] for email in result['emails']]
        unique_domains = set(domains)
        
        # Should have multiple domains
        self.assertGreater(len(unique_domains), 3)
        
        # Check stats
        stats = result['domain_stats']
        self.assertIn('total_domains', stats)
        self.assertIn('usage_distribution', stats)
    
    def test_threaded_generation(self):
        """Test multi-threaded generation"""
        count = 1000
        result = self.generator.generate_batch_threaded(count, num_threads=4)
        
        self.assertEqual(result['count'], count)
        self.assertEqual(len(result['emails']), count)
        
        # Check uniqueness
        unique_emails = set(result['emails'])
        self.assertEqual(len(unique_emails), count, "Thread collision detected")
    
    def test_metrics_tracking(self):
        """Test metrics are tracked correctly"""
        self.generator.generate_batch(50)
        self.generator.generate_batch(50)
        
        metrics = self.generator.get_metrics()
        
        self.assertEqual(metrics['total_generated'], 100)
        self.assertGreater(metrics['total_time_ms'], 0)
        self.assertEqual(metrics['unique_count'], 100)
    
    def test_cache_reset(self):
        """Test cache reset functionality"""
        self.generator.generate_batch(100)
        self.assertGreater(self.generator.unique_cache.size(), 0)
        
        self.generator.reset_cache()
        self.assertEqual(self.generator.unique_cache.size(), 0)
    
    def test_realistic_patterns(self):
        """Test that emails look realistic"""
        result = self.generator.generate_batch(100)
        
        # Check patterns
        patterns_found = {
            'dot': 0,
            'underscore': 0,
            'number': 0
        }
        
        for email in result['emails']:
            local = email.split('@')[0]
            if '.' in local:
                patterns_found['dot'] += 1
            if '_' in local:
                patterns_found['underscore'] += 1
            if any(c.isdigit() for c in local):
                patterns_found['number'] += 1
        
        # Should have variety
        self.assertGreater(patterns_found['dot'], 10)
        self.assertGreater(patterns_found['number'], 40)  # ~70% have numbers


class TestGlobalInstance(unittest.TestCase):
    """Test global instance functionality"""
    
    def test_global_instance(self):
        """Test get_ultra_generator returns same instance"""
        gen1 = get_ultra_generator()
        gen2 = get_ultra_generator()
        
        self.assertIs(gen1, gen2)
    
    def test_global_instance_with_domains(self):
        """Test global instance with custom domains"""
        domains = ['test1.com', 'test2.com']
        gen = get_ultra_generator(domains)
        
        result = gen.generate_batch(10)
        email_domains = [e.split('@')[1] for e in result['emails']]
        
        # Should only use specified domains
        for domain in email_domains:
            self.assertIn(domain, domains)


class TestStressTest(unittest.TestCase):
    """Stress tests for extreme scenarios"""
    
    def test_extreme_batch_100k(self):
        """Test generating 100,000 emails"""
        generator = EmailGeneratorUltra()
        count = 100000
        
        start = time.perf_counter()
        result = generator.generate_batch(count)
        end = time.perf_counter()
        
        total_time = end - start
        
        self.assertEqual(result['count'], count)
        self.assertLess(total_time, 200, "100K emails should complete in <200s")
        
        # Check uniqueness
        self.assertEqual(result['quality']['unique_count'], count)
    
    def test_concurrent_generation(self):
        """Test multiple generators running concurrently"""
        results = []
        lock = threading.Lock()
        
        def worker():
            gen = EmailGeneratorUltra()
            result = gen.generate_batch(100)
            with lock:
                results.append(result)
        
        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Should have 10 results
        self.assertEqual(len(results), 10)
        
        # Each should have 100 emails
        for result in results:
            self.assertEqual(result['count'], 100)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
