from __future__ import annotations

from functools import lru_cache
from typing import Literal
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from pydantic import SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_ignore_empty=True,
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "StudyHelper"
    app_env: Literal["development", "staging", "production"] = "development"
    mode: Literal["webhook", "polling"] = "polling"
    host: str = "0.0.0.0"
    port: int = 10000
    log_level: str = "INFO"

    bot_token: SecretStr | None = None
    admin_ids: str = ""

    database_url: str | None = None
    redis_url: SecretStr | None = None
    db_pool_size: int = 2
    db_max_overflow: int = 1
    db_pool_timeout: int = 10

    webhook_base_url: str | None = None
    webhook_secret_token: SecretStr | None = None
    webhook_path_secret: SecretStr | None = None

    default_language: Literal["uz", "ru", "en"] = "uz"
    business_timezone: str = "Asia/Tashkent"
    throttle_limit: int = 5
    throttle_window_seconds: int = 3
    fsm_ttl_seconds: int = 86_400

    @field_validator("port", "db_pool_size", "db_pool_timeout")
    @classmethod
    def positive_integer(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("qiymat 0 dan katta bo'lishi kerak")
        return value

    @field_validator("db_max_overflow")
    @classmethod
    def non_negative_overflow(cls, value: int) -> int:
        if value < 0:
            raise ValueError("DB_MAX_OVERFLOW manfiy bo'lishi mumkin emas")
        return value

    @property
    def admin_id_set(self) -> frozenset[int]:
        raw = self.admin_ids.strip()
        if not raw:
            return frozenset()
        try:
            return frozenset(int(part.strip()) for part in raw.split(",") if part.strip())
        except ValueError as exc:
            raise ValueError("ADMIN_IDS vergul bilan ajratilgan integer ID bo'lishi kerak") from exc

    @property
    def database_url_async(self) -> str:
        if not self.database_url:
            raise ValueError("DATABASE_URL sozlanmagan")
        raw = self.database_url.strip()
        if raw.startswith("postgres://"):
            raw = "postgresql://" + raw.removeprefix("postgres://")
        if raw.startswith("postgresql://"):
            raw = raw.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif raw.startswith("postgresql+psycopg://"):
            raw = raw.replace("postgresql+psycopg://", "postgresql+asyncpg://", 1)
        if not raw.startswith("postgresql+asyncpg://"):
            raise ValueError("DATABASE_URL PostgreSQL URL bo'lishi kerak")

        # asyncpg expects `ssl`; hosted providers often supply libpq's `sslmode`.
        parts = urlsplit(raw)
        query = parse_qsl(parts.query, keep_blank_values=True)
        sslmode = next((v for k, v in query if k == "sslmode"), None)
        if sslmode and not any(k == "ssl" for k, _ in query):
            query = [(k, v) for k, v in query if k != "sslmode"]
            if sslmode not in {"disable", "allow", "prefer"}:
                query.append(("ssl", "require"))
            raw = urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))
        return raw

    @property
    def redis_url_value(self) -> str:
        if not self.redis_url:
            raise ValueError("REDIS_URL sozlanmagan")
        return self.redis_url.get_secret_value().strip()

    @property
    def bot_token_value(self) -> str:
        if not self.bot_token:
            raise ValueError("BOT_TOKEN sozlanmagan")
        return self.bot_token.get_secret_value().strip()

    @property
    def webhook_url(self) -> str:
        if not self.webhook_base_url or not self.webhook_path_secret:
            raise ValueError("WEBHOOK_BASE_URL va WEBHOOK_PATH_SECRET talab qilinadi")
        base = self.webhook_base_url.rstrip("/")
        path = self.webhook_path_secret.get_secret_value().strip()
        return f"{base}/telegram/webhook/{path}"

    @property
    def webhook_header_secret(self) -> str:
        if not self.webhook_secret_token:
            raise ValueError("WEBHOOK_SECRET_TOKEN sozlanmagan")
        return self.webhook_secret_token.get_secret_value().strip()

    def validate_runtime(self) -> None:
        _ = self.bot_token_value
        _ = self.database_url_async
        _ = self.redis_url_value
        _ = self.admin_id_set
        if self.mode == "webhook":
            _ = self.webhook_url
            secret = self.webhook_header_secret
            allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")
            if not 1 <= len(secret) <= 256 or not set(secret) <= allowed:
                raise ValueError("WEBHOOK_SECRET_TOKEN Telegram ruxsat bergan formatda bo'lishi kerak")
            if not self.webhook_base_url or not self.webhook_base_url.startswith("https://"):
                raise ValueError("WEBHOOK_BASE_URL HTTPS bo'lishi shart")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
