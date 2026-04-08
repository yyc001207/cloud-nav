import json
from typing import Optional, Any
import redis.asyncio as aioredis
from app.core.config import settings
from app.core.logger import logger


_redis_client: Optional[aioredis.Redis] = None


async def init_redis() -> None:
    global _redis_client
    _redis_client = aioredis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        encoding="utf-8",
    )
    await _redis_client.ping()
    logger.info("Redis 连接成功")


async def close_redis() -> None:
    global _redis_client
    if _redis_client:
        await _redis_client.close()
        logger.info("Redis 连接已关闭")


def get_redis() -> aioredis.Redis:
    if _redis_client is None:
        raise RuntimeError("Redis 未初始化")
    return _redis_client


async def cache_get(key: str) -> Optional[str]:
    client = get_redis()
    return await client.get(key)


async def cache_set(key: str, value: str, ttl: int = 300) -> None:
    client = get_redis()
    await client.setex(key, ttl, value)


async def cache_delete(key: str) -> None:
    client = get_redis()
    await client.delete(key)


async def cache_get_json(key: str) -> Optional[Any]:
    raw = await cache_get(key)
    if raw:
        return json.loads(raw)
    return None


async def cache_set_json(key: str, value: Any, ttl: int = 300) -> None:
    await cache_set(key, json.dumps(value, default=str), ttl)


async def is_token_blacklisted(token: str) -> bool:
    client = get_redis()
    return await client.exists(f"token_blacklist:{token}") > 0


async def blacklist_token(token: str, ttl: int = 86400) -> None:
    client = get_redis()
    await client.setex(f"token_blacklist:{token}", ttl, "1")
