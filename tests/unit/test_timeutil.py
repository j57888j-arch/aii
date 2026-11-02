from datetime import UTC, date, datetime

from app.core.timeutil import business_date, business_day_bounds_utc


def test_business_date_uses_tashkent_midnight():
    # 2026-01-01 19:30 UTC is already 2026-01-02 in Tashkent.
    assert business_date(datetime(2026, 1, 1, 19, 30, tzinfo=UTC)) == date(2026, 1, 2)


def test_naive_datetimes_are_treated_as_utc():
    assert business_date(datetime(2026, 1, 1, 20, 0)) == date(2026, 1, 2)


def test_tashkent_business_day_bounds_are_utc():
    start, end = business_day_bounds_utc(date(2026, 1, 2))
    assert start == datetime(2026, 1, 1, 19, 0, tzinfo=UTC)
    assert end == datetime(2026, 1, 2, 19, 0, tzinfo=UTC)
