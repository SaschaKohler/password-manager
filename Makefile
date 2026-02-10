.PHONY: help install dev test lint format security clean docker-build docker-run k8s-deploy

# Default target
help:
	@echo "Available commands:"
	@echo "  install     - Install dependencies"
	@echo "  dev         - Setup development environment"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linting"
	@echo "  format      - Format code"
	@echo "  security    - Run security checks"
	@echo "  clean       - Clean temporary files"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run  - Run Docker container"
	@echo "  k8s-deploy  - Deploy to Kubernetes"

# Install dependencies
install:
	uv sync

# Development setup
dev: install
	cp .env.example .env
	uv run python manage.py migrate
	uv run python manage.py createsuperuser

# Run tests
test:
	uv run pytest --cov=. --cov-report=html --cov-report=term

# Run linting
lint:
	uv run flake8 .
	uv run mypy .
	uv run black --check .
	uv run isort --check-only .

# Format code
format:
	uv run black .
	uv run isort .

# Security checks
security:
	uv run bandit -r ./apps/
	uv run safety check
	uv run uv pip-audit

# Clean temporary files
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf logs/

# Docker build
docker-build:
	docker build -t password-manager:latest .

# Docker run
docker-run:
	docker-compose up --build

# Kubernetes deployment
k8s-deploy:
	kubectl apply -f k8s/
	kubectl rollout status deployment/password-manager-api

# Database migrations
migrate:
	uv run python manage.py migrate

# Create superuser
superuser:
	uv run python manage.py createsuperuser

# Run development server
run:
	uv run python manage.py runserver 0.0.0.0:8000

# Collect static files
collectstatic:
	uv run python manage.py collectstatic --noinput

# Shell access
shell:
	uv run python manage.py shell

# Database reset
reset-db:
	uv run python manage.py flush
	uv run python manage.py migrate

# Generate requirements
requirements:
	uv pip freeze > requirements.txt
