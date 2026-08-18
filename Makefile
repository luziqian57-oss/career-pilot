.PHONY: install dev test lint compose-up compose-down

install:
	python3.12 -m pip install -e ".[dev]"

dev:
	uvicorn career_pilot.main:app --reload

test:
	pytest

lint:
	ruff check .

compose-up:
	docker compose up --build

compose-down:
	docker compose down
