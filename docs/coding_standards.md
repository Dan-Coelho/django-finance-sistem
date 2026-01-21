# 4. Padrões de Código

Para manter a qualidade e a consistência do código, seguimos os seguintes padrões e ferramentas.

## Estilo de Código

- **PEP 8**: Todo o código Python deve seguir as diretrizes da PEP 8.
- **Clean Code**: Aplicamos os princípios do Clean Code para manter o código legível e de fácil manutenção.
- **Aspas Simples**: Usamos aspas simples (`'`) para strings, exceto quando aspas duplas (`"`) são necessárias.
- **Código em Inglês**: Todo o código (variáveis, funções, classes) deve ser escrito em inglês. A interface para o usuário final é em português.

## Ferramentas

- **`ruff`**: Utilizamos o `ruff` como linter e formatter para garantir a conformidade com os padrões de código de forma automática. A configuração pode ser encontrada no arquivo `pyproject.toml`.

## Sistema de Logging

- O projeto utiliza o sistema de logging nativo do Python, configurado de forma estruturada para registrar eventos importantes e erros.
