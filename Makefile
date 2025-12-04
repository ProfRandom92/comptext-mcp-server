.PHONY: help install install-dev test test-cov lint format clean build deploy

help:
	@echo "CompText MCP Server - Available Commands:"
	@echo ""
	@echo "  make install      - Install production dependencies"
	@echo "  make install-dev  - Install development dependencies"
	@echo "  make test         - Run tests"
	@echo "  make test-cov     - Run tests with coverage"
	@echo "  make lint         - Run linters"
	@echo "  make format       - Format code with black and isort"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make build        - Build distribution packages"
	@echo "  make deploy       - Deploy to Railway"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run Docker container"
	@echo ""

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt
	pre-commit install

test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=src/comptext_mcp --cov-report=html --cov-report=term
	@echo "Coverage report: htmlcov/index.html"

lint:
	flake8 src/ tests/
	mypy src/ --ignore-missing-imports

format:
	black src/ tests/
	isort src/ tests/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +

build: clean
	python -m build

docker-build:
	docker build -f Dockerfile.rest -t comptext-api:latest .

docker-run:
	docker run -p 8000:8000 --env-file .env comptext-api:latest

docker-compose-up:
	docker-compose up -d

docker-compose-down:
	docker-compose down

deploy:
	@echo "Deploying to Railway..."
	railway up
	@echo "Getting public URL..."
	railway domain
