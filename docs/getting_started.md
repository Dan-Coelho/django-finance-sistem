# 1. Começando

Este guia irá ajudá-lo a configurar o ambiente de desenvolvimento do Finanpy.

## Pré-requisitos

- Python 3.13+
- `uv` (gerenciador de pacotes e ambientes virtuais)

## Instalação

1. **Clone o repositório:**
   ```bash
   git clone <url-do-repositorio>
   cd finanpy
   ```

2. **Crie e ative o ambiente virtual:**
   ```bash
   uv venv
   source .venv/bin/activate  # Linux/macOS
   .venv\Scripts\activate    # Windows
   ```

3. **Instale as dependências:**
   ```bash
   uv sync
   ```

4. **Aplique as migrações do banco de dados:**
   ```bash
   python manage.py migrate
   ```

5. **Crie um superusuário:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Inicie o servidor de desenvolvimento:**
   ```bash
   python manage.py runserver
   ```

O servidor estará disponível em `http://127.0.0.1:8000/`.
