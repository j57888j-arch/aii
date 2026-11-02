from __future__ import annotations

import asyncio
import logging
import secrets
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from aiogram.types import Update
from pydantic import ValidationError
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine

from app.bot.factory import build_bot, build_dispatcher
from app.config import Settings, get_settings
from app.db.session import build_engine, build_session_factory, database_is_ready
from app.logging import RequestIdMiddleware, configure_logging

logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None) -> FastAPI:
    config = settings or get_settings()

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        config.validate_runtime()
        configure_logging(config.log_level)
        engine: AsyncEngine = build_engine(config)
        session_factory = build_session_factory(engine)
        redis_client = Redis.from_url(
            config.redis_url_value,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            health_check_interval=30,
        )
        bot = build_bot(config)
        dispatcher = build_dispatcher(config, session_factory, redis_client)
        application.state.settings = config
        application.state.engine = engine
        application.state.session_factory = session_factory
        application.state.redis = redis_client
        application.state.bot = bot
        application.state.dispatcher = dispatcher
        polling_task: asyncio.Task[Any] | None = None

        try:
            if config.mode == "webhook":
                await bot.set_webhook(
                    url=config.webhook_url,
                    secret_token=config.webhook_header_secret,
                    allowed_updates=dispatcher.resolve_used_update_types(),
                    drop_pending_updates=False,
                )
                logger.info("Telegram webhook configured")
            else:
                await bot.delete_webhook(drop_pending_updates=True)
                polling_task = asyncio.create_task(
                    dispatcher.start_polling(
                        bot,
                        handle_signals=False,
                        close_bot_session=False,
                        allowed_updates=dispatcher.resolve_used_update_types(),
                    ),
                    name="telegram-polling",
                )
                logger.info("Telegram polling started")
            yield
        finally:
            if polling_task is not None:
                await dispatcher.stop_polling()
                try:
                    await asyncio.wait_for(polling_task, timeout=10)
                except (TimeoutError, asyncio.CancelledError):
                    polling_task.cancel()
                    await asyncio.gather(polling_task, return_exceptions=True)
            try:
                # RedisStorage owns the Redis client passed to it and closes it here.
                await dispatcher.storage.close()
            finally:
                await bot.session.close()
                await engine.dispose()
                logger.info("StudyHelper resources closed")

    application = FastAPI(
        title=config.app_name,
        version="0.1.0",
        docs_url=None if config.app_env == "production" else "/docs",
        redoc_url=None if config.app_env == "production" else "/redoc",
        lifespan=lifespan,
    )
    application.add_middleware(RequestIdMiddleware)

    @application.get("/")
    async def root() -> dict[str, str]:
        return {"app": config.app_name, "status": "running", "phase": "foundation"}

    @application.get("/health")
    async def health() -> dict[str, str]:
        # Process liveness only. Use this lightweight endpoint for UptimeRobot.
        return {"status": "ok"}

    @application.get("/ready")
    async def ready(request: Request) -> JSONResponse:
        engine = getattr(request.app.state, "engine", None)
        redis_client = getattr(request.app.state, "redis", None)
        db_ok = False
        redis_ok = False
        if engine is not None:
            db_ok = await database_is_ready(request.app.state.session_factory)
        if redis_client is not None:
            try:
                redis_ok = bool(await redis_client.ping())
            except Exception:
                redis_ok = False
        status_code = 200 if db_ok and redis_ok else 503
        return JSONResponse(
            status_code=status_code,
            content={"status": "ready" if status_code == 200 else "not_ready", "postgres": db_ok, "redis": redis_ok},
        )

    @application.post("/telegram/webhook/{path_secret}")
    async def telegram_webhook(
        path_secret: str,
        request: Request,
        x_telegram_bot_api_secret_token: str | None = Header(default=None),
    ) -> dict[str, bool]:
        if config.mode != "webhook":
            raise HTTPException(status_code=404, detail="Not found")
        expected_path = config.webhook_path_secret.get_secret_value() if config.webhook_path_secret else ""
        if not secrets.compare_digest(path_secret, expected_path):
            raise HTTPException(status_code=404, detail="Not found")
        if not x_telegram_bot_api_secret_token or not secrets.compare_digest(
            x_telegram_bot_api_secret_token, config.webhook_header_secret
        ):
            raise HTTPException(status_code=403, detail="Forbidden")
        try:
            payload = await request.json()
            update = Update.model_validate(payload, context={"bot": request.app.state.bot})
        except (ValueError, ValidationError) as exc:
            raise HTTPException(status_code=400, detail="Invalid update payload") from exc
        await request.app.state.dispatcher.feed_update(request.app.state.bot, update)
        return {"ok": True}

    return application


app = create_app()
