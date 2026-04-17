.PHONY: help up down restart build logs ps webapp-shell backend-shell db-shell \
	install format lint test clean prune setup-env

# Color constants for better output
BLUE := \033[34m
NC := \033[0m

# Default target
help:
	@echo "$(BLUE)AIICAP - Sistema de Gestão de Imagens$(NC)"
	@echo ""
	@echo "Comandos Docker:"
	@echo "  make up          - Sobe todos os serviços em background"
	@echo "  make down        - Para e remove todos os containers"
	@echo "  make restart     - Reinicia os serviços"
	@echo "  make build       - Reconstrói as imagens Docker"
	@echo "  make logs        - Visualiza os logs em tempo real"
	@echo "  make ps          - Lista o status dos containers"
	@echo ""
	@echo "Acesso aos Containers:"
	@echo "  make webapp-shell  - Abre terminal no container do WebApp"
	@echo "  make backend-shell  - Abre terminal no container do Backend"
	@echo "  make db-shell       - Abre terminal psql no banco de dados"
	@echo ""
	@echo "Desenvolvimento Local & Manutenção:"
	@echo "  make setup-env   - Cria arquivo .env se não existir"
	@echo "  make install     - Instala dependências de todos os componentes"
	@echo "  make format      - Formata o código (Backend, Image Gen e Shared)"
	@echo "  make lint        - Verifica o código com linters"
	@echo "  make test        - Executa todos os testes"
	@echo "  make clean       - Remove arquivos temporários, caches e venvs"
	@echo "  make prune       - Limpeza profunda do Docker (volumes e imagens órfãs)"
	@echo ""

# --- Docker Operations ---

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

build:
	docker-compose build

logs:
	docker-compose logs -f

ps:
	docker-compose ps

webapp-shell:
	docker exec -it aiicap_webapp sh

backend-shell:
	docker exec -it aiicap_backend bash

db-shell:
	docker exec -it aiicap_postgres psql -U aiicap -d aiicap

# --- Local Development ---

setup-env:
	@if [ ! -f .env ]; then \
		cp .env.example .env && echo "Arquivo .env criado a partir do .env.example"; \
	else \
		echo "Arquivo .env já existe."; \
	fi

install:
	@echo "$(BLUE)Instalando dependências do Shared...$(NC)"
	cd packages/shared && python3 -m venv .venv && .venv/bin/pip install -e .
	@echo "$(BLUE)Instalando dependências do Backend...$(NC)"
	$(MAKE) -C backend install
	@echo "$(BLUE)Instalando dependências do Image Generation...$(NC)"
	$(MAKE) -C image-generation install
	@echo "$(BLUE)Instalando dependências do WebApp...$(NC)"
	cd webapp && npm install

format:
	@echo "$(BLUE)Formatando Backend...$(NC)"
	$(MAKE) -C backend format
	@echo "$(BLUE)Formatando Image Generation...$(NC)"
	$(MAKE) -C image-generation format
	@echo "$(BLUE)Formatando Shared Package...$(NC)"
	cd packages/shared && .venv/bin/ruff format . && .venv/bin/ruff check --fix .

lint:
	@echo "$(BLUE)Linting Backend...$(NC)"
	$(MAKE) -C backend lint
	@echo "$(BLUE)Linting Image Generation...$(NC)"
	$(MAKE) -C image-generation lint
	@echo "$(BLUE)Linting WebApp...$(NC)"
	cd webapp && npm run lint

test:
	@echo "$(BLUE)Rodando testes do Backend...$(NC)"
	$(MAKE) -C backend test
	@echo "$(BLUE)Rodando testes do Image Generation...$(NC)"
	$(MAKE) -C image-generation test

clean:
	@echo "$(BLUE)Limpando Backend...$(NC)"
	$(MAKE) -C backend clean
	@echo "$(BLUE)Limpando Image Generation...$(NC)"
	$(MAKE) -C image-generation clean
	@echo "$(BLUE)Limpando Shared Package...$(NC)"
	rm -rf packages/shared/.venv packages/shared/*.egg-info packages/shared/__pycache__
	@echo "$(BLUE)Limpando WebApp...$(NC)"
	rm -rf webapp/node_modules webapp/dist
	@echo "$(BLUE)Limpando diretórios de upload temporários...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

prune:
	docker system prune -f
	docker volume prune -f
