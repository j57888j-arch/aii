from __future__ import annotations

from datetime import UTC, date, datetime, time, timedelta
from zoneinfo import ZoneInfo

BUSINESS_TIMEZONE = ZoneInfo("Asia/Tashkent")


def business_date(now: datetime | None = None, timezone: ZoneInfo = BUSINESS_TIMEZONE) -> date:
    current = now or datetime.now(UTC)
    if current.tzinfo is None:
        current = current.replace(tzinfo=UTC)
    return current.astimezone(timezone).date()


def business_day_bounds_utc(day: date | None = None, timezone: ZoneInfo = BUSINESS_TIMEZONE) -> tuple[datetime, datetime]:
    local_day = day or business_date(timezone=timezone)
    start_local = datetime.combine(local_day, time.min, tzinfo=timezone)
    end_local = start_local + timedelta(days=1)
    return start_local.astimezone(UTC), end_local.astimezone(UTC)
