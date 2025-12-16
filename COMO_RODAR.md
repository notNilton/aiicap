# 🚀 Guia de Serviços AIICAP

Este guia explica como rodar os **serviços separados** do AIICAP.

## 📋 Arquitetura de Serviços

O AIICAP agora funciona com **serviços independentes** que se comunicam via PostgreSQL:

```
┌─────────────────────┐         ┌──────────────────┐
│  run_generator.py   │────────▶│   PostgreSQL     │
│                     │         │   Database       │
│  Gera imagens       │         │                  │
│  continuamente      │         │  - generated_    │
└─────────────────────┘         │    images        │
                                │  - corrected_    │
┌─────────────────────┐         │    images        │
│  run_corrector.py   │◀────────│                  │
│                     │         └──────────────────┘
│  Monitora banco     │
│  Corrige imagens    │
│  automaticamente    │
└─────────────────────┘
```

## ⚙️ Pré-requisitos

1. ✅ PostgreSQL rodando
2. ✅ Banco de dados criado (`aiicap`)
3. ✅ Ambiente virtual ativado
4. ✅ Dependências instaladas
5. ✅ Tabelas inicializadas

```bash
# Ativar ambiente virtual
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Inicializar banco de dados
python3 setup_database.py
```

## 🎨 Serviço 1: Gerador de Imagens

O serviço gerador roda continuamente criando imagens via ChatGPT API.

### Configuração

Edite `.env`:

```env
# API do ChatGPT
OPENAI_API_KEY=sk-your-key-here

# Configurações do gerador
GENERATION_DELAY=60  # Tempo entre gerações (segundos)
SIMULATION_MODE=false  # true = modo teste sem API
```

### Executar

```bash
source .venv/bin/activate
python3 run_generator.py
```

**Saída esperada:**

```
============================================================
 Serviço Gerador de Imagens - AIICAP
============================================================
Delay entre gerações: 60s

[INFO] Inicializando banco de dados...
[OK] Banco de dados pronto

[INFO] Serviço iniciado em 2025-12-16 14:00:00
[INFO] Pressione Ctrl+C para parar

[2025-12-16 14:00:00] Geração #1
------------------------------------------------------------
[INFO] Prompt: Uma paisagem medieval serena com montanhas...
[OK] Imagem gerada e salva (ID: 1)
[INFO] Aguardando 60s até próxima geração...
```

### Modo Simulação (Sem API)

Para testar sem API key real:

```env
SIMULATION_MODE=true
```

Isso gera imagens coloridas simples para teste.

### Parar o Serviço

Pressione `Ctrl+C`

## 🔧 Serviço 2: Corretor de Imagens

O serviço corretor monitora o banco e processa automaticamente imagens novas.

### Configuração

Edite `.env`:

```env
# Configurações do corretor
CORRECTION_CHECK_INTERVAL=30  # Verifica banco a cada N segundos
CORRECTION_BATCH_SIZE=5        # Processa N imagens por vez
```

### Executar

**Em outro terminal:**

```bash
source .venv/bin/activate
python3 run_corrector.py
```

**Saída esperada:**

```
============================================================
 Serviço Corretor de Imagens - AIICAP
============================================================
Intervalo de verificação: 30s
Tamanho do lote: 5
Pipeline de correções: 4 etapas
  1. pixelation
  2. dithering
  3. palette_reduction
  4. color_correction

[INFO] Inicializando banco de dados...
[OK] Banco de dados pronto

[INFO] Serviço iniciado em 2025-12-16 14:00:30
[INFO] Pressione Ctrl+C para parar

[2025-12-16 14:00:30] Verificação #1
------------------------------------------------------------
[INFO] Encontradas 1 imagens para corrigir
  [14:00:30] Processando imagem ID: 1
    [PROC] Aplicando pixelation...
    [OK] pixelation concluída
    [PROC] Aplicando dithering...
    [OK] dithering concluída
    [PROC] Aplicando palette_reduction...
    [OK] palette_reduction concluída
    [PROC] Aplicando color_correction...
    [OK] color_correction concluída
  [OK] Imagem 1 processada com sucesso
[INFO] Aguardando 30s até próxima verificação...
```

### Pipeline de Correções

O corretor aplica automaticamente:

1. **Pixelation** (pixel_size=128)
2. **Dithering** (levels=10)
3. **Palette Reduction** (num_colors=16)
4. **Color Correction** (strategy=AVERAGE)

Para personalizar, edite `run_corrector.py` → `_load_correction_pipeline()`

### Parar o Serviço

Pressione `Ctrl+C`

## 🔄 Executar Ambos Simultaneamente

### Opção 1: Terminais Separados

**Terminal 1 - Gerador:**

```bash
source .venv/bin/activate
python3 run_generator.py
```

**Terminal 2 - Corretor:**

```bash
source .venv/bin/activate
python3 run_corrector.py
```

### Opção 2: Background Jobs

```bash
source .venv/bin/activate

# Rodar gerador em background
python3 run_generator.py > generator.log 2>&1 &
GENERATOR_PID=$!

# Rodar corretor em background
python3 run_corrector.py > corrector.log 2>&1 &
CORRECTOR_PID=$!

# Ver logs
tail -f generator.log corrector.log

# Para parar
kill $GENERATOR_PID $CORRECTOR_PID
```

### Opção 3: Screen/Tmux

```bash
# Criar sessão screen
screen -S generator
source .venv/bin/activate
python3 run_generator.py
# Ctrl+A D para desanexar

screen -S corrector
source .venv/bin/activate
python3 run_corrector.py
# Ctrl+A D para desanexar

# Reconectar
screen -r generator
screen -r corrector
```

## 📊 Monitorar o Sistema

### Ver Estatísticas do Banco

```python
from modules.database import get_session
from modules.database.repository import ImageRepository

with get_session() as session:
    stats = ImageRepository.get_statistics(session)
    print(f"Imagens geradas: {stats['total_generated_images']}")
    print(f"Imagens corrigidas: {stats['total_corrected_images']}")
```

### Listar Imagens Recentes

```python
from modules.image_generation import ImageGenerator

generator = ImageGenerator()
images = generator.get_all_generated_images(limit=10)

for img in images:
    print(f"ID: {img['id']} | Prompt: {img['prompt'][:50]}...")
```

### Ver Correções de uma Imagem

```python
from modules.image_correction import ImageCorrector

corrector = ImageCorrector(source_db_id=1)
corrections = corrector.get_all_corrections()

print(f"Total: {len(corrections)} correções")
for corr in corrections:
    print(f"- {corr['correction_type']}")
```

## 🐛 Troubleshooting

### Gerador não funciona

**Erro: "NotImplementedError"**

- **Causa**: ChatGPT API não está implementada
- **Solução**: Configure `SIMULATION_MODE=true` no `.env` OU implemente a API

**Erro: "OPENAI_API_KEY not set"**

- **Solução**: Adicione a key no `.env`

### Corretor não encontra imagens

**Nenhuma imagem para corrigir**

- Verifique se o gerador está rodando
- Verifique se há imagens no banco: `psql aiicap -c "SELECT COUNT(*) FROM generated_images;"`

### Erros de conexão ao banco

**"Connection refused"**

```bash
sudo systemctl status postgresql
sudo systemctl start postgresql
```

## ⚡ Otimizações

### Processar Mais Rápido

```env
# Reduzir intervalo de verificação
CORRECTION_CHECK_INTERVAL=10

# Aumentar tamanho do lote
CORRECTION_BATCH_SIZE=10
```

### Gerar Mais Devagar

```env
# Aumentar delay entre gerações
GENERATION_DELAY=300  # 5 minutos
```

## 📝 Logs

### Salvar Logs em Arquivo

```bash
# Gerador
python3 run_generator.py 2>&1 | tee generator.log

# Corretor
python3 run_corrector.py 2>&1 | tee corrector.log
```

### Formato de Log

```
[TIMESTAMP] Tipo de mensagem
[INFO]  - Informação
[OK]    - Sucesso
[WARN]  - Aviso
[ERROR] - Erro
[PROC]  - Processando
[SKIP]  - Pulado
```

## 🎯 Próximos Passos

1. **Implementar ChatGPT API**: Descomentar código em `generator.py`
2. **Criar Dashboard**: Monitoramento visual
3. **Adicionar Filas**: Redis para processamento distribuído
4. **API REST**: Endpoint para controlar serviços
5. **Docker**: Containerizar serviços

---

**Os serviços estão prontos para rodar! 🚀**

Para começar:

1. `python3 run_generator.py` (Terminal 1)
2. `python3 run_corrector.py` (Terminal 2)
3. Ver magia acontecer! ✨
