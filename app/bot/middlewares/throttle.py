from __future__ import annotations

import asyncio
import logging
import time
from collections import OrderedDict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from redis.exceptions import RedisError

from app.core.i18n.loader import translate

logger = logging.getLogger(__name__)
_INCREMENT_WITH_TTL = "local n = redis.call('INCR', KEYS[1]); if n == 1 then redis.call('EXPIRE', KEYS[1], ARGV[1]); end; return n"


class ThrottleMiddleware(BaseMiddleware):
    def __init__(self, redis_client, limit: int = 5, window_seconds: int = 3, max_fallback_keys: int = 10_000):
        self.redis = redis_client
        self.limit = limit
        self.window_seconds = window_seconds
        self.max_fallback_keys = max_fallback_keys
        self._fallback: OrderedDict[str, tuple[int, float]] = OrderedDict()
        self._lock = asyncio.Lock()

    async def _fallback_count(self, key: str) -> int:
        now = time.monotonic()
        async with self._lock:
            current = self._fallback.get(key)
            if current is None or current[1] <= now:
                value = (1, now + self.window_seconds)
            else:
                value = (current[0] + 1, current[1])
            self._fallback[key] = value
            self._fallback.move_to_end(key)
            while len(self._fallback) > self.max_fallback_keys:
                self._fallback.popitem(last=False)
            return value[0]

    async def __call__(self, handler, event, data):
        telegram_user = getattr(event, "from_user", None)
        if telegram_user is None:
            return await handler(event, data)
        event_name = "callback" if isinstance(event, CallbackQuery) else "message"
        key = f"studyhelper:throttle:{event_name}:{telegram_user.id}"
        try:
            count = int(await self.redis.eval(_INCREMENT_WITH_TTL, 1, key, self.window_seconds))
        except RedisError:
            logger.warning("Redis throttle unavailable; using bounded local fallback")
            count = await self._fallback_count(key)
        if count > self.limit:
            language = data.get("language", "uz")
            notice = translate(language, "too_fast")
            if isinstance(event, CallbackQuery):
                await event.answer(notice, show_alert=True)
            elif isinstance(event, Message):
                await event.answer(notice)
            return None
        return await handler(event, data)
