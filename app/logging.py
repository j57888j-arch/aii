from __future__ import annotations

import json
import logging
import re
import uuid
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any

from starlette.types import ASGIApp, Message, Receive, Scope, Send

request_id_var: ContextVar[str] = ContextVar("request_id", default="-")
_SECRET_KEY = re.compile(r"(token|password|secret|authorization|api[_-]?key)", re.IGNORECASE)
_CREDENTIAL_PATTERN = re.compile(
    r"(?i)(bot[0-9]{5,}:[A-Za-z0-9_-]{20,}|[0-9]{5,}:[A-Za-z0-9_-]{20,}|sk-ant-[A-Za-z0-9_-]{12,})"
)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        safe_message = _CREDENTIAL_PATTERN.sub("[REDACTED]", record.getMessage())
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": safe_message,
            "request_id": request_id_var.get(),
        }
        # Telegram user IDs and message content are intentionally excluded from logs.
        for key in ("update_id", "path", "status_code", "duration_ms"):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value
        if record.exc_info:
            payload["exception"] = _CREDENTIAL_PATTERN.sub("[REDACTED]", self.formatException(record.exc_info))
        return json.dumps(payload, ensure_ascii=False, default=str)


def redact_mapping(values: dict[str, Any]) -> dict[str, Any]:
    """Redact obvious secret-bearing fields before structured logging."""
    return {key: ("[REDACTED]" if _SECRET_KEY.search(key) else value) for key, value in values.items()}


def configure_logging(level: str = "INFO") -> None:
    root = logging.getLogger()
    root.handlers.clear()
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root.addHandler(handler)
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("aiogram.event").setLevel(logging.INFO)


class RequestIdMiddleware:
    """Pure ASGI request ID middleware; it does not buffer request or response bodies."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request_id = uuid.uuid4().hex
        for key, value in scope.get("headers", []):
            if key.lower() == b"x-request-id":
                candidate = value.decode("latin-1").strip()
                if re.fullmatch(r"[A-Za-z0-9_.-]{1,128}", candidate):
                    request_id = candidate
                break

        context_token = request_id_var.set(request_id)

        async def send_with_request_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((b"x-request-id", request_id.encode("ascii", errors="ignore")))
                message["headers"] = headers
            await send(message)

        try:
            await self.app(scope, receive, send_with_request_id)
        finally:
            request_id_var.reset(context_token)
