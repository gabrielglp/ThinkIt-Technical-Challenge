# Orders Dashboard

Aplicação fullstack para gestão de pedidos de e-commerce. Desenvolvida como desafio técnico utilizando FastAPI, Next.js 16, PostgreSQL e Docker Compose.

## Stack

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Alembic |
| Banco de dados | PostgreSQL 16 |
| Frontend | Next.js 16, React 19, TypeScript, TanStack Query v5 |
| UI | Shadcn/ui, Tailwind CSS, Recharts |
| Estado de URL | nuqs v2 |
| Gerenciador de pacotes | Bun |
| Infraestrutura | Docker Compose, multi-stage builds |

## Como executar

### Requisitos

- Docker e Docker Compose

### Início rápido

**Opção A — copiar o arquivo de exemplo:**
```bash
cp .env.example .env
```

**Opção B — colar diretamente (valores prontos para uso local):**
```env
# ─── PostgreSQL ───────────────────────────────────────────────
POSTGRES_USER=orders_user
POSTGRES_PASSWORD=orders_pass
POSTGRES_DB=orders_db
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Assembled by docker-compose — don't change unless you know what you're doing
DATABASE_URL=postgresql+asyncpg://orders_user:orders_pass@db:5432/orders_db
DATABASE_URL_SYNC=postgresql://orders_user:orders_pass@db:5432/orders_db

# ─── API ──────────────────────────────────────────────────────
API_HOST=0.0.0.0
API_PORT=8000

# CORS — comma-separated origins
CORS_ORIGINS=http://localhost:3000

# ─── Auth / JWT ───────────────────────────────────────────────
JWT_SECRET=change-me-in-production

NEXT_PUBLIC_API_URL=http://localhost:8000
```

**2. Suba todos os serviços (PostgreSQL + API + Frontend + ETL seed):**
```bash
docker compose up --build
```

A aplicação estará disponível nas URLs abaixo assim que os containers estiverem saudáveis.

### URLs locais

| Serviço | URL |
|---|---|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |

## Demo em produção

A aplicação está hospedada e acessível em:

| Serviço | URL |
|---|---|
| Frontend | https://avant-glp.lat/dashboard |
| API / Swagger | https://zaker.lat/docs |

### Hospedagem

O domínio e a infraestrutura são gerenciados pela **[Atlas Hosting](https://atlashosting.com.br)** — uma plataforma de hospedagem que eu mesmo desenvolvi com Next.js. O domínio foi comprado diretamente pela plataforma, que integra a **API da Namecheap** para registro de domínios e gerenciamento de DNS. Entre as funcionalidades:

- Registro de domínios integrado com a **API da Namecheap**
- Gerenciamento de DNS via **deSEC**
- Provisionamento automático de **certificados SSL**
- Planos de hospedagem com integração ao cPanel via **API do Plesk**
- Instalação de **WordPress** com um clique via API XML do WHMCS/Plesk
- Sistema de cobrança, pagamentos e programa de afiliados

A infraestrutura roda em um VPS com **Docker Swarm + Traefik** para roteamento e HTTPS automático.

### Executando os testes

```bash
docker compose exec api pytest tests/ -v
```

## Endpoints da API

| Método | Caminho | Descrição |
|---|---|---|
| `GET` | `/orders` | Lista paginada com filtros |
| `GET` | `/orders/{order_id}` | Detalhes do pedido com itens |
| `GET` | `/metrics` | Ticket médio, receita, top produtos, distribuição por status |

### Filtros — `GET /orders`

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `status` | enum | `processing`, `shipped`, `delivered`, `cancelled` |
| `customer_name` | string | Busca parcial sem distinção de maiúsculas |
| `date_from` | datetime | Pedidos criados a partir desta data |
| `date_to` | datetime | Pedidos criados até esta data |
| `min_value` | number | Valor mínimo do pedido |
| `max_value` | number | Valor máximo do pedido |
| `page` | int | Número da página (padrão: 1) |
| `page_size` | int | Itens por página (padrão: 20, máx: 100) |

## Arquitetura

### Backend — Clean Architecture

```
backend/
├── app/
│   ├── domain/          # Entidades, value objects, interfaces de repositório (Protocols)
│   ├── application/     # Casos de uso — orquestram domínio e repositórios
│   ├── infrastructure/  # Models SQLAlchemy, repositórios async, engine do banco
│   └── presentation/    # Routers FastAPI, schemas Pydantic, injeção de dependências
├── etl/                 # Pipeline de ingestão de CSV (validar → transformar → carregar)
├── migrations/          # Migrations Alembic
└── tests/
    ├── unit/            # Lógica de domínio e ETL (sem necessidade de banco)
    └── integration/     # Endpoints da API via TestClient
```

As interfaces de repositório são definidas como classes `Protocol` na camada de domínio. A camada de infraestrutura as implementa. Os casos de uso dependem apenas dos protocolos — nunca de implementações concretas.

### Frontend — Next.js App Router

```
frontend/src/
├── app/
│   ├── dashboard/       # Página principal (métricas, gráfico, tabela com filtros)
│   └── dashboard/[id]/  # Página de detalhes do pedido
├── components/
│   ├── ui/              # Primitivos do Shadcn/ui
│   └── *.tsx            # Componentes específicos do domínio
├── lib/
│   ├── api.ts           # Funções de fetch para cada endpoint
│   └── utils.ts         # cn(), formatCurrency(), formatDate()
└── types/               # Interfaces TypeScript espelhando os schemas da API
```

O estado dos filtros é sincronizado com a URL via **nuqs**, então os filtros sobrevivem a recarregamentos da página e podem ser compartilhados via link. A busca de dados utiliza **TanStack Query** para cache, deduplicação e estados de carregamento.

### Pipeline ETL

O ETL é idempotente — seguro para executar múltiplas vezes com o mesmo CSV:

1. **Validar** — regex, coerção de tipos, verificações de intervalo, ordenação de datas
2. **Transformar** — deduplicação de clientes/produtos por chave natural
3. **Carregar** — `ON CONFLICT DO UPDATE` para clientes, produtos e pedidos; `WHERE NOT EXISTS` para itens de pedido

Erros são gravados em `etl_errors.log` e um resumo em `etl_report.json`.

### Decisões técnicas

**`Protocol` em vez de `ABC` para interfaces de repositório** — a tipagem estrutural evita acoplamento por herança entre camadas. A camada de infraestrutura nunca importa da camada de domínio. Trocar o repositório PostgreSQL por um in-memory para testes não exige nenhuma alteração nas camadas superiores.

**`COUNT(*) OVER()`** — window function retorna o total junto com cada linha, evitando uma segunda query `COUNT(*)` separada para paginação. Uma query em vez de duas por listagem.

**`lazy="raise"` em todos os relacionamentos SQLAlchemy** — qualquer acesso a relacionamento não carregado explicitamente levanta uma exceção em vez de disparar uma query silenciosa. Previne queries N+1 acidentais; todos os joins são declarados explicitamente nos repositórios.

**`bindparams` com tipos explícitos** — o asyncpg não consegue inferir tipos PostgreSQL para parâmetros `None`. Usar `bindparam("status", type_=String)` informa ao SQLAlchemy o tipo correto para que o asyncpg emita a anotação de tipo no protocolo binário.

**Bun como gerenciador de pacotes** — em vez do npm ou yarn, o Bun instala dependências em média 10–25x mais rápido por usar um cache binário nativo e paralelizar downloads. O `bun.lock` é mais compacto que o `package-lock.json` e o build do Next.js roda via `bun run build` sem nenhuma configuração extra.

**nuqs para estado de filtros na URL** — em vez de `useState` local, os filtros de busca, status, data e valor são serializados como query params (`?status=shipped&page=2`). Isso permite compartilhar links com filtros aplicados, preservar o estado ao voltar no histórico do navegador e fazer deep link direto para uma busca específica.

**Shadcn/ui em vez de uma biblioteca de componentes fechada** — o Shadcn não é instalado como dependência; os componentes são copiados para `src/components/ui/` e pertencem ao projeto. Isso permite customizar tokens de design (cores, raios, espaçamentos) via variáveis CSS no `globals.css` sem sobrescrever estilos de terceiros ou depender de versões externas.

**Recharts para os gráficos** — biblioteca React-native baseada em SVG com API declarativa. O gráfico de barras (`BarChart`) e o donut (`PieChart`) em `status-chart.tsx` e `status-line-chart.tsx` são compostos com primitivos (` <Bar>`, `<Cell>`, `<Tooltip>`) sem configuração de canvas ou `useEffect`, mantendo o código legível e fácil de testar.

**bcrypt com tempo constante no login** — ao buscar um usuário por e-mail e não encontrá-lo, o código ainda executa `bcrypt.verify` com um hash fictício antes de retornar o erro. Isso garante que o tempo de resposta seja o mesmo independentemente de o e-mail existir ou não, prevenindo enumeração de usuários via timing attack.

**Zod para validação de formulários no frontend** — todos os formulários (login, cadastro, criação/edição de pedido, redefinição de senha) definem um schema Zod com mensagens de erro por campo. O `react-hook-form` integra via `zodResolver`, garantindo que nenhuma requisição seja enviada com dados inválidos e centralizando as regras de validação em um único lugar — as mesmas regras que geram os tipos TypeScript via `z.infer`.

**nuqs + TanStack Query em conjunto** — o nuqs serializa os filtros ativos como query params na URL (estado externo), enquanto o TanStack Query usa esses valores como `queryKey` para cache e deduplicação (estado de servidor). A combinação elimina `useEffect` para sincronizar filtros, garante que trocar um filtro invalide o cache automaticamente e mantém o estado de paginação e busca compartilhável via link.

**SQLAlchemy 2.0 async com asyncpg** — todos os repositórios usam `AsyncSession` e `async/await` nativos, sem misturar I/O síncrono na thread do event loop do uvicorn. O driver `asyncpg` usa o protocolo binário do PostgreSQL, mais eficiente que o protocolo texto do psycopg2. A API `select()` do SQLAlchemy 2.0 (estilo Core) é usada nos repositórios em vez do estilo ORM legado, dando controle explícito sobre os joins gerados.

**Alembic para migrations** — em vez de `Base.metadata.create_all()` que recria o schema do zero, o Alembic mantém um histórico versionado de alterações (`migrations/versions/`). Cada migration é reversível (`upgrade`/`downgrade`), o que permite rollback seguro em produção. O comando `alembic upgrade head` roda automaticamente no startup do container da API, garantindo que o schema esteja sempre atualizado antes de aceitar requisições.

**Multi-stage Docker builds** — o estágio `builder` instala compiladores (`gcc`, `libpq-dev`) e gera os artefatos; o estágio `runtime` copia apenas o venv compilado e o código, sem ferramentas de build. A imagem final é significativamente menor e não expõe dependências de compilação.

## ⭐ Funcionalidades extras — além do escopo

O desafio exigia três endpoints de leitura, um script ETL e um dashboard. Tudo abaixo foi construído além disso, sem ter sido solicitado.

### Sistema de autenticação

Um fluxo completo de autenticação JWT foi implementado de ponta a ponta:

| Funcionalidade | Detalhes |
|---|---|
| Cadastro | `POST /auth/register` — cria conta, retorna JWT |
| Login | `POST /auth/login` — valida credenciais, retorna JWT |
| Esqueci a senha | `POST /auth/forgot-password` — envia link de redefinição por e-mail via SMTP |
| Redefinir senha | `POST /auth/reset-password/{token}` — valida token JWT assinado (TTL de 30 min, claim `"reset"`), atualiza a senha |
| Rotas protegidas | `POST /orders`, `PUT /orders/{id}`, `POST /orders/import` exigem Bearer token |

### Endpoints de escrita

| Método | Caminho | Descrição |
|---|---|---|
| `POST` | `/orders` | Cria um novo pedido com dados completos de cliente e itens |
| `PUT` | `/orders/{order_id}` | Edita um pedido existente (itens substituídos integralmente) |
| `POST` | `/orders/import` | Faz upload de um CSV, processa pelo ETL e retorna relatório |

O frontend disponibiliza um formulário completo de criação/edição de pedidos com preenchimento automático de CEP (ViaCEP), máscara de moeda, dropdown de busca de categoria e seletor de status.

### Importação de CSV pela interface

Usuários autenticados podem fazer upload de um arquivo `.csv` diretamente pelo dashboard. O arquivo é enviado para um **bucket S3-compatível da Storj** antes do processamento pelo ETL, mantendo um registro permanente de cada importação. A resposta inclui contagens de linhas (válidas, inválidas, erros) e a chave S3.

### Segurança

- **Rate limiting** — `slowapi` limita login a 5 req/min, cadastro a 10 req/min e esqueci-a-senha a 3 req/min por IP (HTTP 429)
- **Login com tempo constante** — o bcrypt é sempre executado mesmo quando o e-mail não existe, prevenindo enumeração de usuários via tempo de resposta
- **Headers de segurança** — toda resposta inclui `X-Frame-Options: DENY`, `X-Content-Type-Options: nosniff`, `Strict-Transport-Security`, `Referrer-Policy` e `Permissions-Policy`
- **Força de senha** — mínimo de 8 caracteres com pelo menos um dígito, validado tanto no backend (Pydantic `field_validator`) quanto no frontend (schema Zod)
- **Validação com Zod** — todos os formulários do frontend validam com Zod antes de enviar qualquer requisição, com mensagens de erro por campo

## O que eu faria diferente

**Controle de acesso baseado em papéis (RBAC)** — a tabela `users` e as claims do JWT já estão implementadas. Adicionar um campo `role` (`admin` / `viewer`) permitiria restringir operações de escrita apenas a admins. Um papel de super-admin poderia gerenciar contas e criar novos usuários, transformando o sistema em um painel multi-tenant.

**Isolamento de dados por usuário** — atualmente todos os usuários autenticados compartilham a mesma lista de pedidos. Com uma coluna `tenant_id` ou `owner_id` em `orders`, cada usuário (ou equipe) veria apenas seus próprios dados. Uma conta de super-admin manteria visibilidade global.

**ETL orientado a eventos** — substituir o script pontual por uma fila de mensagens (RabbitMQ ou AWS SQS). Novos arquivos CSV seriam depositados no object storage, disparando um worker assíncrono. Isso habilita retries, filas de dead-letter e escalonamento horizontal sem bloquear a API.

**Cache com Redis para métricas** — o endpoint `/metrics` agrega toda a tabela `order_items` a cada requisição. Com Redis, os resultados poderiam ser cacheados com TTL curto e invalidados ao término do ETL.

**Modelos separados de leitura e escrita (CQRS)** — os repositórios atuais atendem tanto leituras quanto escritas. Um modelo de leitura dedicado com views pré-agregadas ou uma réplica de leitura melhoraria o desempenho das queries em escala.

**Jobs em background para relatórios** — exports pesados (CSV, PDF) deveriam ser enfileirados e entregues de forma assíncrona em vez de bloquear uma requisição HTTP.

**Observabilidade** — logging estruturado (JSON), rastreamento distribuído (OpenTelemetry) e um endpoint de métricas (Prometheus) tornariam incidentes em produção muito mais fáceis de diagnosticar.

**Testes E2E com Playwright** — os testes de integração cobrem o contrato da API, mas não a interação no navegador. Testes Playwright validariam o comportamento dos filtros, paginação, fluxos de formulário e redirecionamentos de rotas protegidas de ponta a ponta.

**Testes de contrato** — além dos testes de integração, testes de contrato orientados ao consumidor (Pact) detectariam breaking changes na API antes de chegarem à produção, especialmente úteis conforme frontend e backend evoluem de forma independente.
