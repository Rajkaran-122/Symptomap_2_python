from functools import wraps
import json
from fastapi import Request, Response
from app.core.redis import redis_client
import hashlib
from typing import Optional, Callable

def cache_response(ttl_seconds: int = 300):
    """
    Decorator to cache FastAPI response in Redis (or MockRedis).
    TTL default: 5 minutes.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 1. Generate Cache Key
            # We need to construct a key based on the route and query params
            # args[0] might not be Request if used in a certain way, so let's find it 
            # or rely on kwargs. FastAPI usually passes dependencies as kwargs.
            # Actually, simpler: use the function name + crucial kwargs.
            # But specific query params matter (like ?limit=5).
            
            # Helper to find Request object if present (optional/advanced)
            # For simplicity, let's create a key string from function name and kwargs
            # We filter out 'db' session as it's not serializable/relevant for key
            
            key_parts = [func.__name__]
            for k, v in kwargs.items():
                if k != 'db': # Ignore database session
                    key_parts.append(f"{k}={v}")
            
            cache_key = f"cache:{':'.join(key_parts)}"
            
            # 2. Check Cache
            cached_data = await redis_client.get(cache_key)
            if cached_data:
                # print(f"⚡ Cache Hit: {cache_key}")
                try:
                    return json.loads(cached_data)
                except:
                    pass # Fallback to fresh fetch if stale/corrupt
            
            # 3. Fetch Fresh Data
            # print(f"🐢 Cache Miss: {cache_key}")
            response_data = await func(*args, **kwargs)
            
            # 4. Store in Cache
            try:
                # We assume response_data is JSON serializable (Dict or List)
                # FastAPI handles Pydantic, but here we likely return Dicts from our endpoints
                await redis_client.set(
                    cache_key,
                    json.dumps(response_data, default=str), # default=str handles datetime
                    ex=ttl_seconds
                )
            except Exception as e:
                print(f"⚠️ Cache Write Error: {e}")
                
            return response_data
            
        return wrapper
    return decorator
