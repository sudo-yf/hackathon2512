.PHONY: sync lint format test check run run-cli docker-build docker-run

sync:
	uv sync

lint:
	uv run ruff check main.py src tests

format:
	uv run ruff format main.py src tests

test:
	uv run pytest -q

check: lint test

run:
	uv run python main.py

run-cli:
	uv run python main.py --task "输出当前环境检查结果"

docker-build:
	docker build -t argus-dual-agent:latest .

docker-run:
	docker compose run --rm argus
