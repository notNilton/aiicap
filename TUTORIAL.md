# Tutorial de Configuração e Execução do AIICAP

Este guia passo a passo ajudará você a configurar o banco de dados e executar o sistema AIICAP.

## Pré-requisitos

Certifique-se de ter o seguinte instalado:
- **Python 3.7+**
- **PostgreSQL**
- **Git**

## Passo 1: Configurar o Banco de Dados (PostgreSQL)

Você precisa criar um banco de dados e um usuário no PostgreSQL.

1.  Acesse o shell do PostgreSQL:
    ```bash
    sudo -u postgres psql
    ```

2.  Execute os seguintes comandos SQL para criar o banco e o usuário:
    ```sql
    CREATE DATABASE aiicap;
    CREATE USER aiicap_user WITH PASSWORD 'sua_senha_aqui';
    GRANT ALL PRIVILEGES ON DATABASE aiicap TO aiicap_user;
    \q
    ```
    *(Substitua 'sua_senha_aqui' por uma senha segura)*

## Passo 2: Configurar Variáveis de Ambiente

1.  Copie o arquivo de exemplo `.env.example` para `.env`:
    ```bash
    cp .env.example .env
    ```

2.  Edite o arquivo `.env` com suas credenciais:
    - Abra o arquivo `.env` no seu editor.
    - Atualize a linha `DATABASE_URL` com a senha que você definiu:
      ```env
      DATABASE_URL=postgresql://aiicap_user:sua_senha_aqui@localhost:5432/aiicap
      ```
    - Se você for usar a geração de imagens, adicione sua chave da API da OpenAI em `OPENAI_API_KEY`.

## Passo 3: Instalar Dependências

Instale as bibliotecas Python necessárias:

```bash
pip install -r requirements.txt
```

## Passo 4: Inicializar o Banco de Dados

Execute o script para criar as tabelas necessárias no banco de dados:

```bash
python3 setup_database.py
```

Você deve ver uma mensagem de sucesso indicando que as tabelas `generated_images` e `corrected_images` foram criadas.

## Passo 5: Executar a Aplicação

Agora você pode iniciar o sistema:

```bash
python3 main.py
```

## Solução de Problemas Comuns

- **Erro de conexão com o banco**: Verifique se o serviço do PostgreSQL está rodando (`sudo service postgresql status`) e se as credenciais no `.env` estão corretas.
- **Erro de módulo não encontrado**: Certifique-se de que você ativou seu ambiente virtual (se estiver usando um) e rodou o `pip install -r requirements.txt`.
