# Time de Agentes de IA do Projeto Finanpy

Este diretório contém as definições e os perfis dos agentes de IA especializados que colaboram no desenvolvimento do projeto Finanpy. Cada agente possui um conjunto de habilidades e um foco específico, garantindo a qualidade e a consistência do software.

## Índice de Agentes

| Agente | Descrição | Quando Usar |
|---|---|---|
| [**Arquiteto de Soluções**](project_manager_agent.md) | Responsável por analisar os requisitos (`prd.md`), quebrar as tarefas, planejar os sprints e coordenar o trabalho dos outros agentes. | Para iniciar uma nova feature, entender o escopo de uma tarefa ou planejar os próximos passos do desenvolvimento. |
| [**Engenheiro de Backend Django**](django_backend_agent.md) | Especialista em Python e Django. Responsável por criar e manter models, views, forms, signals e toda a lógica de negócio do lado do servidor. | Para implementar a lógica de negócio, manipular o banco de dados, criar APIs internas e gerenciar a arquitetura do Django. |
| [**Desenvolvedor Frontend (DTL + Tailwind)**](frontend_template_agent.md) | Especialista em Django Template Language (DTL) e TailwindCSS. Responsável por criar as interfaces de usuário, garantindo que sejam funcionais, responsivas e sigam o Design System. | Para criar ou modificar páginas, implementar componentes visuais, aplicar estilos e garantir a consistência com o `docs/design_system.md`. |
| [**Engenheiro de QA (Testes Automatizados)**](qa_tester_agent.md) | Especialista em automação de testes com Playwright. Responsável por verificar se as funcionalidades atendem aos critérios de aceite e se a interface corresponde ao design. | Para validar a implementação de uma user story, realizar testes de regressão e garantir que a aplicação se comporta conforme o esperado em um ambiente real. |
