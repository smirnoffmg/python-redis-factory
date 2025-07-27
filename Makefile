.PHONY: help install test test-parallel lint type-check build clean release-patch release-minor release-major version

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	uv sync

test: ## Run tests sequentially
	uv run pytest -n 0

test-parallel: ## Run tests in parallel (recommended)
	uv run pytest -n auto

test-coverage: ## Run tests with coverage
	uv run pytest --cov=python_redis_factory -n auto

lint: ## Run linting
	uv run ruff check .

format: ## Format code
	uv run ruff format .

type-check: ## Run type checking
	uv run mypy src/

build: ## Build package
	uv build

clean: ## Clean build artifacts
	rm -rf dist/ build/ *.egg-info/

version: ## Show current version
	python scripts/version.py current

release-patch: ## Release patch version (0.1.0 -> 0.1.1)
	python scripts/version.py bump patch
	python scripts/version.py tag

release-minor: ## Release minor version (0.1.0 -> 0.2.0)
	python scripts/version.py bump minor
	python scripts/version.py tag

release-major: ## Release major version (0.1.0 -> 1.0.0)
	python scripts/version.py bump major
	python scripts/version.py tag

ci: ## Run full CI checks (lint, type-check, test)
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) test-parallel 