# Phase 1 self-check

## Implemented in this phase

- [x] Settings validation and Render URL normalization.
- [x] JSON logging; no message text is logged by INFO handlers.
- [x] Async SQLAlchemy engine/session factory with conservative pool sizes.
- [x] Hand-written Alembic initial migration (no `create_all`).
- [x] Users table; admin rights are not stored in PostgreSQL.
- [x] Tashkent business-day helper.
- [x] uz/ru/en locale catalogues and key-parity test.
- [x] aiogram bot/dispatcher factory, Redis FSM with TTL.
- [x] `/start` onboarding flow (language + goal) and `/menu`.
- [x] DB session, user loader, ban, i18n, throttle and error-boundary middleware.
- [x] Webhook secret header + secret URL path validation.
- [x] `/health` liveness and `/ready` dependency checks (503 on failure).
- [x] Render Blueprint, Docker, local Compose, UptimeRobot instructions and CI.

## Must be verified after deployment by the owner

- [ ] Enter real BotFather token and confirm `/start` in Telegram.
- [ ] Confirm Render created Postgres and Key Value in the same region.
- [ ] Confirm Alembic migration completed in Render logs.
- [ ] Confirm `/ready` returns 200 after deployment.
- [ ] Confirm webhook is registered with Telegram and secret header is accepted.
- [ ] Add UptimeRobot monitor and confirm checks every 5 minutes.
- [ ] Confirm notification alert delivery.

## Known limits / NOT VERIFIED

- Live Telegram webhook and polling were not exercised because no real BotFather token was supplied.
- Redis/Valkey network connectivity and Render Blueprint deployment were not exercised from this workspace.
- Postgres migration up/down was not run against a real PostgreSQL server in this workspace.
- Python packages aiogram, redis and asyncpg were not installed in the execution workspace; the code was syntax-checked, while package integration must be run in Docker/CI.
- AI provider, credit quota, Stars billing, referrals, media, Mini App and admin dashboard are intentionally outside Phase 1.
