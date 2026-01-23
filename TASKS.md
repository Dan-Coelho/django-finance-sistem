## 13. Lista de Tarefas

### Sprint 1: Setup e Infraestrutura Base (1 semana)

#### 1.1 Configuração do Projeto
- [x] **1.1.1** Inicializar projeto Django com uv
  - Executar `uv init` na pasta do projeto
  - Criar arquivo pyproject.toml com dependências básicas
  - Configurar Python 3.13+

- [x] **1.1.2** Instalar e configurar Django
  - Adicionar Django 6.0.1 ao pyproject.toml
  - Executar `uv sync` para instalar dependências
  - Criar projeto Django: `django-admin startproject app .`

- [x] **1.1.3** Configurar ruff
  - Adicionar ruff ao pyproject.toml
  - Criar configuração do ruff (line-length, rules, etc)
  - Configurar pre-commit hook (opcional)

- [x] **1.1.4** Configurar sistema de logging
  - Adicionar configuração de LOGGING em settings.py
  - Criar formatters personalizados
  - Configurar handlers (console e arquivo)
  - Definir níveis de log por ambiente

#### 1.2 Estrutura de Apps
- [x] **1.2.1** Criar app users
  - Executar `python manage.py startapp users`
  - Adicionar ao INSTALLED_APPS
  - Criar estrutura de pastas (templates, static)

- [x] **1.2.2** Criar app profiles
  - Executar `python manage.py startapp profiles`
  - Adicionar ao INSTALLED_APPS
  - Configurar estrutura de pastas

- [x] **1.2.3** Criar app accounts
  - Executar `python manage.py startapp accounts`
  - Adicionar ao INSTALLED_APPS
  - Configurar estrutura de pasas

- [x] **1.2.4** Criar app categories
  - Executar `python manage.py startapp categories`
  - Adicionar ao INSTALLED_APPS
  - Configurar estrutura de pastas

- [x] **1.2.5** Criar app transactions
  - Executar `python manage.py startapp transactions`
  - Adicionar ao INSTALLED_APPS
  - Configurar estrutura de pastas

#### 1.3 Configuração do Django
- [x] **1.3.1** Configurar settings.py
  - Configurar SECRET_KEY
  - Configurar DEBUG e ALLOWED_HOSTS
  - Configurar DATABASES (SQLite)
  - Configurar LANGUAGE_CODE = 'pt-br'
  - Configurar TIME_ZONE = 'America/Fortaleza'
  - Configurar STATIC_URL e STATIC_ROOT
  - Configurar MEDIA_URL e MEDIA_ROOT

- [x] **1.3.2** Configurar autenticação customizada
  - Configurar AUTH_USER_MODEL para email login
  - Adicionar AUTHENTICATION_BACKENDS
  - Configurar LOGIN_URL e LOGIN_REDIRECT_URL
  - Configurar LOGOUT_REDIRECT_URL

- [x] **1.3.3** Configurar URLs principais
  - Criar estrutura de URLs em app/urls.py
  - Incluir URLs de cada app
  - Configurar URL para arquivos estáticos e media

#### 1.4 Setup do TailwindCSS
- [x] **1.4.1** Configurar TailwindCSS via CDN
  - Criar template base.html
  - Adicionar CDN do TailwindCSS no head
  - Adicionar configuração inline do Tailwind (se necessário)

- [x] **1.4.2** Criar estrutura de templates
  - Criar pasta templates/ na raiz
  - Criar base.html com estrutura básica
  - Configurar blocks: title, content, scripts
  - Adicionar meta tags responsivas

- [x] **1.4.3** Criar componentes base
  - Criar templates/components/navbar.html
  - Criar templates/components/sidebar.html
  - Criar templates/components/footer.html
  - Criar templates/components/alerts.html

### Sprint 2: Modelos e Banco de Dados (1 semana)

#### 2.1 Model User Customizado
- [ ] **2.1.1** Criar CustomUser model
  - Criar classe CustomUser em users/models.py
  - Herdar de AbstractBaseUser e PermissionsMixin
  - Adicionar campo email como USERNAME_FIELD
  - Adicionar campos: is_active, is_staff, is_superuser
  - Adicionar campos created_at e updated_at

- [ ] **2.1.2** Criar CustomUserManager
  - Criar classe CustomUserManager
  - Implementar create_user()
  - Implementar create_superuser()
  - Validação de email obrigatório

- [ ] **2.1.3** Configurar admin do User
  - Criar UserAdmin em users/admin.py
  - Configurar list_display
  - Configurar search_fields
  - Configurar list_filter
  - Configurar fieldsets

#### 2.2 Model Profile
- [ ] **2.2.1** Criar Profile model
  - Criar classe Profile em profiles/models.py
  - Relacionamento OneToOne com User
  - Adicionar campos: first_name, last_name, phone
  - Adicionar campos created_at e updated_at
  - Adicionar __str__ method

- [ ] **2.2.2** Criar signal para Profile
  - Criar arquivo profiles/signals.py
  - Implementar signal post_save do User
  - Criar Profile automaticamente ao criar User
  - Registrar signal em profiles/apps.py

- [ ] **2.2.3** Configurar admin do Profile
  - Criar ProfileAdmin em profiles/admin.py
  - Configurar list_display
  - Configurar search_fields
  - Inline no UserAdmin (opcional)

#### 2.3 Model Account
- [ ] **2.3.1** Criar Account model
  - Criar classe Account em accounts/models.py
  - Relacionamento ForeignKey com User
  - Adicionar campos: name, description, balance
  - Adicionar campo is_active
  - Adicionar campos created_at e updated_at
  - Adicionar __str__ method

- [ ] **2.3.2** Adicionar validações no model
  - Validar balance >= 0
  - Validar name não vazio
  - Meta class com ordering
  - Meta class com unique_together (user, name)

- [ ] **2.3.3** Configurar admin do Account
  - Criar AccountAdmin em accounts/admin.py
  - Configurar list_display
  - Configurar list_filter (user, is_active)
  - Configurar search_fields
  - Adicionar readonly_fields (balance, created_at, updated_at)

#### 2.4 Model Category
- [ ] **2.4.1** Criar Category model
  - Criar classe Category em categories/models.py
  - Relacionamento ForeignKey com User (null=True para defaults)
  - Adicionar campos: name, color, type
  - Adicionar campos: is_default, is_active
  - Adicionar created_at e updated_at
  - Adicionar choices para type (INCOME, EXPENSE)
  - Adicionar __str__ method

- [ ] **2.4.2** Criar categorias padrão
  - Criar data migration para categorias default
  - Categorias de receita: Salário, Freelance, Investimentos, Outros
  - Categorias de despesa: Alimentação, Transporte, Moradia, Saúde, Lazer, Educação, Outros
  - Associar cores para cada categoria

- [ ] **2.4.3** Configurar admin do Category
  - Criar CategoryAdmin em categories/admin.py
  - Configurar list_display (name, type, color, is_default, user)
  - Configurar list_filter (type, is_default, is_active)
  - Configurar search_fields
  - Adicionar color picker visual (opcional)

#### 2.5 Model Transaction
- [ ] **2.5.1** Criar Transaction model
  - Criar classe Transaction em transactions/models.py
  - ForeignKey com Account (on_delete=PROTECT)
  - ForeignKey com Category (on_delete=PROTECT)
  - Adicionar campos: type, amount, date, description
  - Adicionar created_at e updated_at
  - Adicionar choices para type (INCOME, EXPENSE)
  - Adicionar __str__ method

- [ ] **2.5.2** Adicionar validações
  - Validar amount > 0
  - Validar date não pode ser futura
  - Validar category.type == transaction.type
  - Meta class com ordering ('-date', '-created_at')
  - Meta class com indexes (date, account, category)

- [ ] **2.5.3** Criar signals para Transaction
  - Criar arquivo transactions/signals.py
  - Signal post_save: atualizar balance do Account
  - Signal post_delete: atualizar balance do Account
  - Registrar signals em transactions/apps.py
  - Usar F() expressions para evitar race conditions

- [ ] **2.5.4** Configurar admin do Transaction
  - Criar TransactionAdmin em transactions/admin.py
  - Configurar list_display
  - Configurar list_filter (type, date, account, category)
  - Configurar search_fields (description)
  - Configurar date_hierarchy (date)
  - Adicionar readonly_fields (created_at, updated_at)

#### 2.6 Migrações
- [ ] **2.6.1** Criar migrations iniciais
  - Executar makemigrations para cada app
  - Revisar arquivos de migration gerados
  - Verificar dependências entre migrations

- [ ] **2.6.2** Aplicar migrations
  - Executar migrate
  - Verificar tabelas criadas no SQLite
  - Testar constraints e indexes

- [ ] **2.6.3** Criar superuser
  - Executar createsuperuser
  - Testar login no admin
  - Verificar models no admin

### Sprint 3: Autenticação e Landing Page (1 semana)

#### 3.1 Sistema de Autenticação
- [ ] **3.1.1** Criar CustomAuthBackend
  - Criar arquivo users/backends.py
  - Implementar EmailAuthBackend
  - Permitir login apenas com email (case-insensitive)
  - Adicionar em settings.AUTHENTICATION_BACKENDS

- [ ] **3.1.2** Criar formulário de cadastro
  - Criar arquivo users/forms.py
  - Criar SignUpForm (ModelForm ou Form)
  - Campos: email, password1, password2
  - Validar email único
  - Validar senhas coincidem
  - Adicionar validadores de senha do Django

- [ ] **3.1.3** Criar view de cadastro
  - Criar SignUpView (CreateView) em users/views.py
  - Template users/templates/signup.html
  - Processar POST do formulário
  - Criar User e fazer login automático
  - Redirecionar para dashboard
  - Adicionar mensagens de sucesso/erro

- [ ] **3.1.4** Criar formulário de login
  - Criar LoginForm em users/forms.py
  - Campos: email, password
  - Adicionar campo "lembrar-me"
  - Validação customizada

- [ ] **3.1.5** Criar view de login
  - Criar LoginView em users/views.py
  - Template users/templates/login.html
  - Processar autenticação
  - Implementar "lembrar-me"
  - Redirecionar para dashboard
  - Mensagens de erro claras

- [ ] **3.1.6** Criar view de logout
  - Criar LogoutView em users/views.py
  - Implementar logout
  - Redirecionar para landing page
  - Mensagem de confirmação

#### 3.2 Recuperação de Senha
- [ ] **3.2.1** Configurar email backend
  - Configurar EMAIL_BACKEND em settings.py
  - Para desenvolvimento: console backend
  - Configurar EMAIL_HOST, EMAIL_PORT (para produção futura)

- [ ] **3.2.2** Criar views de recuperação
  - PasswordResetView: solicitar email
  - PasswordResetDoneView: confirmação de envio
  - PasswordResetConfirmView: formulário nova senha
  - PasswordResetCompleteView: confirmação final

- [ ] **3.2.3** Criar templates de recuperação
  - Template password_reset_form.html
  - Template password_reset_done.html
  - Template password_reset_confirm.html
  - Template password_reset_complete.html
  - Template de email (password_reset_email.html)

- [ ] **3.2.4** Configurar URLs de recuperação
  - Adicionar URLs em users/urls.py
  - Configurar URL patterns do Django contrib.auth
  - Testar fluxo completo

#### 3.3 Landing Page Pública
- [ ] **3.3.1** Criar view da landing page
  - Criar LandingPageView em users/views.py (ou app separado)
  - Template landing.html
  - Verificar se usuário já está logado
  - Redirecionar para dashboard se autenticado

- [ ] **3.3.2** Design da landing page
  - Hero section com título e CTA
  - Seção de features/benefícios
  - Seção "Como funciona"
  - Seção de call-to-action final
  - Footer com links
  - Design com gradientes e tema escuro
  - Totalmente responsivo

- [ ] **3.3.3** Componentes da landing
  - Navbar com logo e botões Login/Cadastrar
  - Cards de features com ícones
  - Botões com gradiente e hover effects
  - Animações sutis (opcional)

- [ ] **3.3.4** Configurar URL raiz
  - Adicionar URL / para landing page
  - Configurar redirecionamento baseado em autenticação

#### 3.4 Templates de Autenticação
- [ ] **3.4.1** Template de cadastro
  - Formulário estilizado com TailwindCSS
  - Campos: email, senha, confirmar senha
  - Validação client-side básica
  - Link para login
  - Mensagens de erro formatadas
  - Design responsivo

- [ ] **3.4.2** Template de login
  - Formulário estilizado
  - Campos: email, senha
  - Checkbox "lembrar-me"
  - Link "Esqueci minha senha"
  - Link para cadastro
  - Mensagens de erro
  - Design responsivo

- [ ] **3.4.3** Mensagens e feedback
  - Configurar Django messages framework
  - Criar template de alerts reutilizável
  - Estilos para success, error, warning, info
  - Posicionamento e animação

### Sprint 4: Dashboard e Navegação (1 semana)

#### 4.1 Estrutura Base do Dashboard
- [ ] **4.1.1** Criar app dashboard (opcional) ou usar transactions
  - Criar DashboardView em views.py
  - Template dashboard.html
  - Apenas usuários autenticados
  - Usar @login_required decorator

- [ ] **4.1.2** Layout do dashboard
  - Criar base_dashboard.html (herda de base.html)
  - Sidebar com navegação
  - Topbar com nome do usuário e logout
  - Content area principal
  - Mobile: hamburger menu

- [ ] **4.1.3** Sidebar de navegação
  - Links: Dashboard, Transações, Categorias, Contas, Perfil
  - Ícones para cada item (usando emoji ou biblioteca)
  - Indicador de página ativa
  - Estilo com hover effects
  - Collapse em mobile

#### 4.2 Cards de Resumo
- [ ] **4.2.1** Card Saldo Total
  - Calcular soma de todas as contas ativas do usuário
  - Exibir valor formatado em BRL
  - Gradiente verde se positivo, vermelho se negativo
  - Ícone representativo

- [ ] **4.2.2** Card Receitas do Mês
  - Filtrar transações tipo INCOME do mês atual
  - Somar valores
  - Exibir formatado
  - Gradiente verde
  - Comparativo com mês anterior (%, arrow up/down)

- [ ] **4.2.3** Card Despesas do Mês
  - Filtrar transações tipo EXPENSE do mês atual
  - Somar valores
  - Exibir formatado
  - Gradiente vermelho
  - Comparativo com mês anterior

- [ ] **4.2.4** Card Balanço do Mês
  - Receitas - Despesas do mês
  - Exibir formatado
  - Gradiente baseado em positivo/negativo
  - Percentual em relação às receitas

#### 4.3 Lista de Transações Recentes
- [ ] **4.3.1** Query de transações
  - Buscar últimas 5-10 transações do usuário
  - Ordenar por data decrescente
  - select_related para Account e Category
  - Filtrar apenas contas ativas

- [ ] **4.3.2** Tabela de transações
  - Colunas: Data, Descrição, Categoria, Conta, Valor
  - Badge colorido para tipo (receita/despesa)
  - Formatação de moeda
  - Responsivo: stack em mobile

- [ ] **4.3.3** Link para página completa
  - Botão "Ver todas" redirecionando para /transactions/
  - Manter consistência visual

#### 4.4 Gráfico de Despesas
- [ ] **4.4.1** Processar dados para gráfico
  - Agrupar despesas do mês por categoria
  - Calcular total e percentual de cada
  - Ordenar por valor (maior primeiro)
  - Limitar às top 5 categorias

- [ ] **4.4.2** Implementar gráfico
  - Usar Chart.js via CDN
  - Gráfico de pizza (donut) ou barras
  - Cores das categorias
  - Labels com valores e percentuais
  - Responsivo

- [ ] **4.4.3** Fallback sem dados
  - Exibir mensagem se não houver despesas
  - Sugerir registrar primeira transação
  - Design consistente

#### 4.5 Seletor de Período
- [ ] **4.5.1** Criar componente de filtro
  - Dropdown ou tabs para períodos
  - Opções: Esta semana, Este mês, Mês passado, Este ano, Personalizado
  - Para personalizado: dois campos de data

- [ ] **4.5.2** Implementar lógica de filtro
  - Query params na URL (?period=month)
  - Recalcular todos os cards
  - Atualizar gráfico
  - Atualizar lista de transações
  - Manter seleção ao navegar

- [ ] **4.5.3** JavaScript para interatividade
  - Form submit ao selecionar período
  - AJAX para atualizar sem reload (opcional)
  - Loading state durante filtro

### Sprint 5: CRUD de Contas (1 semana)

#### 5.1 Listagem de Contas
- [ ] **5.1.1** Criar AccountListView
  - ListView baseada em Account model
  - Filtrar por usuário logado
  - Ordenar por nome ou saldo
  - Template accounts/account_list.html
  - Paginação (se necessário)

- [ ] **5.1.2** Template de listagem
  - Grid de cards, uma para cada conta
  - Exibir: nome, saldo, descrição
  - Badge ativa/inativa
  - Botões: Editar, Excluir
  - Botão flutuante "Nova Conta"
  - Responsivo

- [ ] **5.1.3** Card de resumo geral
  - Total de todas as contas
  - Número de contas ativas
  - Conta com maior saldo
  - Design destacado

#### 5.2 Criação de Conta
- [ ] **5.2.1** Criar AccountCreateView
  - CreateView para Account model
  - Form fields: name, description, balance
  - Associar user automaticamente (request.user)
  - Redirect para lista após sucesso
  - Mensagem de sucesso

- [ ] **5.2.2** Criar AccountForm
  - ModelForm em accounts/forms.py
  - Fields: name, description, balance
  - Validação: balance >= 0
  - Validação: name não vazio
  - Widgets customizados com classes Tailwind

- [ ] **5.2.3** Template de criação
  - Formulário estilizado
  - Labels claros em português
  - Help text quando necessário
  - Botões: Salvar, Cancelar
  - Validação visual de erros
  - Responsivo

#### 5.3 Edição de Conta
- [ ] **5.3.1** Criar AccountUpdateView
  - UpdateView para Account model
  - Verificar que account.user == request.user
  - Form pré-preenchido
  - Campos editáveis: name, description, is_active
  - Balance readonly (calculado via transações)

- [ ] **5.3.2** Template de edição
  - Mesma estrutura do create
  - Título diferenciado
  - Campo balance readonly mas visível
  - Indicador visual de campo readonly

- [ ] **5.3.3** Validação de permissões
  - Apenas dono pode editar
  - Retornar 403 ou 404 se não autorizado
  - Mensagem clara de erro

#### 5.4 Exclusão de Conta
- [ ] **5.4.1** Criar AccountDeleteView
  - DeleteView para Account model
  - Verificar ownership
  - Verificar se não há transações associadas
  - Redirect para lista
  - Mensagem de sucesso/erro

- [ ] **5.4.2** Modal de confirmação
  - Template com modal (ou página de confirmação)
  - Mensagem clara: "Tem certeza?"
  - Listar informações da conta
  - Avisar sobre transações se houver
  - Botões: Confirmar (vermelho), Cancelar

- [ ] **5.4.3** Validação de integridade
  - Verificar relacionamento com Transaction
  - Bloquear exclusão se houver transações
  - Mensagem explicativa
  - Sugestão: desativar ao invés de excluir

#### 5.5 URLs e Navegação
- [ ] **5.5.1** Configurar URLs de accounts
  - /accounts/ - lista
  - /accounts/create/ - criar
  - /accounts/<pk>/edit/ - editar
  - /accounts/<pk>/delete/ - excluir
  - /accounts/<pk>/ - detalhes (opcional)

- [ ] **5.5.2** Adicionar links na navegação
  - Sidebar: item "Contas"
  - Dashboard: link para contas
  - Breadcrumbs nas páginas internas

### Sprint 6: CRUD de Categorias (1 semana)

#### 6.1 Listagem de Categorias
- [ ] **6.1.1** Criar CategoryListView
  - ListView para Category model
  - Filtrar categorias do usuário + categorias default
  - Separar visualmente receitas e despesas
  - Template categories/category_list.html
  - Ordenar por tipo e nome

- [ ] **6.1.2** Template de listagem
  - Duas seções: Receitas e Despesas
  - Cards ou lista com: nome, cor (preview), tipo
  - Indicador de categoria padrão vs personalizada
  - Botões: Editar (só personalizadas), Excluir (só personalizadas)
  - Botão "Nova Categoria"
  - Responsivo

- [ ] **6.1.3** Filtros e busca
  - Filtro por tipo (todas, receitas, despesas)
  - Busca por nome
  - Toggle mostrar/ocultar inativas

#### 6.2 Criação de Categoria
- [ ] **6.2.1** Criar CategoryCreateView
  - CreateView para Category model
  - Fields: name, type, color
  - Associar user automaticamente
  - is_default = False
  - Redirect para lista

- [ ] **6.2.2** Criar CategoryForm
  - ModelForm em categories/forms.py
  - Fields: name, type, color
  - Choices para type (INCOME/EXPENSE)
  - Widget para color (color picker ou select)
  - Validação: nome único por tipo e usuário

- [ ] **6.2.3** Template de criação
  - Formulário estilizado
  - Seletor visual de cores
  - Preview da categoria antes de salvar
  - Radio buttons ou select para tipo
  - Botões: Salvar, Cancelar

#### 6.3 Edição de Categoria
- [ ] **6.3.1** Criar CategoryUpdateView
  - UpdateView para Category model
  - Verificar: category.user == request.user E is_default == False
  - Bloquear edição de categorias padrão
  - Fields: name, color, is_active
  - Type não editável

- [ ] **6.3.2** Template de edição
  - Mesma estrutura do create
  - Campo type readonly mas visível
  - Preview atualizado em tempo real
  - Validação de permissões

- [ ] **6.3.3** Validações
  - Apenas categorias personalizadas editáveis
  - Mensagem clara se tentar editar padrão
  - Verificar ownership

#### 6.4 Exclusão de Categoria
- [ ] **6.4.1** Criar CategoryDeleteView
  - DeleteView para Category model
  - Verificar ownership e is_default == False
  - Verificar se não há transações usando
  - Bloquear exclusão se houver transações

- [ ] **6.4.2** Modal de confirmação
  - Avisar sobre transações se houver
  - Sugerir desativar ao invés de excluir
  - Mensagem sobre impacto
  - Botões: Confirmar, Cancelar

- [ ] **6.4.3** Tratamento de erros
  - Mensagem se categoria padrão
  - Mensagem se há transações
  - Redirect apropriado

#### 6.5 URLs e Navegação
- [ ] **6.5.1** Configurar URLs
  - /categories/ - lista
  - /categories/create/ - criar
  - /categories/<pk>/edit/ - editar
  - /categories/<pk>/delete/ - excluir

- [ ] **6.5.2** Navegação
  - Adicionar "Categorias" na sidebar
  - Links no dashboard se relevante
  - Breadcrumbs

### Sprint 7: CRUD de Transações (1-2 semanas)

#### 7.1 Listagem de Transações
- [ ] **7.1.1** Criar TransactionListView
  - ListView para Transaction model
  - Filtrar por account.user == request.user
  - Ordenar por data decrescente
  - select_related('account', 'category')
  - Paginação (20 por página)

- [ ] **7.1.2** Template de listagem
  - Tabela responsiva
  - Colunas: Data, Descrição, Categoria, Conta, Tipo, Valor
  - Badge colorido para tipo
  - Ícone da cor da categoria
  - Botões: Editar, Excluir
  - Total da página/filtro
  - Responsivo: cards em mobile

- [ ] **7.1.3** Botão de nova transação
  - Botão flutuante ou no topo
  - Dropdown: Nova Receita / Nova Despesa
  - Design destacado com gradiente

#### 7.2 Filtros de Transações
- [ ] **7.2.1** Criar form de filtros
  - Campo: período (data início e fim)
  - Campo: categorias (multiple choice)
  - Campo: contas (multiple choice)
  - Campo: tipo (receita/despesa/todas)
  - Botões: Filtrar, Limpar

- [ ] **7.2.2** Implementar lógica de filtro
  - Query params na URL
  - Filtros combinados (AND)
  - Manter filtros ao paginar
  - Exibir filtros ativos

- [ ] **7.2.3** UI de filtros
  - Sidebar de filtros (desktop)
  - Drawer ou modal (mobile)
  - Chips mostrando filtros ativos
  - Contador de resultados

- [ ] **7.2.4** Resumo filtrado
  - Card com total de receitas filtradas
  - Card com total de despesas filtradas
  - Card com balanço
  - Comparativo com período anterior

#### 7.3 Criação de Transação
- [ ] **7.3.1** Criar TransactionCreateView
  - CreateView para Transaction model
  - Two views: CreateIncomeView e CreateExpenseView
  - Ou uma view com type pré-selecionado
  - Fields: amount, date, category, account, description

- [ ] **7.3.2** Criar TransactionForm
  - ModelForm em transactions/forms.py
  - Fields: amount, date, category, account, description
  - Filtrar categories por type
  - Filtrar accounts por user
  - Validações: amount > 0, date não futura
  - Data padrão: hoje
  - Widgets customizados

- [ ] **7.3.3** Template de criação
  - Formulário em duas colunas (desktop)
  - Input de valor destacado e grande
  - Date picker (HTML5 date input)
  - Select estilizado para categoria e conta
  - Textarea para descrição
  - Preview do impacto no saldo
  - Botões: Salvar, Salvar e Novo, Cancelar

- [ ] **7.3.4** Validações avançadas
  - Verificar category.type == transaction.type
  - Verificar account pertence ao user
  - Verificar saldo suficiente (warning, não bloqueio)
  - Mensagens de validação claras

#### 7.4 Edição de Transação
- [ ] **7.4.1** Criar TransactionUpdateView
  - UpdateView para Transaction model
  - Verificar account.user == request.user
  - Todos os campos editáveis
  - Recalcular saldo da conta

- [ ] **7.4.2** Template de edição
  - Mesma estrutura do create
  - Título diferenciado
  - Mostrar valor anterior do saldo
  - Mostrar novo valor do saldo (calculado)
  - Indicador de mudança no saldo

- [ ] **7.4.3** Lógica de atualização de saldo
  - No save do form: reverter transação antiga
  - Aplicar nova transação
  - Usar transaction.atomic()
  - Logging das mudanças

#### 7.5 Exclusão de Transação
- [ ] **7.5.1** Criar TransactionDeleteView
  - DeleteView para Transaction model
  - Verificar ownership via account.user
  - Signal ajustará saldo automaticamente

- [ ] **7.5.2** Modal de confirmação
  - Mostrar detalhes da transação
  - Avisar sobre impacto no saldo
  - Mostrar novo saldo após exclusão
  - Botões: Confirmar (vermelho), Cancelar

- [ ] **7.5.3** Feedback de sucesso
  - Mensagem confirmando exclusão
  - Mostrar novo saldo da conta
  - Redirect para lista

#### 7.6 Detalhes de Transação (Opcional)
- [ ] **7.6.1** Criar TransactionDetailView
  - DetailView para Transaction model
  - Exibir todos os campos
  - Informações da conta e categoria
  - Histórico de edições (se implementado)

- [ ] **7.6.2** Template de detalhes
  - Layout de card grande
  - Badges e ícones
  - Botões: Editar, Excluir, Voltar

#### 7.7 URLs e Navegação
- [ ] **7.7.1** Configurar URLs
  - /transactions/ - lista
  - /transactions/income/create/ - nova receita
  - /transactions/expense/create/ - nova despesa
  - /transactions/<pk>/ - detalhes
  - /transactions/<pk>/edit/ - editar
  - /transactions/<pk>/delete/ - excluir

- [ ] **7.7.2** Navegação
  - Item "Transações" na sidebar
  - Links no dashboard
  - Breadcrumbs em todas as páginas

### Sprint 8: Gestão de Perfil e Melhorias UX (1 semana)

#### 8.1 Visualização de Perfil
- [ ] **8.1.1** Criar ProfileDetailView
  - DetailView para Profile model
  - Buscar via request.user.profile
  - Template profiles/profile_detail.html

- [ ] **8.1.2** Template de perfil
  - Card com informações do usuário
  - Exibir: nome completo, email, telefone
  - Avatar (placeholder ou inicial do nome)
  - Estatísticas: total de transações, contas, desde quando usa
  - Botão "Editar Perfil"
  - Design moderno com gradientes

#### 8.2 Edição de Perfil
- [ ] **8.2.1** Criar ProfileUpdateView
  - UpdateView para Profile model
  - Fields: first_name, last_name, phone
  - Verificar profile.user == request.user

- [ ] **8.2.2** Criar ProfileForm
  - ModelForm em profiles/forms.py
  - Fields: first_name, last_name, phone
  - Validação de telefone (formato brasileiro)
  - Todos os campos opcionais

- [ ] **8.2.3** Template de edição
  - Formulário estilizado
  - Preview do nome completo
  - Validação client-side
  - Botões: Salvar, Cancelar

- [ ] **8.2.4** Edição de email e senha
  - Link "Alterar Email" (form separado)
  - Link "Alterar Senha" (form separado)
  - Validações de segurança
  - Confirmação por email (opcional)

#### 8.3 Melhorias de UX
- [ ] **8.3.1** Mensagens de feedback
  - Toast notifications com Tailwind
  - Auto-dismiss após 5s
  - Posicionamento top-right
  - Animações suaves

- [ ] **8.3.2** Loading states
  - Spinner em botões durante submit
  - Skeleton screens em listas
  - Progress bar em operações longas

- [ ] **8.3.3** Empty states
  - Mensagem quando não há transações
  - Mensagem quando não há contas
  - Mensagem quando não há categorias personalizadas
  - CTAs para primeira ação
  - Ilustrações ou ícones grandes

- [ ] **8.3.4** Confirmações visuais
  - Animação de sucesso em criações
  - Highlight em items recém-criados
  - Transições suaves entre páginas

#### 8.4 Breadcrumbs e Navegação
- [ ] **8.4.1** Implementar breadcrumbs
  - Componente reutilizável
  - Em todas as páginas internas
  - Links funcionais
  - Página atual não clicável

- [ ] **8.4.2** Melhorar sidebar
  - Indicador de página ativa
  - Contador de items (ex: "5 contas")
  - Collapse/expand em mobile
  - Smooth transitions

#### 8.5 URLs e Navegação
- [ ] **8.5.1** Configurar URLs
  - /profile/ - visualizar
  - /profile/edit/ - editar
  - /profile/change-email/ - alterar email
  - /profile/change-password/ - alterar senha

- [ ] **8.5.2** Navegação
  - Item "Perfil" na sidebar
  - Dropdown de usuário no topbar
  - Links rápidos

### Sprint 9: Melhorias de Dashboard e Relatórios (1 semana)

#### 9.1 Aprimoramento do Dashboard
- [ ] **9.1.1** Adicionar mais métricas
  - Média de gastos diários do mês
  - Categoria com maior gasto
  - Evolução mensal (últimos 6 meses)
  - Meta de gastos (configurável - opcional)

- [ ] **9.1.2** Gráfico de evolução
  - Gráfico de linha: receitas vs despesas
  - Por mês nos últimos 6-12 meses
  - Usando Chart.js
  - Cores consistentes com design
  - Responsivo

- [ ] **9.1.3** Top categorias
  - Lista das 5 categorias com mais gastos
  - Valor e percentual
  - Barra de progresso visual
  - Link para filtro por categoria

#### 9.2 Página de Relatórios (Opcional)
- [ ] **9.2.1** Criar ReportsView
  - View para geração de relatórios
  - Filtros: período, categorias, contas
  - Template reports/reports.html

- [ ] **9.2.2** Relatório de Resumo Mensal
  - Tabela: categoria x valor
  - Total de receitas
  - Total de despesas
  - Balanço
  - Comparativo com mês anterior

- [ ] **9.2.3** Relatório por Categoria
  - Detalhar todas as transações por categoria
  - Gráfico de pizza
  - Tabela de transações
  - Export CSV (opcional)

- [ ] **9.2.4** Relatório de Fluxo de Caixa
  - Entradas e saídas dia a dia
  - Saldo acumulado
  - Gráfico de linha
  - Identificar dias de maior gasto

#### 9.3 Exportação de Dados (Opcional)
- [ ] **9.3.1** Export de transações para CSV
  - Botão "Exportar" na lista de transações
  - Gerar CSV com filtros aplicados
  - Headers em português
  - Formatação de valores

- [ ] **9.3.2** Export de relatórios para PDF
  - Biblioteca para geração de PDF
  - Template do relatório em PDF
  - Download direto
  - Ou: usar print CSS para impressão

#### 9.4 URLs
- [ ] **9.4.1** Configurar URLs
  - /reports/ - página de relatórios
  - /reports/monthly/ - relatório mensal
  - /reports/category/ - por categoria
  - /reports/cashflow/ - fluxo de caixa
  - /transactions/export/ - export CSV

### Sprint 10: Otimizações e Polimento (1 semana)

#### 10.1 Otimizações de Performance
- [ ] **10.1.1** Otimizar queries
  - Revisar todas as views
  - Adicionar select_related onde necessário
  - Adicionar prefetch_related para many-to-many
  - Remover N+1 queries

- [ ] **10.1.2** Adicionar indexes
  - Index em Transaction.date
  - Index em Transaction.account_id
  - Index em Transaction.category_id
  - Index compostos se necessário
  - Criar migration para indexes

- [ ] **10.1.3** Caching (opcional)
  - Cache de dashboard stats
  - Cache de categorias padrão
  - Cache de templates (template fragment)
  - Configurar cache backend

#### 10.2 Validações e Segurança
- [ ] **10.2.1** Revisar permissões
  - Todas as views com login_required
  - Verificar ownership em updates/deletes
  - CSRF protection em todos os forms
  - Validação de dados no backend

- [ ] **10.2.2** Sanitização de inputs
  - Escape de HTML em outputs
  - Validação de valores numéricos
  - Validação de datas
  - Proteção contra SQL injection (Django já faz)

- [ ] **10.2.3** Rate limiting (opcional)
  - Limitar tentativas de login
  - Limitar criação de transações
  - Django-ratelimit ou similar

#### 10.3 Tratamento de Erros
- [ ] **10.3.1** Páginas de erro customizadas
  - 404.html - Página não encontrada
  - 500.html - Erro do servidor
  - 403.html - Acesso negado
  - Design consistente com o sistema

- [ ] **10.3.2** Logging estruturado
  - Logs de erros em arquivo
  - Logs de ações importantes (criar conta, transação)
  - Formato consistente
  - Rotação de logs

- [ ] **10.3.3** Tratamento de exceções
  - Try-except em operações críticas
  - Mensagens de erro amigáveis
  - Fallbacks quando possível

#### 10.4 Acessibilidade
- [ ] **10.4.1** Semântica HTML
  - Usar tags apropriadas (header, nav, main, etc)
  - Labels em todos os inputs
  - Alt text em imagens
  - Heading hierarchy correta

- [ ] **10.4.2** Navegação por teclado
  - Tab order lógico
  - Focus visível
  - Atalhos de teclado (opcional)
  - Skip to content link

- [ ] **10.4.3** Contraste e legibilidade
  - Verificar contraste de cores (WCAG AA)
  - Tamanhos de fonte adequados
  - Line height confortável
  - Não depender apenas de cor

#### 10.5 Responsividade
- [ ] **10.5.1** Testar em diferentes devices
  - Mobile (320px, 375px, 414px)
  - Tablet (768px, 1024px)
  - Desktop (1280px, 1920px)
  - Landscape e portrait

- [ ] **10.5.2** Ajustes responsivos
  - Menu hamburger funcional em mobile
  - Tabelas scroll horizontal em mobile
  - Forms em coluna única em mobile
  - Botões com tamanho adequado para toque

- [ ] **10.5.3** Performance mobile
  - Otimizar imagens
  - Minimizar JavaScript
  - Lazy loading (se aplicável)

#### 10.6 Documentação
- [ ] **10.6.1** README.md
  - Descrição do projeto
  - Como instalar (setup com uv)
  - Como rodar
  - Estrutura do projeto
  - Comandos úteis

- [ ] **10.6.2** Docstrings
  - Docstrings em classes importantes
  - Docstrings em métodos complexos
  - Seguir padrão Google ou NumPy

- [ ] **10.6.3** Comentários no código
  - Comentar lógica complexa
  - Explicar decisões não óbvias
  - TODOs para melhorias futuras

### Sprint 11: Testes (Sprint Final)

#### 11.1 Testes de Models
- [ ] **11.1.1** Testar User model
  - Teste de criação de usuário
  - Teste de email único
  - Teste de criação de superuser
  - Teste de métodos customizados

- [ ] **11.1.2** Testar Profile model
  - Teste de criação automática via signal
  - Teste de relacionamento com User
  - Teste de __str__ method

- [ ] **11.1.3** Testar Account model
  - Teste de criação
  - Teste de validações
  - Teste de atualização de balance
  - Teste de relacionamento com User

- [ ] **11.1.4** Testar Category model
  - Teste de categorias padrão
  - Teste de categorias personalizadas
  - Teste de validações

- [ ] **11.1.5** Testar Transaction model
  - Teste de criação
  - Teste de validações
  - Teste de signals (atualização de balance)
  - Teste de relacionamentos

#### 11.2 Testes de Views
- [ ] **11.2.1** Testar autenticação
  - Teste de signup
  - Teste de login
  - Teste de logout
  - Teste de recuperação de senha

- [ ] **11.2.2** Testar CRUD de contas
  - Teste de listagem
  - Teste de criação
  - Teste de edição
  - Teste de exclusão
  - Teste de permissões

- [ ] **11.2.3** Testar CRUD de categorias
  - Teste de listagem
  - Teste de criação
  - Teste de edição (apenas personalizadas)
  - Teste de exclusão (apenas personalizadas)

- [ ] **11.2.4** Testar CRUD de transações
  - Teste de listagem
  - Teste de criação (receita e despesa)
  - Teste de edição
  - Teste de exclusão
  - Teste de filtros

- [ ] **11.2.5** Testar dashboard
  - Teste de acesso autenticado
  - Teste de cálculos de cards
  - Teste de filtros de período

#### 11.3 Testes de Forms
- [ ] **11.3.1** Testar SignUpForm
  - Validação de email único
  - Validação de senhas coincidentes
  - Validação de força de senha

- [ ] **11.3.2** Testar AccountForm
  - Validação de campos obrigatórios
  - Validação de balance >= 0

- [ ] **11.3.3** Testar CategoryForm
  - Validação de nome único por tipo
  - Validação de campos

- [ ] **11.3.4** Testar TransactionForm
  - Validação de amount > 0
  - Validação de data não futura
  - Validação de category type

#### 11.4 Testes de Integração
- [ ] **11.4.1** Fluxo completo de usuário
  - Cadastro → Login → Dashboard
  - Criar conta → Criar transação → Ver saldo atualizado
  - Filtrar transações → Ver totais corretos

- [ ] **11.4.2** Testes de signals
  - Criar transação → Balance atualizado
  - Editar transação → Balance recalculado
  - Deletar transação → Balance ajustado
  - Criar User → Profile criado automaticamente

#### 11.5 Configuração de Testes
- [ ] **11.5.1** Setup de testes
  - Configurar pytest (ou unittest)
  - Configurar coverage
  - Fixtures reutilizáveis
  - Factory para criação de objetos (factory_boy)

- [ ] **11.5.2** Executar testes
  - Comando para rodar todos os testes
  - Relatório de coverage
  - Meta: cobertura > 80%

- [ ] **11.5.3** CI/CD (opcional)
  - GitHub Actions para rodar testes
  - Verificar coverage
  - Lint com ruff

### Sprint 12: Docker e Deploy (Sprint Final)

#### 12.1 Dockerização
- [ ] **12.1.1** Criar Dockerfile
  - Base image Python 3.13
  - Instalar dependências com uv
  - Copiar código
  - Configurar entrypoint
  - Expose porta 8000

- [ ] **12.1.2** Criar docker-compose.yml
  - Service para Django
  - Volume para código (desenvolvimento)
  - Volume para banco SQLite
  - Port mapping
  - Environment variables

- [ ] **12.1.3** Scripts de inicialização
  - Script para migrations
  - Script para collectstatic
  - Script para criar superuser
  - Documentar uso

#### 12.2 Configurações de Produção
- [ ] **12.2.1** settings.py para produção
  - Separar settings (base, dev, prod)
  - SECRET_KEY de variável de ambiente
  - DEBUG = False em produção
  - ALLOWED_HOSTS configurável
  - SECURE_* settings

- [ ] **12.2.2** Arquivos estáticos
  - Configurar STATIC_ROOT
  - Collectstatic
  - Servir via Whitenoise (ou nginx)

- [ ] **12.2.3** Banco de dados
  - Manter SQLite ou migrar para PostgreSQL
  - Backup automático do SQLite
  - Configurar DATABASE_URL

#### 12.3 Deploy (Opcional)
- [ ] **12.3.1** Escolher plataforma
  - Heroku (simples)
  - Railway (simples)
  - DigitalOcean (mais controle)
  - AWS/GCP (mais complexo)

- [ ] **12.3.2** Configurar deploy
  - Procfile (se Heroku)
  - Railway config
  - Ou: Dockerfile + Cloud Run

- [ ] **12.3.3** Variáveis de ambiente
  - SECRET_KEY
  - DEBUG
  - ALLOWED_HOSTS
  - DATABASE_URL (se não SQLite)

- [ ] **12.3.4** Domínio e SSL
  - Configurar domínio personalizado
  - Certificado SSL (Let's Encrypt)
  - Redirecionamento HTTP → HTTPS

#### 12.4 Monitoramento (Opcional)
- [ ] **12.4.1** Logs
  - Configurar logging para produção
  - Serviço de logs (Papertrail, etc)
  - Alertas de erros

- [ ] **12.4.2** Uptime monitoring
  - Ping periódico
  - Alertas se fora do ar
  - StatusPage (opcional)

- [ ] **12.4.3** Analytics (Opcional)
  - Google Analytics ou similar
  - Métricas de uso
  - Funis de conversão

### Sprint 13: Multitenant (Sprint Final - Futuro)

#### 13.1 Preparação para Multitenant
- [ ] **13.1.1** Análise de arquitetura
  - Decidir estratégia: schema por tenant ou row-level
  - Avaliar django-tenants ou implementação custom
  - Planejar migração de dados

- [ ] **13.1.2** Model Tenant
  - Criar model Tenant/Organization
  - Relacionamentos com User
  - Subdomínio ou slug

- [ ] **13.1.3** Middleware
  - Detectar tenant por subdomínio/slug
  - Filtrar queries por tenant
  - Isolamento de dados

#### 13.2 Adaptação dos Models
- [ ] **13.2.1** Adicionar ForeignKey para Tenant
  - Em Account
  - Em Category
  - Em Transaction
  - Migration de dados existentes

- [ ] **13.2.2** Filtros por tenant
  - Managers customizados
  - Filtros automáticos em queries
  - Garantir isolamento

#### 13.3 Funcionalidades Multitenant
- [ ] **13.3.1** Cadastro de organizações
  - Form de criação
  - Escolha de subdomínio
  - Owner da organização

- [ ] **13.3.2** Convite de membros
  - Enviar convites por email
  - Aceitar/recusar convites
  - Roles: admin, member, viewer

- [ ] **13.3.3** Gestão de membros
  - Lista de membros
  - Alterar roles
  - Remover membros