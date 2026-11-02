from __future__ import annotations

import json
import logging

from app.logging import JsonFormatter, redact_mapping


def test_json_formatter_does_not_emit_telegram_user_id():
    record = logging.LogRecord("test", logging.INFO, __file__, 1, "safe event", (), None)
    record.user_id = 123456789
    rendered = JsonFormatter().format(record)
    payload = json.loads(rendered)
    assert payload["message"] == "safe event"
    assert "user_id" not in payload


def test_log_secret_fields_are_redacted():
    assert redact_mapping({"api_key": "dont-log-me", "action": "start"}) == {
        "api_key": "[REDACTED]",
        "action": "start",
    }
