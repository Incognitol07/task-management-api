# app/utils/redis_cache.py:

from redis.asyncio import Redis
from .logging_config import logger

# Create a Redis client instance
redis_client = Redis(
    host="localhost",  # Adjust the host based on your Redis configuration
    port=6379,         # Default Redis port
    decode_responses=True  # Decode byte responses to strings
)

import json

async def set_cache(key: str, value: any, expire: int = 3600):
    """
    Set a cache value in Redis with serialization.
    """
    try:
        # Serialize the value to JSON string before storing it in Redis
        serialized_value = json.dumps(value)
        await redis_client.set(key, serialized_value, ex=expire)
    except Exception as e:
        logger.error(f"Error setting cache for key {key}: {e}")
        raise


async def get_cache(key: str) -> str | None:
    """
    Retrieve a cached value from Redis.

    Args:
        key (str): Cache key.

    Returns:
        str | None: Cached value, or None if the key doesn't exist.
    """
    return await redis_client.get(key)

async def delete_cache(key: str):
    """
    Delete a cached value from Redis.

    Args:
        key (str): Cache key.
    """
    await redis_client.delete(key)
