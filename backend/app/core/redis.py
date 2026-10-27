"""Shared async Redis client — connection pooling handled by redis-py
itself; this just avoids every caller constructing its own client."""

from redis.asyncio import Redis

from app.core.config import settings

redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
