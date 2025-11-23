"""
Cache Manager for Performance Optimization
Bi Tool v2.1 - In-memory caching with TTL
"""

import time
import hashlib
import json
from functools import wraps
from collections import OrderedDict
from datetime import datetime, timedelta
import threading

class CacheManager:
    """Simple in-memory cache with TTL and LRU eviction"""
    
    def __init__(self, max_size=1000, default_ttl=300):
        """
        Initialize cache manager
        
        Args:
            max_size: Maximum number of cache entries
            default_ttl: Default TTL in seconds (300 = 5 minutes)
        """
        self.cache = OrderedDict()
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.lock = threading.Lock()
        
        # Statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'evictions': 0,
            'expired': 0
        }
    
    def _generate_key(self, prefix, *args, **kwargs):
        """Generate cache key from function arguments"""
        # Create a string representation of args and kwargs
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_str = json.dumps(key_data, sort_keys=True)
        
        # Hash the key for consistent length
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        
        return f"{prefix}:{key_hash}"
    
    def get(self, key):
        """
        Get value from cache
        
        Returns:
            Value if found and not expired, None otherwise
        """
        with self.lock:
            if key not in self.cache:
                self.stats['misses'] += 1
                return None
            
            entry = self.cache[key]
            
            # Check if expired
            if time.time() > entry['expires_at']:
                del self.cache[key]
                self.stats['expired'] += 1
                self.stats['misses'] += 1
                return None
            
            # Move to end (LRU)
            self.cache.move_to_end(key)
            
            self.stats['hits'] += 1
            return entry['value']
    
    def set(self, key, value, ttl=None):
        """
        Set value in cache with TTL
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (None = use default)
        """
        if ttl is None:
            ttl = self.default_ttl
        
        with self.lock:
            # Evict oldest if at max size
            if len(self.cache) >= self.max_size and key not in self.cache:
                self.cache.popitem(last=False)
                self.stats['evictions'] += 1
            
            # Store with expiry time
            self.cache[key] = {
                'value': value,
                'expires_at': time.time() + ttl,
                'created_at': time.time()
            }
            
            # Move to end (most recently used)
            self.cache.move_to_end(key)
    
    def delete(self, key):
        """Delete a specific key from cache"""
        with self.lock:
            if key in self.cache:
                del self.cache[key]
                return True
            return False
    
    def clear(self):
        """Clear all cache entries"""
        with self.lock:
            self.cache.clear()
            # Don't reset stats
    
    def cleanup_expired(self):
        """Remove all expired entries"""
        current_time = time.time()
        expired_keys = []
        
        with self.lock:
            for key, entry in self.cache.items():
                if current_time > entry['expires_at']:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.cache[key]
                self.stats['expired'] += 1
        
        return len(expired_keys)
    
    def get_stats(self):
        """Get cache statistics"""
        with self.lock:
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'size': len(self.cache),
                'max_size': self.max_size,
                'hits': self.stats['hits'],
                'misses': self.stats['misses'],
                'hit_rate': round(hit_rate, 2),
                'evictions': self.stats['evictions'],
                'expired': self.stats['expired'],
                'total_requests': total_requests
            }
    
    def get_info(self, key):
        """Get information about a cached entry"""
        with self.lock:
            if key not in self.cache:
                return None
            
            entry = self.cache[key]
            current_time = time.time()
            
            return {
                'key': key,
                'exists': True,
                'expired': current_time > entry['expires_at'],
                'ttl_remaining': max(0, entry['expires_at'] - current_time),
                'age': current_time - entry['created_at'],
                'created_at': datetime.fromtimestamp(entry['created_at']).isoformat(),
                'expires_at': datetime.fromtimestamp(entry['expires_at']).isoformat()
            }

# Global cache instance
cache = CacheManager(max_size=1000, default_ttl=300)

def cached(ttl=300, key_prefix='cache'):
    """
    Decorator for caching function results
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Prefix for cache key
        
    Usage:
        @cached(ttl=60, key_prefix='user_data')
        def get_user(user_id):
            return database_query(user_id)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache._generate_key(key_prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl=ttl)
            
            return result
        
        # Add cache control methods
        wrapper.cache_clear = lambda: cache.delete(
            cache._generate_key(key_prefix, *args, **kwargs)
        )
        wrapper.cache_info = lambda: cache.get_info(
            cache._generate_key(key_prefix, *args, **kwargs)
        )
        
        return wrapper
    
    return decorator

class QueryCache:
    """Specialized cache for database queries"""
    
    def __init__(self, cache_manager):
        self.cache = cache_manager
    
    def cache_query(self, query_name, query_func, ttl=300, *args, **kwargs):
        """
        Cache a database query result
        
        Args:
            query_name: Unique name for the query
            query_func: Function that executes the query
            ttl: Time to live
            *args, **kwargs: Arguments for query_func
        """
        cache_key = self.cache._generate_key(f'query:{query_name}', *args, **kwargs)
        
        # Try cache first
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Execute query
        result = query_func(*args, **kwargs)
        
        # Cache result
        self.cache.set(cache_key, result, ttl=ttl)
        
        return result
    
    def invalidate_query(self, query_name, *args, **kwargs):
        """Invalidate cached query"""
        cache_key = self.cache._generate_key(f'query:{query_name}', *args, **kwargs)
        return self.cache.delete(cache_key)
    
    def invalidate_pattern(self, pattern):
        """Invalidate all queries matching a pattern"""
        with self.cache.lock:
            keys_to_delete = [
                key for key in self.cache.cache.keys()
                if pattern in key
            ]
            
            for key in keys_to_delete:
                del self.cache.cache[key]
        
        return len(keys_to_delete)

# Global query cache
query_cache = QueryCache(cache)

class SessionCache:
    """Cache for user session data"""
    
    def __init__(self, cache_manager):
        self.cache = cache_manager
    
    def get_session_data(self, session_token):
        """Get cached session data"""
        key = f"session:{session_token}"
        return self.cache.get(key)
    
    def set_session_data(self, session_token, data, ttl=3600):
        """Cache session data (default 1 hour)"""
        key = f"session:{session_token}"
        self.cache.set(key, data, ttl=ttl)
    
    def delete_session(self, session_token):
        """Delete cached session"""
        key = f"session:{session_token}"
        return self.cache.delete(key)

# Global session cache
session_cache = SessionCache(cache)

class StatsCache:
    """Cache for statistical data"""
    
    def __init__(self, cache_manager):
        self.cache = cache_manager
    
    def get_stats(self, stat_name):
        """Get cached statistics"""
        key = f"stats:{stat_name}"
        return self.cache.get(key)
    
    def set_stats(self, stat_name, data, ttl=60):
        """Cache statistics (default 1 minute)"""
        key = f"stats:{stat_name}"
        self.cache.set(key, data, ttl=ttl)
    
    def invalidate_stats(self, stat_name=None):
        """Invalidate statistics cache"""
        if stat_name:
            key = f"stats:{stat_name}"
            return self.cache.delete(key)
        else:
            # Invalidate all stats
            return query_cache.invalidate_pattern('stats:')

# Global stats cache
stats_cache = StatsCache(cache)

# Cleanup scheduler (run periodically)
def start_cache_cleanup_scheduler(interval=300):
    """
    Start background thread to cleanup expired cache entries
    
    Args:
        interval: Cleanup interval in seconds (default 5 minutes)
    """
    def cleanup_task():
        while True:
            time.sleep(interval)
            expired_count = cache.cleanup_expired()
            if expired_count > 0:
                print(f"✨ Cache cleanup: Removed {expired_count} expired entries")
    
    thread = threading.Thread(target=cleanup_task, daemon=True)
    thread.start()
    print(f"✅ Cache cleanup scheduler started (interval: {interval}s)")

# Example usage:
"""
# Using decorator
@cached(ttl=60, key_prefix='user_list')
def get_all_users():
    # Expensive database query
    return database.query('SELECT * FROM users')

# Using query cache
def get_user_stats(user_id):
    return query_cache.cache_query(
        'user_stats',
        lambda: database.query('SELECT * FROM stats WHERE user_id = ?', user_id),
        ttl=300,
        user_id=user_id
    )

# Using session cache
session_data = session_cache.get_session_data(session_token)
if not session_data:
    session_data = load_from_database(session_token)
    session_cache.set_session_data(session_token, session_data)

# Using stats cache
stats = stats_cache.get_stats('dashboard_overview')
if not stats:
    stats = calculate_dashboard_stats()
    stats_cache.set_stats('dashboard_overview', stats, ttl=60)

# Get cache statistics
print(cache.get_stats())

# Clear specific cache
cache.delete('user_list:abc123')

# Clear all cache
cache.clear()
"""
