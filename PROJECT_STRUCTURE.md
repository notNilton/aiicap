# 📁 Estrutura Final do Projeto AIICAP

## ✅ Implementação Completa

### 🎯 Arquitetura de Serviços Independentes

```
aiicap/
├── 🚀 main.py                    # Interface CLI interativa (NOVO!)
│
├── 📂 scripts/                    # Todos os scripts do projeto
│   ├── 🐍 Python Scripts
│   │   ├── run_generator.py      # Serviço gerador
│   │   ├── run_corrector.py      # Serviço corretor
│   │   ├── setup_database.py     # Setup PostgreSQL
│   │   └── exemplo_completo.py   # Exemplo de uso
│   │
│   ├── 🔧 Bash Scripts
│   │   ├── setup.sh              # Setup inicial
│   │   ├── start.sh              # Iniciar serviços
│   │   ├── stop.sh               # Parar serviços
│   │   ├── restart.sh            # Reiniciar serviços
│   │   ├── status.sh             # Ver status
│   │   ├── logs.sh               # Ver logs
│   │   └── clean.sh              # Limpar dados
│   │
│   └── 📚 Documentação
│       ├── README.md             # Guia scripts bash
│       └── PYTHON_SCRIPTS.md     # Guia scripts Python
│
├── 📂 modules/                    # Módulos do projeto
│   ├── storage/                   # Camada de abstração de storage
│   │   ├── __init__.py
│   │   ├── database_storage.py   # Backend PostgreSQL
│   │   └── filesystem_storage.py # Backend File System
│   │
│   ├── image_generation/          # Geração de imagens
│   │   ├── __init__.py
│   │   └── generator.py
│   │
│   ├── image_correction/          # Correção de imagens
│   │   ├── __init__.py
│   │   ├── corrector.py
│   │   ├── effects.py
│   │   ├── strategies.py
│   │   └── color_utils.py
│   │
│   ├── database/                  # PostgreSQL ORM
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── session.py
│   │   ├── repository.py
│   │   └── config.py
│   │
│   └── common/                    # Utilitários
│       ├── __init__.py
│       ├── file_utils.py
│       └── display_utils.py
│
├── 📂 data/                       # Dados (se USE_DATABASE=false)
│   ├── untreated/                 # Imagens geradas
│   ├── treated/                   # Imagens corrigidas
│   └── metadata/                  # Metadados JSON
│
├── 📂 logs/                       # Logs dos serviços
│   ├── generator.log
│   ├── generator.pid
│   ├── corrector.log
│   └── corrector.pid
│
├── 📄 .env                        # Configurações (gitignored)
├── 📄 .env.example                # Template de configuração
├── 📄 requirements.txt            # Dependências Python
│
└── 📚 Documentação
    ├── README.md                  # Visão geral
    ├── STORAGE_MODES.md           # Guia de storage
    └── test_services.sh           # Script de teste
```

## 🚀 Como Usar

### Opção 1: Interface Interativa (Recomendado)

```bash
python3 main.py
```

**Menu Interativo:**

```
============================================================
   AIICAP - AI Image Correction and Processing
============================================================

Escolha uma opção:

  1 - Iniciar Gerador de Imagens
  2 - Iniciar Corretor de Imagens
  3 - Iniciar Ambos (Gerador + Corretor)
  4 - Ver Status dos Serviços
  5 - Ver Logs em Tempo Real
  6 - Parar Todos os Serviços
  7 - Configurações (.env)
  8 - Estatísticas
  9 - Executar Exemplo Completo
  0 - Sair
```

### Opção 2: Scripts Bash

```bash
# Setup inicial
./scripts/setup.sh

# Iniciar serviços
./scripts/start.sh

# Ver status
./scripts/status.sh

# Ver logs
./scripts/logs.sh

# Parar serviços
./scripts/stop.sh
```

### Opção 3: Scripts Python Diretos

```bash
# Rodar gerador diretamente
python3 scripts/run_generator.py

# Rodar corretor diretamente
python3 scripts/run_corrector.py

# Executar exemplo
python3 scripts/exemplo_completo.py
```

## ⚙️ Configuração (.env)

```env
# Storage Mode
USE_DATABASE=true          # true = PostgreSQL, false = File System

# PostgreSQL (se USE_DATABASE=true)
DATABASE_URL=postgresql://user:pass@localhost:5432/aiicap

# OpenAI (para geração real)
OPENAI_API_KEY=sk-...

# Generator Service
SIMULATION_MODE=true       # true = teste, false = API real
GENERATION_DELAY=60        # Segundos entre gerações

# Corrector Service
CORRECTION_CHECK_INTERVAL=30   # Intervalo de verificação
CORRECTION_BATCH_SIZE=5        # Imagens por lote
```

## 🎯 Workflows Típicos

### 1. First Time Setup

```bash
# Clone
git clone https://github.com/notNilton/orion-aiicap.git
cd aiicap

# Setup
./scripts/setup.sh

# Ajustar .env se necessário
nano .env

# Iniciar via interface
python3 main.py
# Escolha opção 3 (Iniciar Ambos)
```

### 2. Desenvolvimento

```bash
# Iniciar interface
python3 main.py

# Ou rodar diretamente (ver output)
python3 scripts/run_generator.py      # Terminal 1
python3 scripts/run_corrector.py      # Terminal 2
```

### 3. Produção

```bash
# Iniciar em background
./scripts/start.sh

# Monitorar
./scripts/status.sh
./scripts/logs.sh

# Parar quando necessário
./scripts/stop.sh
```

## 🔄 Dois Modos de Storage

### PostgreSQL (`USE_DATABASE=true`)

```
Imagens → PostgreSQL Tables
├── generated_images
└── corrected_images
```

**Vantagens:**

- Queries SQL
- Relacional
- Escalável
- Buscas rápidas

### File System (`USE_DATABASE=false`)

```
Imagens → Pastas
├── data/untreated/      # Imagens geradas
├── data/treated/        # Imagens corrigidas
└── data/metadata/       # Metadados JSON
```

**Vantagens:**

- Simples
- Sem dependências
- Visualização direta
- Fácil backup

## 📊 Funcionalidades

### ✅ Serviço Gerador

- Gera imagens continuamente
- Modo simulação ou API real (ChatGPT/DALL-E)
- Salva automaticamente no storage
- Configurável via .env

### ✅ Serviço Corretor

- Monitora storage automaticamente
- Detecta imagens não corrigidas
- Aplica pipeline de correções:
  1. Pixelation
  2. Dithering
  3. Palette Reduction
  4. Color Correction
- Salva cada correção automaticamente

### ✅ Interface CLI (main.py)

- Menu interativo
- Controle de serviços
- Status em tempo real
- Ver logs
- Configurações
- Estatísticas

### ✅ Scripts Helper

- Setup automatizado
- Gerenciamento de serviços
- Monitoramento
- Limpeza

## 🧪 Teste Realizado

```
✅ Modo File System:
  - 3 imagens geradas em data/untreated/
  - 12 correções em data/treated/
  - Metadados em data/metadata/

✅ Scripts movidos para scripts/:
  - run_generator.py
  - run_corrector.py
  - setup_database.py
  - exemplo_completo.py

✅ main.py redesenhado:
  - Interface CLI interativa
  - Gerenciamento completo de serviços
  - Status e monitoramento

Tudo funcionando perfeitamente! 🎉
```

## 📝 Próximos Passos

1. **Implementar API ChatGPT Real**

   - Descomentar código em `modules/image_generation/generator.py`
   - Configurar `OPENAI_API_KEY`

2. **Testar Modo PostgreSQL**

   - `USE_DATABASE=true` no .env
   - Run `./scripts/setup.sh`

3. **Criar Dashboard Web**

   - FastAPI + React
   - Monitoramento visual

4. **Adicionar Filas**

   - Redis/RabbitMQ
   - Processamento distribuído

5. **Docker**
   - Containerizar serviços
   - Docker Compose

---

## 🎊 **PROJETO COMPLETO E ORGANIZADO!**

Agora você tem:
✅ Interface CLI amigável (`main.py`)
✅ Scripts organizados (`scripts/`)
✅ Dual storage mode (PostgreSQL/FileSystem)
✅ Serviços independentes
✅ Documentação completa

**Para começar:**

```bash
python3 main.py
```

Divirta-se! 🚀
