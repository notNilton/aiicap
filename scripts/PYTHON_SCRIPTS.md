# Scripts Python do Projeto AIICAP

Esta pasta contém todos os scripts Python executáveis do projeto.

## 🐍 Scripts Python

### 1. `setup_database.py` - Inicializar Banco de Dados

Cria as tabelas no PostgreSQL.

```bash
python3 scripts/setup_database.py
```

**Quando usar:**

- Primeira vez configurando PostgreSQL
- Depois de dropar as tabelas
- Modo: `USE_DATABASE=true`

---

### 2. `run_generator.py` - Serviço Gerador

Serviço que gera imagens continuamente.

```bash
# Rodar diretamente (foreground)
python3 scripts/run_generator.py

# Rodar com script helper (background)
./scripts/start.sh
```

**Configurações (.env):**

- `SIMULATION_MODE=true/false` - Modo simulação ou API real
- `GENERATION_DELAY=N` - Segundos entre gerações
- `OPENAI_API_KEY` - Chave da API (se não usar simulação)

**Funcionalidades:**

- Gera imagens via ChatGPT API (ou simulação)
- Salva automaticamente no storage (PostgreSQL ou File System)
- Loop contínuo com delay configurável
- Logs estruturados

---

### 3. `run_corrector.py` - Serviço Corretor

Serviço que monitora e corrige imagens automaticamente.

```bash
# Rodar diretamente (foreground)
python3 scripts/run_corrector.py

# Rodar com script helper (background)
./scripts/start.sh
```

**Configurações (.env):**

- `CORRECTION_CHECK_INTERVAL=N` - Segundos entre verificações
- `CORRECTION_BATCH_SIZE=N` - Imagens por lote

**Funcionalidades:**

- Monitora storage em busca de imagens não corrigidas
- Aplica pipeline de correções:
  1. Pixelation
  2. Dithering
  3. Palette Reduction
  4. Color Correction
- Salva cada correção automaticamente
- Skip de correções já aplicadas

---

### 4. `exemplo_completo.py` - Exemplo de Uso

Script demonstrativo do workflow completo.

```bash
python3 scripts/exemplo_completo.py
```

**O que faz:**

- Carrega/cria uma imagem
- Salva como imagem gerada
- Aplica todas as correções
- Mostra estatísticas
- Salva resultado final

**Útil para:**

- Entender o workflow
- Testar funcionalidades
- Exemplo de código

---

## 🔧 Scripts Bash Helper

Os scripts `.sh` nesta pasta facilitam o gerenciamento dos serviços Python:

- `setup.sh` - Configura projeto e chama `setup_database.py`
- `start.sh` - Inicia `run_generator.py` e `run_corrector.py` em background
- `stop.sh` - Para os serviços
- `restart.sh` - Reinicia os serviços
- `status.sh` - Mostra status dos serviços
- `logs.sh` - Mostra logs em tempo real
- `clean.sh` - Limpa dados

Ver [README.md](README.md) para detalhes dos scripts bash.

---

## 🚀 Uso Típico

### Desenvolvimento

```bash
# Rodar diretamente para ver output
python3 scripts/run_generator.py      # Terminal 1
python3 scripts/run_corrector.py      # Terminal 2
```

### Produção

```bash
# Usar scripts helper para background
./scripts/start.sh        # Inicia ambos em background
./scripts/status.sh       # Verifica status
./scripts/logs.sh         # Monitora logs
./scripts/stop.sh         # Para quando necessário
```

---

## 📋 Estrutura

```
scripts/
├── Python Scripts (executáveis principais)
│   ├── setup_database.py      # Setup PostgreSQL
│   ├── run_generator.py       # Serviço gerador
│   ├── run_corrector.py       # Serviço corretor
│   └── exemplo_completo.py    # Exemplo de uso
│
└── Bash Scripts (helpers)
    ├── setup.sh               # Setup completo
    ├── start.sh               # Iniciar serviços
    ├── stop.sh                # Parar serviços
    ├── restart.sh             # Reiniciar serviços
    ├── status.sh              # Ver status
    ├── logs.sh                # Ver logs
    └── clean.sh               # Limpar dados
```

---

## ⚙️ Configuração

Todos os scripts Python leem configurações do arquivo `.env` na raiz do projeto:

```env
# Storage
USE_DATABASE=true/false

# Generator
OPENAI_API_KEY=sk-...
SIMULATION_MODE=true/false
GENERATION_DELAY=60

# Corrector
CORRECTION_CHECK_INTERVAL=30
CORRECTION_BATCH_SIZE=5
```

---

## 🐛 Debug

Para executar scripts Python em modo debug:

```bash
# Com Python debugger
python3 -m pdb scripts/run_generator.py

# Com verbose logging
DEBUG=true python3 scripts/run_generator.py

# Ver apenas parte específica
python3 scripts/run_generator.py 2>&1 | grep "SIMULATION"
```

---

## 📚 Mais Informações

- [../README.md](../README.md) - Visão geral do projeto
- [../STORAGE_MODES.md](../STORAGE_MODES.md) - Modos de storage
- [README.md](README.md) - Scripts bash helper
