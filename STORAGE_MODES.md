# 🔄 Storage Modes - PostgreSQL vs File System

## 📋 Visão Geral

O AIICAP agora suporta **dois modos de armazenamento**:

1. **PostgreSQL** (Banco de dados) - Modo profissional
2. **File System** (Sistema de pastas) - Modo simples

Você pode alternar entre eles simplesmente mudando uma variável no `.env`!

## ⚙️ Configuração

### Modo PostgreSQL (Padrão)

```env
USE_DATABASE=true
```

**Vantagens:**

- ✅ Busca rápida
- ✅ Queries complexas
- ✅ Escalável
- ✅ Relacional
- ✅ ACID compliant

**Requer:**

- PostgreSQL instalado
- Banco de dados criado
- `python3 setup_database.py`

### Modo File System

```env
USE_DATABASE=false
```

**Vantagens:**

- ✅ Não precisa de PostgreSQL
- ✅ Simples de entender
- ✅ Fácil de fazer backup (copiar pastas)
- ✅ Visualizar imagens diretamente

**Estrutura:**

```
data/
├── untreated/           # Imagens geradas
│   ├── image_1.png
│   ├── image_2.png
│   └── ...
├── treated/             # Imagens corrigidas
│   ├── corrected_1_pixelation.png
│   ├── corrected_1_dithering.png
│   └── ...
└── metadata/            # Metadados em JSON
    ├── generated_1.json
    ├── generated_2.json
    └── ...
```

## 🚀 Como Usar

### Opção 1: PostgreSQL

```bash
# 1. Configurar .env
echo "USE_DATABASE=true" >> .env

# 2. Inicializar banco
python3 setup_database.py

# 3. Rodar serviços
python3 run_generator.py &
python3 run_corrector.py &
```

**Resultado:**

- Imagens salvas em tabelas PostgreSQL
- Queries SQL para buscar
- IDs numéricos para referência

### Opção 2: File System

```bash
# 1. Configurar .env
echo "USE_DATABASE=false" >> .env

# 2. Criar diretórios (criados automaticamente)
mkdir -p data/{untreated,treated,metadata}

# 3. Rodar serviços
python3 run_generator.py &
python3 run_corrector.py &
```

**Resultado:**

```
data/
├── untreated/
│   ├── image_1.png          # Gerada
│   └── image_2.png          # Gerada
├── treated/
│   ├── corrected_1_pixelation.png
│   ├── corrected_1_dithering.png
│   ├── corrected_1_palette_reduction.png
│   ├── corrected_1_color_correction.png
│   └── (mesmo para image_2)
└── metadata/
    ├── generated_1.json     # Metadados + lista de correções
    └── generated_2.json
```

## 📊 Comparação

| Característica | PostgreSQL      | File System |
| -------------- | --------------- | ----------- |
| Instalação     | Complexa        | Simples     |
| Performance    | Rápida          | Média       |
| Escalabilidade | Alta            | Baixa       |
| Queries        | SQL             | Arquivos    |
| Backup         | pg_dump         | cp -r       |
| Visualização   | Precisa extrair | Direto      |
| Metadata       | No banco        | JSON files  |
| Relacional     | Sim             | Não         |

## 🔍 Estrutura de Metadata (File System)

```json
{
  "id": 1,
  "prompt": "Uma paisagem medieval serena",
  "model": "simulation",
  "size": "512x512",
  "quality": "standard",
  "created_at": "2025-12-16T14:02:15.955306",
  "generation_time": 0.1,
  "image_path": "./data/untreated/image_1.png",
  "corrections": [
    {
      "type": "pixelation",
      "parameters": { "pixel_size": 128 },
      "image_path": "./data/treated/corrected_1_pixelation.png",
      "created_at": "2025-12-16T14:02:49.707937"
    },
    {
      "type": "dithering",
      "parameters": { "levels": 10 },
      "image_path": "./data/treated/corrected_1_dithering.png",
      "created_at": "2025-12-16T14:02:51.123456"
    }
    // ... mais correções
  ]
}
```

## 💡 Casos de Uso

### Use PostgreSQL quando:

- 🏢 Produção em larga escala
- 🔍 Precisa de busca complexa
- 📊 Quer estatísticas avançadas
- 🔐 Precisa de controle de acesso
- 🌐 Sistema distribuído

### Use File System quando:

- 🎓 Desenvolvimento/Teste
- 👤 Uso pessoal
- 📁 Quer visualizar imagens facilmente
- 💻 Sem recursos para database
- Prototipagem rápida

## 🔄 Migração entre Modos

### PostgreSQL → File System

```python
# Exportar do banco para arquivos
from modules.database import get_session
from modules.database.models import GeneratedImage
from modules.database.repository import ImageRepository
import json, os

os.makedirs("data/untreated", exist_ok=True)
os.makedirs("data/metadata", exist_ok=True)

with get_session() as session:
    images = session.query(GeneratedImage).all()

    for db_img in images:
        # Salvar imagem
        img = ImageRepository.load_image_from_db(db_img)
        img.save(f"data/untreated/image_{db_img.id}.png")

        # Salvar metadata
        metadata = db_img.to_dict()
        metadata['image_path'] = f"./data/untreated/image_{db_img.id}.png"
        metadata['corrections'] = []

        with open(f"data/metadata/generated_{db_img.id}.json", 'w') as f:
            json.dump(metadata, f, indent=2)

print("✓ Migração completa!")
```

### File System → PostgreSQL

```python
# Importar de arquivos para banco
from modules.storage.filesystem_storage import FileSystemStorage
from modules.storage.database_storage import DatabaseStorage
import glob, json

fs_storage = FileSystemStorage()
db_storage = DatabaseStorage()

# Migrar imagens geradas
for metadata_file in glob.glob("data/metadata/generated_*.json"):
    with open(metadata_file, 'r') as f:
        metadata = json.load(f)

    # Carregar imagem
    img_path = metadata['image_path']
    from PIL import Image
    img = Image.open(img_path)

    # Salvar no banco
    db_storage.save_generated_image(
        image=img,
        prompt=metadata['prompt'],
        model=metadata['model'],
        size=metadata['size'],
        quality=metadata['quality']
    )

print("✓ Migração completa!")
```

## 🧪 Teste Ambos os Modos

```bash
# Testar PostgreSQL
echo "USE_DATABASE=true" > .env
python3 run_generator.py &  # Gera 1 imagem
sleep 20 && killall python3
psql aiicap -c "SELECT COUNT(*) FROM generated_images;"

# Testar File System
echo "USE_DATABASE=false" > .env
python3 run_generator.py &  # Gera 1 imagem
sleep 20 && killall python3
ls data/untreated/
```

## 🎯 Recomendação

**Para começar:** Use **File System** (mais simples)

**Para produção:** Use **PostgreSQL** (mais poderoso)

**Para desenvolvimento:** Alterne entre os dois conforme necessário!

---

## ✅ Teste Realizado

```
✅ Modo File System testado com sucesso!

Gerado:
- 2 imagens em data/untreated/
- 2 metadata em data/metadata/

Corrigido:
- 8 imagens em data/treated/ (4 correções × 2 imagens)
- Metadata atualizado com histórico

Tudo funcionando perfeitamente! 🎉
```
