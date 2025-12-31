"""
Redis client setup with Mock fallback
"""

import redis.asyncio as redis
from app.core.config import settings
import asyncio

class MockRedis:
    """In-memory Redis mock for local development"""
    def __init__(self):
        self.store = {}
        print("⚠️ Using In-Memory Mock Redis (Data will be lost on restart)")

    async def connect(self):
        pass

    async def disconnect(self):
        pass

    async def get(self, key):
        return self.store.get(key)
    
    async def set(self, key, value, ex=None):
        self.store[key] = value
        if ex:
             # In a real mock we'd handle expiry, but for MVP local test it's fine
             pass
    
    async def delete(self, key):
        if key in self.store:
            del self.store[key]
            
    async def exists(self, key):
        return 1 if key in self.store else 0


class RedisClient:
    """Async Redis client wrapper"""
    
    def __init__(self):
        self.redis = None
        self.use_mock = False
    
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=2  # Fast fail
            )
            await self.redis.ping()
            print("✅ Connected to Redis")
        except Exception as e:
            print(f"❌ Redis Connection Failed: {e}")
            print("🔄 Switching to Mock Redis...")
            self.use_mock = True
            self.redis = MockRedis()
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis and not self.use_mock:
            await self.redis.close()
    
    async def get(self, key: str) -> str:
        """Get value from Redis"""
        if not self.redis: await self.connect()
        return await self.redis.get(key)
    
    async def set(self, key: str, value: str, ex: int = None):
        """Set value in Redis with optional expiry"""
        if not self.redis: await self.connect()
        await self.redis.set(key, value, ex=ex)
    
    async def delete(self, key: str):
        """Delete key from Redis"""
        if not self.redis: await self.connect()
        await self.redis.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.redis: await self.connect()
        return await self.redis.exists(key)


redis_client = RedisClient()
