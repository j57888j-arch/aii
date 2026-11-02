#!/usr/bin/env sh
set -eu

# Run only explicit, hand-written Alembic migrations. Never use metadata.create_all here.
alembic upgrade head

exec uvicorn app.main:app \
  --host "${HOST:-0.0.0.0}" \
  --port "${PORT:-10000}" \
  --proxy-headers \
  --forwarded-allow-ips="*"
