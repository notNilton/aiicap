.PHONY: help install dev run test lint format clean docker-build docker-run

# Default target
help:
	@echo "AIICAP Image Generator - Comandos Disponíveis"
	@echo ""
	@echo "  make install     - Instalar dependências"
	@echo "  make dev         - Rodar servidor de desenvolvimento"
	@echo "  make run         - Rodar servidor (produção)"
	@echo "  make test        - Rodar testes"
	@echo "  make lint        - Verificar código com ruff"
	@echo "  make format      - Formatar código com ruff"
	@echo "  make clean       - Limpar arquivos temporários"
	@echo "  make docker-build - Construir imagem Docker"
	@echo "  make docker-run  - Rodar container Docker"
	@echo ""

# Python virtual environment
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

# Create virtual environment
$(VENV)/bin/activate:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip

# Install dependencies
install: $(VENV)/bin/activate
	$(PIP) install -e .
	$(PIP) install -e ../../packages/shared
	$(PIP) install ruff pytest pytest-asyncio

# Run development server
dev: install
	$(VENV)/bin/uvicorn src.main:app --reload --host 0.0.0.0 --port 8001

# Run production server
run: install
	$(VENV)/bin/uvicorn src.main:app --host 0.0.0.0 --port 8001

# Run tests
test: install
	$(PYTHON) -m pytest tests/ -v

# Lint code
lint:
	$(VENV)/bin/ruff check src/

# Format code
format:
	$(VENV)/bin/ruff format src/
	$(VENV)/bin/ruff check --fix src/

# Clean temporary files
clean:
	rm -rf $(VENV)
	rm -rf __pycache__ src/__pycache__ src/**/__pycache__
	rm -rf .pytest_cache .ruff_cache
	rm -rf *.egg-info
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

# Docker commands
docker-build:
	docker build -t aiicap-image-generator -f Dockerfile ../..

docker-run:
	docker run -p 8001:8001 --env-file ../../.env aiicap-image-generator
