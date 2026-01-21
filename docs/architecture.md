# 2. Arquitetura

Esta seção descreve a arquitetura técnica e a stack de tecnologia do Finanpy.

## Stack Tecnológica

**Backend:**
- **Python 3.13+**: Linguagem de programação principal.
- **Django 6.0.1**: Framework web full stack.
- **SQLite**: Banco de dados relacional para simplicidade e portabilidade.

**Frontend:**
- **Django Template Language (DTL)**: Sistema de templates nativo do Django para renderização do frontend.
- **TailwindCSS 3.x**: Framework CSS utility-first para estilização.
- **JavaScript (Vanilla)**: Utilizado pontualmente para interatividade no lado do cliente.

**Ferramentas de Gerenciamento:**
- **`uv`**: Gerenciador de dependências e ambientes virtuais.
- **`ruff`**: Linter e formatter de código Python.
- **`python logging`**: Sistema de logs nativo do Python.

## Padrões de Arquitetura

- **Class-Based Views (CBVs)**: Utilizamos as CBVs do Django para estruturar as views de forma organizada e reutilizável.
- **Apps Modulares**: O projeto é dividido em apps por domínio, cada um com sua responsabilidade, promovendo baixo acoplamento e alta coesão.
- **Autenticação Nativa do Django**: O sistema de autenticação customizado é construído sobre a base segura de autenticação do Django.
