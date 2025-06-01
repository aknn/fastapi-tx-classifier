.PHONY: help init install test lint format clean dev docker-up docker-down

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

init: ## Initialize development environment
	@echo "Setting up development environment..."
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r dev-requirements.txt
	pre-commit install
	@echo "Development environment ready!"

install: ## Install production dependencies
	pip install -r requirements.txt

test: ## Run tests
	pytest

test-cov: ## Run tests with coverage
	pytest --cov=fastapi_tx_classifier --cov-report=html --cov-report=term

lint: ## Run linting
	ruff check .
	mypy fastapi_tx_classifier/

format: ## Format code
	black .
	ruff check --fix .

clean: ## Clean up cache files
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/

dev: ## Run development server
	python main.py

docker-up: ## Start services with Docker Compose
	docker compose up -d

docker-down: ## Stop Docker Compose services
	docker compose down

docker-logs: ## View Docker Compose logs
	docker compose logs -f
