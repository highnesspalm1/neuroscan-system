"""
Advanced caching strategies and performance optimization
"""
import asyncio
import hashlib
import json
import time
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, timedelta
from functools import wraps
import redis.asyncio as redis
from redis.asyncio import Redis
import logging
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)

class CacheStrategy(Enum):
    """Cache strategy types"""
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"
    CACHE_ASIDE = "cache_aside"
    REFRESH_AHEAD = "refresh_ahead"

class EvictionPolicy(Enum):
    """Cache eviction policies"""
    LRU = "lru"
    LFU = "lfu"
    FIFO = "fifo"
    TTL = "ttl"

@dataclass
class CacheConfig:
    """Cache configuration"""
    default_ttl: int = 3600  # 1 hour
    max_size: int = 10000
    strategy: CacheStrategy = CacheStrategy.CACHE_ASIDE
    eviction_policy: EvictionPolicy = EvictionPolicy.LRU
    compression_threshold: int = 1024  # Compress if larger than 1KB
    enable_stats: bool = True
    namespace: str = "neuroscan"

@dataclass
class CacheStats:
    """Cache statistics"""
    hits: int = 0
    misses: int = 0
    sets: int = 0
    deletes: int = 0
    memory_usage: int = 0
    last_reset: datetime = None

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

class AdvancedCacheManager:
    """Advanced caching with multiple strategies and optimization"""
    
    def __init__(self, redis_client: Redis = None, config: CacheConfig = None):
        self.redis = redis_client
        self.config = config or CacheConfig()
        self.stats = CacheStats(last_reset=datetime.utcnow())
        self._local_cache = {}  # L1 cache
        self._cache_locks = {}
        self._redis_available = redis_client is not None
        
    def _get_key(self, key: str, namespace: str = None) -> str:
        """Generate namespaced cache key"""
        ns = namespace or self.config.namespace
        return f"{ns}:{key}"
    
    def _serialize_value(self, value: Any) -> bytes:
        """Serialize value with compression if needed"""
        serialized = json.dumps(value, default=str).encode('utf-8')
        
        if len(serialized) > self.config.compression_threshold:
            import gzip
            serialized = gzip.compress(serialized)
            
        return serialized
    
    def _deserialize_value(self, data: bytes) -> Any:
        """Deserialize value with decompression if needed"""
        try:
            # Try to decompress first
            import gzip
            decompressed = gzip.decompress(data)
            return json.loads(decompressed.decode('utf-8'))
        except:
            # If decompression fails, treat as uncompressed
            return json.loads(data.decode('utf-8'))
    
    async def get(self, key: str, namespace: str = None) -> Optional[Any]:
        """Get value from cache with L1/L2 strategy"""
        cache_key = self._get_key(key, namespace)
        
        # L1 cache check (local memory)
        if cache_key in self._local_cache:
            self.stats.hits += 1
            return self._local_cache[cache_key]
        
        # L2 cache check (Redis) - only if Redis is available
        if self._redis_available:
            try:
                data = await self.redis.get(cache_key)
                if data:
                    value = self._deserialize_value(data)
                    # Store in L1 cache
                    self._local_cache[cache_key] = value
                    self.stats.hits += 1
                    return value
                else:
                    self.stats.misses += 1
                    return None
            except Exception as e:
                logger.error(f"Cache get error for key {cache_key}: {e}")
                self.stats.misses += 1
                return None
        else:
            # Redis not available, only use L1 cache
            self.stats.misses += 1
            return None
    async def set(self, key: str, value: Any, ttl: int = None, namespace: str = None) -> bool:
        """Set value in cache with TTL"""
        cache_key = self._get_key(key, namespace)
        ttl = ttl or self.config.default_ttl
        
        try:
            # Always update L1 cache
            self._local_cache[cache_key] = value
            
            # Update L2 cache (Redis) only if available
            if self._redis_available:
                serialized = self._serialize_value(value)
                await self.redis.setex(cache_key, ttl, serialized)
            
            # Evict from L1 if too large
            if len(self._local_cache) > self.config.max_size:
                await self._evict_l1_cache()
            
            self.stats.sets += 1
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {cache_key}: {e}")
            return False
    async def delete(self, key: str, namespace: str = None) -> bool:
        """Delete value from cache"""
        cache_key = self._get_key(key, namespace)
        
        try:
            # Delete from Redis if available
            if self._redis_available:
                await self.redis.delete(cache_key)
            
            # Always delete from L1 cache
            self._local_cache.pop(cache_key, None)
            self.stats.deletes += 1
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {cache_key}: {e}")
            return False
    
    async def _evict_l1_cache(self):
        """Evict entries from L1 cache based on policy"""
        if self.config.eviction_policy == EvictionPolicy.LRU:
            # Simple LRU - remove oldest 25%
            to_remove = len(self._local_cache) // 4
            keys_to_remove = list(self._local_cache.keys())[:to_remove]
            for key in keys_to_remove:
                self._local_cache.pop(key, None)
    
    async def get_or_set(self, key: str, factory: Callable, ttl: int = None, namespace: str = None) -> Any:
        """Get value or set if not exists using factory function"""
        value = await self.get(key, namespace)
        if value is not None:
            return value
        
        # Use lock to prevent cache stampede
        cache_key = self._get_key(key, namespace)
        if cache_key not in self._cache_locks:
            self._cache_locks[cache_key] = asyncio.Lock()
        
        async with self._cache_locks[cache_key]:
            # Double-check after acquiring lock
            value = await self.get(key, namespace)
            if value is not None:
                return value
            
            # Generate value
            if asyncio.iscoroutinefunction(factory):
                value = await factory()
            else:
                value = factory()
            
            await self.set(key, value, ttl, namespace)
            return value
    
    async def mget(self, keys: List[str], namespace: str = None) -> Dict[str, Any]:
        """Get multiple values from cache"""
        cache_keys = [self._get_key(key, namespace) for key in keys]
        results = {}
        
        try:
            # Check L1 cache first
            l1_results = {}
            remaining_keys = []
            for i, cache_key in enumerate(cache_keys):
                if cache_key in self._local_cache:
                    l1_results[keys[i]] = self._local_cache[cache_key]
                else:
                    remaining_keys.append((keys[i], cache_key))
              # Get remaining from Redis (if available)
            if remaining_keys and self._redis_available:
                redis_keys = [ck for _, ck in remaining_keys]
                redis_values = await self.redis.mget(redis_keys)
                
                for i, ((orig_key, cache_key), data) in enumerate(zip(remaining_keys, redis_values)):
                    if data:
                        value = self._deserialize_value(data)
                        results[orig_key] = value
                        self._local_cache[cache_key] = value
                        self.stats.hits += 1
                    else:
                        self.stats.misses += 1
            
            results.update(l1_results)
            return results
            
        except Exception as e:
            logger.error(f"Cache mget error: {e}")
            return {}
    
    async def mset(self, data: Dict[str, Any], ttl: int = None, namespace: str = None) -> bool:
        """Set multiple values in cache"""
        ttl = ttl or self.config.default_ttl
        
        try:
            pipe = self.redis.pipeline()
            for key, value in data.items():
                cache_key = self._get_key(key, namespace)
                serialized = self._serialize_value(value)
                pipe.setex(cache_key, ttl, serialized)
                self._local_cache[cache_key] = value
            await pipe.execute()
            self.stats.sets += len(data)
            return True
        except Exception as e:
            logger.error(f"Cache mset error: {e}")
            return False
    
    async def invalidate_pattern(self, pattern: str, namespace: str = None) -> int:
        """Invalidate cache entries matching pattern"""
        pattern_key = self._get_key(pattern, namespace)
        
        try:
            keys = []
            
            # Get keys from Redis if available
            if self._redis_available:
                async for key in self.redis.scan_iter(match=pattern_key):
                    keys.append(key)
                
                if keys:
                    await self.redis.delete(*keys)
            
            # Remove from L1 cache (pattern matching)
            l1_keys_to_remove = [k for k in self._local_cache.keys() if pattern in k]
            for key in l1_keys_to_remove:
                self._local_cache.pop(key, None)
            
            total_removed = len(keys) + len(l1_keys_to_remove)
            self.stats.deletes += total_removed
            return total_removed
        except Exception as e:
            logger.error(f"Cache invalidate_pattern error for pattern {pattern}: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            if self._redis_available:
                redis_info = await self.redis.info('memory')
                self.stats.memory_usage = redis_info.get('used_memory', 0)
        except:
            pass
        
        return {
            **asdict(self.stats),
            'l1_cache_size': len(self._local_cache),
            'config': asdict(self.config),
            'redis_available': self._redis_available
        }
    
    async def clear_stats(self):
        """Clear cache statistics"""
        self.stats = CacheStats(last_reset=datetime.utcnow())
    
    async def initialize(self):
        """Initialize the cache manager"""
        logger.info("Cache manager initialized")
    
    async def cleanup(self):
        """Cleanup cache manager resources"""
        if self._redis_available and self.redis:
            try:
                await self.redis.close()
            except:
                pass
        logger.info("Cache manager cleanup completed")

# Cache decorators
def cache_result(ttl: int = 3600, namespace: str = None, key_generator: Callable = None):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, cache_manager: AdvancedCacheManager = None, **kwargs):
            if not cache_manager:
                return await func(*args, **kwargs)
            
            # Generate cache key
            if key_generator:
                cache_key = key_generator(*args, **kwargs)
            else:
                # Default key generation
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = hashlib.md5(":".join(key_parts).encode()).hexdigest()
            
            # Try to get from cache
            result = await cache_manager.get(cache_key, namespace)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_manager.set(cache_key, result, ttl, namespace)
            return result
        
        return wrapper
    return decorator

def invalidate_cache(pattern: str, namespace: str = None):
    """Decorator to invalidate cache after function execution"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, cache_manager: AdvancedCacheManager = None, **kwargs):
            result = await func(*args, **kwargs)
            if cache_manager:
                await cache_manager.invalidate_pattern(pattern, namespace)
            return result
        return wrapper
    return decorator

class CacheWarmupManager:
    """Cache warmup strategies"""
    
    def __init__(self, cache_manager: AdvancedCacheManager):
        self.cache_manager = cache_manager
        self.warmup_tasks = []
    
    async def register_warmup_task(self, name: str, task: Callable, schedule: str = "0 */6 * * *"):
        """Register a cache warmup task"""
        self.warmup_tasks.append({
            'name': name,
            'task': task,
            'schedule': schedule,
            'last_run': None
        })
    
    async def run_warmup_task(self, task_name: str):
        """Run a specific warmup task"""
        for task_info in self.warmup_tasks:
            if task_info['name'] == task_name:
                try:
                    logger.info(f"Running cache warmup task: {task_name}")
                    if asyncio.iscoroutinefunction(task_info['task']):
                        await task_info['task'](self.cache_manager)
                    else:
                        task_info['task'](self.cache_manager)
                    task_info['last_run'] = datetime.utcnow()
                    logger.info(f"Cache warmup task completed: {task_name}")
                except Exception as e:
                    logger.error(f"Cache warmup task failed {task_name}: {e}")
                break
    
    async def run_all_warmup_tasks(self):
        """Run all registered warmup tasks"""
        for task_info in self.warmup_tasks:
            await self.run_warmup_task(task_info['name'])
    
    def get_warmup_status(self) -> List[Dict]:
        """Get status of all warmup tasks"""
        return [
            {
                'name': task['name'],
                'schedule': task['schedule'],
                'last_run': task['last_run'].isoformat() if task['last_run'] else None
            }
            for task in self.warmup_tasks
        ]

# Usage example functions for common cache patterns
async def cache_user_session(cache_manager: AdvancedCacheManager, user_id: str, session_data: Dict) -> bool:
    """Cache user session data"""
    return await cache_manager.set(f"session:{user_id}", session_data, ttl=1800, namespace="auth")

async def get_cached_user_session(cache_manager: AdvancedCacheManager, user_id: str) -> Optional[Dict]:
    """Get cached user session"""
    return await cache_manager.get(f"session:{user_id}", namespace="auth")

async def cache_api_response(cache_manager: AdvancedCacheManager, endpoint: str, params: Dict, response: Any) -> bool:
    """Cache API response"""
    key = f"api:{endpoint}:{hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()}"
    return await cache_manager.set(key, response, ttl=300, namespace="api")

async def cache_database_query(cache_manager: AdvancedCacheManager, query_hash: str, result: Any, ttl: int = 600) -> bool:
    """Cache database query result"""
    return await cache_manager.set(f"query:{query_hash}", result, ttl=ttl, namespace="db")


# Global cache manager instance
try:
    # Try to create Redis client, fallback to None if Redis is not available
    redis_client = redis.Redis(host='localhost', port=6379, decode_responses=False)
    # Test connection (simplified check)
    try:
        # Simple sync test
        import redis as sync_redis
        sync_client = sync_redis.Redis(host='localhost', port=6379)
        sync_client.ping()
    except:
        redis_client = None
except Exception:
    # Redis not available, use a mock client or disable caching
    redis_client = None
    logger.warning("Redis not available, cache manager will operate in local-only mode")

# Always create cache manager, even without Redis
cache_manager = AdvancedCacheManager(redis_client)
