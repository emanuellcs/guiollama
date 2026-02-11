.PHONY: install dev lint test docker-up docker-down

install:
	pip install -e .[dev]

dev:
	chainlit run guiollama/ui/app.py -w --port 8000

lint:
	ruff check .
	ruff format --check .
	mypy guiollama

format:
	ruff check --fix .
	ruff format .

test:
	pytest tests/

docker-up:
	docker-compose up --build -d

docker-down:
	docker-compose down
