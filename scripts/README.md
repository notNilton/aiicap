# Scripts do Projeto AIICAP

Esta pasta contém scripts para gerenciar o projeto AIICAP.

## 📜 Scripts Disponíveis

### 1. `setup.sh` - Configuração Inicial

Configura o projeto pela primeira vez.

```bash
./scripts/setup.sh
```

**O que faz:**

- Cria ambiente virtual (.venv)
- Instala dependências
- Cria arquivo .env
- Inicializa storage (PostgreSQL ou File System)
- Verifica instalação

**Quando usar:** Primeira vez que clonar o projeto

---

### 2. `start.sh` - Iniciar Serviços

Inicia os serviços gerador e corretor em background.

```bash
./scripts/start.sh
```

**O que faz:**

- Para serviços antigos (se houver)
- Inicia gerador em background
- Inicia corretor em background
- Salva PIDs em logs/
- Redireciona output para logs/

**Output:**

- `logs/generator.log` - Log do gerador
- `logs/corrector.log` - Log do corretor
- `logs/generator.pid` - PID do gerador
- `logs/corrector.pid` - PID do corretor

---

### 3. `stop.sh` - Parar Serviços

Para todos os serviços em execução.

```bash
./scripts/stop.sh
```

**O que faz:**

- Para processo do gerador
- Para processo do corretor
- Remove arquivos .pid

---

### 4. `restart.sh` - Reiniciar Serviços

Para e inicia os serviços novamente.

```bash
./scripts/restart.sh
```

Equivalente a:

```bash
./scripts/stop.sh
./scripts/start.sh
```

---

### 5. `status.sh` - Ver Status

Mostra o status dos serviços e estatísticas.

```bash
./scripts/status.sh
```

**Mostra:**

- Modo de storage (PostgreSQL ou File System)
- Status do gerador (rodando/parado)
- Status do corretor (rodando/parado)
- Última atividade de cada serviço
- Estatísticas (imagens geradas/corrigidas)

**Exemplo de output:**

```
========================================
 Status dos Serviços AIICAP
========================================

📦 Modo de Storage: File System

🎨 Gerador:
  Status: ✓ Rodando (PID: 12345)
  Última atividade: [2025-12-16 14:15:30]

🔧 Corretor:
  Status: ✓ Rodando (PID: 12346)
  Última atividade: [2025-12-16 14:15:31]

📊 Estatísticas:
  Imagens geradas: 10
  Imagens corrigidas: 40
  Total: 50
```

---

### 6. `logs.sh` - Ver Logs

Mostra os logs dos serviços em tempo real.

```bash
./scripts/logs.sh
```

**Comportamento:**

- Se serviços estão rodando: Acompanha logs em tempo real (tail -f)
- Se serviços estão parados: Mostra últimas 20 linhas de cada log

**Pressione Ctrl+C para sair**

---

### 7. `clean.sh` - Limpar Dados

Remove imagens, metadados e logs.

```bash
# Limpar apenas File System e logs
./scripts/clean.sh

# Limpar File System, logs E banco de dados
./scripts/clean.sh --db
```

**Remove:**

- `data/untreated/*.png`
- `data/treated/*.png`
- `data/metadata/*.json`
- `logs/*.log`
- `logs/*.pid`
- Banco de dados (se usar `--db`)

**⚠️ CUIDADO:** Esta operação é irreversível!

---

## 🚀 Workflow Típico

### Primeira Vez

```bash
# 1. Setup inicial
./scripts/setup.sh

# 2. Ajustar .env se necessário
nano .env

# 3. Iniciar serviços
./scripts/start.sh

# 4. Ver status
./scripts/status.sh

# 5. Acompanhar logs
./scripts/logs.sh
```

### Uso Diário

```bash
# Verificar se está rodando
./scripts/status.sh

# Iniciar (se não estiver rodando)
./scripts/start.sh

# Ver o que está acontecendo
./scripts/logs.sh

# Parar quando terminar
./scripts/stop.sh
```

### Desenvolvimento

```bash
# Limpar dados de teste
./scripts/clean.sh

# Reiniciar com configurações novas
./scripts/restart.sh

# Monitorar em tempo real
./scripts/logs.sh
```

### Troubleshooting

```bash
# Ver status detalhado
./scripts/status.sh

# Ver logs para debug
./scripts/logs.sh

# Reiniciar tudo
./scripts/restart.sh

# Limpar tudo e começar de novo
./scripts/clean.sh --db
./scripts/setup.sh
./scripts/start.sh
```

---

## 📋 Permissões

Para executar os scripts, você pode precisar dar permissão de execução:

```bash
chmod +x scripts/*.sh
```

Ou executar com bash:

```bash
bash scripts/setup.sh
bash scripts/start.sh
# etc...
```

---

## 🔧 Customização

Todos os scripts podem ser editados conforme sua necessidade. Eles são simples scripts bash.

**Arquivos importantes:**

- `.env` - Configurações do projeto
- `logs/` - Logs e PIDs dos serviços
- `data/` - Imagens (se usar File System)

---

## 📚 Mais Informações

- [README.md](../README.md) - Visão geral do projeto
- [STORAGE_MODES.md](../STORAGE_MODES.md) - Modos de armazenamento
- [.env.example](../.env.example) - Exemplo de configuração
