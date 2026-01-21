# 3. Estrutura do Projeto

O Finanpy segue a arquitetura de apps modulares do Django. Cada app tem uma responsabilidade única no sistema.

## Estrutura de Diretórios

```
finanpy/
├── app/                  # Configurações principais do projeto Django
├── accounts/             # App para gerenciar contas financeiras
├── categories/           # App para gerenciar categorias de transações
├── profiles/             # App para gerenciar perfis de usuário
├── transactions/         # App para gerenciar transações
├── users/                # App para gerenciar usuários e autenticação
├── manage.py             # Utilitário de linha de comando do Django
├── pyproject.toml        # Definição do projeto e dependências
├── uv.lock               # Arquivo de lock de dependências
└── ...
```

## Descrição dos Apps

- **`app`**: Contém as configurações globais do projeto Django (`settings.py`, `urls.py`, etc.).
- **`users`**: Gerencia o modelo de usuário customizado, autenticação (login, logout, cadastro) e recuperação de senha.
- **`profiles`**: Responsável pelos perfis dos usuários, com informações adicionais como nome e telefone.
- **`accounts`**: Modela as contas financeiras do usuário (ex: carteira, conta bancária), cada uma com seu próprio saldo.
- **`categories`**: Gerencia as categorias de receitas e despesas, incluindo categorias padrão e personalizadas pelo usuário.
- **`transactions`**: O coração do sistema, onde as transações de receita e despesa são registradas, vinculadas a uma conta e uma categoria.
