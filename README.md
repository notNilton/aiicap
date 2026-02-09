# AIICAP - AI Image Correction and Processing

Sistema modular para geração e correção de imagens usando IA, organizado como monorepo.

## Estrutura

```
aiicap/
├── apps/
│   ├── frontend/           # React + Vite (UI)
│   ├── backend/            # FastAPI (API REST)
│   └── image_generator/    # FastAPI (Geração via DALL-E)
├── packages/
│   └── shared/             # Código Python compartilhado
└── docker-compose.yml
```

## Requisitos

- Docker e Docker Compose
- Node.js 20+ (para desenvolvimento local do frontend)
- Python 3.10+ (para desenvolvimento local dos serviços)

## Quick Start

```bash
# Copiar arquivo de ambiente
cp .env.example .env

# Subir todos os serviços
docker-compose up -d

# Acessar
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# Image Generator: http://localhost:8001
```

## Desenvolvimento Local

### Frontend

```bash
cd apps/frontend
npm install
npm run dev
```

### Backend

```bash
cd apps/backend
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -e ../../packages/shared
uvicorn src.main:app --reload
```

### Image Generator

```bash
cd apps/image_generator
python -m venv .venv
source .venv/bin/activate
pip install -e .
pip install -e ../../packages/shared
uvicorn src.main:app --reload --port 8001
```

## API Endpoints

### Backend (`:8000`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/health` | Health check |
| GET | `/api/images` | Listar imagens |
| POST | `/api/generate` | Solicitar geração |
| POST | `/api/correct` | Aplicar correção |
| GET | `/api/correct/types` | Tipos de correção |

### Image Generator (`:8001`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/health` | Health check |
| POST | `/generate` | Gerar imagem |
| GET | `/status/{id}` | Status da geração |

## Variáveis de Ambiente

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/aiicap

# OpenAI (para geração real)
OPENAI_API_KEY=sk-...

# Services
IMAGE_GENERATOR_URL=http://localhost:8001
```

## Licença

MIT
