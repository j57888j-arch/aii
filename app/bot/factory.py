from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from app.bot.middlewares.ban_check import BanCheckMiddleware
from app.bot.middlewares.db_session import DbSessionMiddleware
from app.bot.middlewares.error_boundary import ErrorBoundaryMiddleware
from app.bot.middlewares.i18n import I18nMiddleware
from app.bot.middlewares.throttle import ThrottleMiddleware
from app.bot.middlewares.user_loader import UserLoaderMiddleware
from app.bot.routers.menu import router as menu_router
from app.bot.routers.start import router as start_router
from app.config import Settings


def build_bot(settings: Settings) -> Bot:
    return Bot(
        token=settings.bot_token_value,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def build_dispatcher(
    settings: Settings,
    session_factory: async_sessionmaker[AsyncSession],
    redis_client: Redis,
) -> Dispatcher:
    storage = RedisStorage(
        redis=redis_client,
        state_ttl=settings.fsm_ttl_seconds,
        data_ttl=settings.fsm_ttl_seconds,
    )
    dispatcher = Dispatcher(storage=storage)
    dispatcher.update.outer_middleware(ErrorBoundaryMiddleware())

    for observer in (dispatcher.message, dispatcher.callback_query):
        observer.outer_middleware(DbSessionMiddleware(session_factory))
        observer.outer_middleware(UserLoaderMiddleware())
        observer.outer_middleware(I18nMiddleware())
        observer.outer_middleware(BanCheckMiddleware())
        observer.outer_middleware(
            ThrottleMiddleware(
                redis_client,
                limit=settings.throttle_limit,
                window_seconds=settings.throttle_window_seconds,
            )
        )

    dispatcher.include_routers(start_router, menu_router)
    return dispatcher
