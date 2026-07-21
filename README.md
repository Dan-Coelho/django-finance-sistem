# FinanPy - Gestão Financeira Pessoal

FinanPy é uma aplicação web de gestão financeira pessoal que permite aos usuários controlar suas finanças de forma simples e eficiente.

## Como instalar

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/seu-usuario/finanpy.git
    cd finanpy
    ```

2.  **Crie e ative o ambiente virtual:**
    ```bash
    uv venv
    source .venv/bin/activate  # Linux/macOS
    # .venv\Scripts\activate  # Windows
    ```

3.  **Instale as dependências:**
    ```bash
    uv sync
    ```

4.  **Aplique as migrações do banco de dados:**
    ```bash
    python manage.py migrate
    ```

5.  **Crie um superusuário:**
    ```bash
    python manage.py createsuperuser
    ```

## Como rodar

1.  **Inicie o servidor de desenvolvimento:**
    ```bash
    python manage.py runserver
    ```

2.  **Acesse a aplicação:**
    Abra seu navegador e acesse `http://127.0.0.1:8000/`

## Estrutura do projeto

O projeto segue a estrutura padrão do Django, com as aplicações separadas em seus próprios diretórios.

-   `app/`: Contém as configurações principais do projeto.
-   `accounts/`: Gerencia as contas financeiras dos usuários.
-   `categories/`: Gerencia as categorias de transações.
-   `profiles/`: Gerencia os perfis dos usuários.
-   `transactions/`: Gerencia as transações financeiras.
-   `users/`: Gerencia a autenticação e os usuários.
-   `templates/`: Contém os templates HTML do projeto.
-   `static/`: Contém os arquivos estáticos (CSS, JS, imagens).

## Comandos úteis

-   **Rodar os testes:**
    ```bash
    pytest
    ```

-   **Verificar a cobertura dos testes:**
    ```bash
    pytest --cov
    ```

-   **Formatar o código:**
    ```bash
    ruff format .
    ```

-   **Verificar o linting do código:**
    ```bash
    ruff check .
    ```
