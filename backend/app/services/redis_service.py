import json
import logging
from typing import Optional, List, Any
import redis.asyncio as redis
from app.config import settings

logger = logging.getLogger(__name__)

# Singleton redis client
_redis_client: Optional[redis.Redis] = None

def get_redis_client() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _redis_client

async def get_notes_cache(user_id: str) -> Optional[List[Dict[str, Any]]]:
    """
    Get notes list from cache. Returns None on miss.
    """
    try:
        client = get_redis_client()
        key = f"notes:{user_id}"
        data = await client.get(key)
        if data:
            logger.info(f"Cache hit for notes:{user_id}")
            return json.loads(data)
    except Exception as e:
        logger.warning(f"Redis read failed: {e}")
    return None

async def set_notes_cache(user_id: str, notes: List[Any]) -> None:
    """
    Cache notes list with TTL.
    """
    try:
        client = get_redis_client()
        key = f"notes:{user_id}"
        # We need a custom encoder or handle objects before this in a real app
        # but for this logic we assume 'notes' is a serializable list
        await client.set(key, json.dumps(notes), ex=settings.CACHE_TTL_SECONDS)
        logger.info(f"Cache set for notes:{user_id}")
    except Exception as e:
        logger.warning(f"Redis write failed: {e}")

async def invalidate_notes_cache(user_id: str) -> None:
    """
    Delete notes cache for user.
    """
    try:
        client = get_redis_client()
        key = f"notes:{user_id}"
        await client.delete(key)
        logger.info(f"Cache invalidated for notes:{user_id}")
    except Exception as e:
        logger.warning(f"Redis delete failed: {e}")

async def check_rate_limit(user_id: str, action: str) -> bool:
    """
    Check if user is within rate limits for action.
    Returns True if allowed, False if limited.
    """
    try:
        client = get_redis_client()
        key = f"ratelimit:{action}:{user_id}"
        
        # Increment and set TTL if new
        count = await client.incr(key)
        if count == 1:
            await client.expire(key, 60)
            
        limit = settings.RATE_LIMIT_TRANSCRIBE if action == "transcribe" else 30
        return count <= limit
    except Exception as e:
        logger.warning(f"Rate limit check failed: {e}")
        return True # Fail open to not block users on Redis error
