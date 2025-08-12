.PHONY: help install dev-install run-api run-gui test lint format compose-up compose-down clean

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install production dependencies
	python -m pip install --upgrade pip
	pip install -r requirements.txt

dev-install: ## Install development dependencies
	python -m pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

run-api: ## Start the FastAPI server
	python -m src.api_server

run-gui: ## Start the React GUI dashboard
	cd llama-gui && npm ci && npm run start

test: ## Run the test suite
	pytest tests/ -v

lint: ## Run linting checks
	black --check src/ tests/
	isort --check-only src/ tests/
	flake8 src/ tests/
	mypy src/

format: ## Format code
	black src/ tests/
	isort src/ tests/

compose-up: ## Start services with Docker Compose
	docker compose up --build

compose-down: ## Stop Docker Compose services
	docker compose down

clean: ## Clean up build artifacts
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/

venv: ## Create virtual environment
	python -m venv venv
	@echo "Virtual environment created. Activate with: source venv/bin/activate"

setup: venv install ## Initial project setup
	@echo "Project setup complete!"
	@echo "Next steps:"
	@echo "  1. source venv/bin/activate"
	@echo "  2. cp .env.example .env"
	@echo "  3. make run-api"
