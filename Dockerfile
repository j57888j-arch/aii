FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /opt/studyhelper

COPY pyproject.toml README.md ./
COPY app ./app
COPY alembic.ini ./alembic.ini
COPY scripts ./scripts

RUN pip install --no-cache-dir . \
    && chmod +x scripts/start.sh

EXPOSE 10000
CMD ["./scripts/start.sh"]
