.PHONY: install run migrate test lint format check down

install:
	python -m pip install -e ".[dev]"

run:
	MODE=polling uvicorn app.main:app --host 0.0.0.0 --port 10000 --reload

migrate:
	alembic upgrade head

revision:
	alembic revision -m "$(message)"

test:
	pytest

lint:
	ruff check .

format:
	ruff format .

check: lint test

down:
	docker compose down
