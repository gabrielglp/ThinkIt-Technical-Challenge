# Orders Dashboard

Fullstack application for e-commerce order management. Built as a technical challenge with FastAPI, Next.js 16, PostgreSQL and Docker Compose.

## Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, FastAPI, SQLAlchemy 2.0 (async), Alembic |
| Database | PostgreSQL 16 |
| Frontend | Next.js 16, React 19, TypeScript, TanStack Query v5 |
| UI | Shadcn/ui, Tailwind CSS, Recharts |
| URL State | nuqs v2 |
| Package Manager | Bun |
| Infrastructure | Docker Compose, multi-stage builds |

## Getting started

### Requirements

- Docker and Docker Compose

### Quick start

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Start all services (PostgreSQL + API + Frontend)
docker compose up --build

# 3. (Optional) Populate the database from the sample CSV
docker compose --profile etl up etl
```

The application will be available at the URLs below as soon as the containers are healthy.

### URLs

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| API | http://localhost:8000 |
| Swagger | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |

### Running tests

```bash
docker compose exec api pytest tests/ -v
```

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/orders` | Paginated list with filters |
| `GET` | `/orders/{order_id}` | Order detail with items |
| `GET` | `/metrics` | Average ticket, revenue, top products, status breakdown |

### Filters — `GET /orders`

| Parameter | Type | Description |
|---|---|---|
| `status` | enum | `processing`, `shipped`, `delivered`, `cancelled` |
| `customer_name` | string | Case-insensitive partial match |
| `date_from` | datetime | Orders created from this date |
| `date_to` | datetime | Orders created up to this date |
| `min_value` | number | Minimum order total |
| `max_value` | number | Maximum order total |
| `page` | int | Page number (default: 1) |
| `page_size` | int | Items per page (default: 20, max: 100) |

## Architecture

### Backend — Clean Architecture

```
backend/
├── app/
│   ├── domain/          # Entities, value objects, repository interfaces (Protocols)
│   ├── application/     # Use cases — orchestrate domain and repositories
│   ├── infrastructure/  # SQLAlchemy models, async repositories, DB engine
│   └── presentation/    # FastAPI routers, Pydantic schemas, dependency injection
├── etl/                 # CSV ingestion pipeline (validate → transform → load)
├── migrations/          # Alembic migrations
└── tests/
    ├── unit/            # Domain and ETL logic (no DB required)
    └── integration/     # API endpoints via TestClient
```

Repository interfaces are defined as `Protocol` classes in the domain layer. The infrastructure layer implements them. Use cases depend only on the protocols — never on concrete implementations.

### Frontend — Next.js App Router

```
frontend/src/
├── app/
│   ├── orders/          # Dashboard page (metrics, chart, table with filters)
│   └── orders/[id]/     # Order detail page
├── components/
│   ├── ui/              # Shadcn/ui primitives
│   └── *.tsx            # Domain-specific components
├── lib/
│   ├── api.ts           # Fetch functions for each endpoint
│   └── utils.ts         # cn(), formatCurrency(), formatDate()
└── types/               # TypeScript interfaces mirroring API schemas
```

Filter state is synced to the URL via **nuqs**, so filters survive page refreshes and can be shared via link. Data fetching uses **TanStack Query** for caching, deduplication and loading states.

### ETL pipeline

The ETL is idempotent — safe to run multiple times against the same CSV:

1. **Validate** — regex, type coercion, range checks, date ordering
2. **Transform** — deduplicate customers/products by natural key
3. **Load** — `ON CONFLICT DO UPDATE` for customers, products and orders; `WHERE NOT EXISTS` for order items

Errors are written to `etl_errors.log` and a summary to `etl_report.json`.

### Key technical decisions

**`Protocol` over `ABC` for repository interfaces** — structural typing avoids inheritance coupling between layers. The infrastructure layer never imports from the domain layer.

**`COUNT(*) OVER()`** — window function returns the total count alongside each row, avoiding a separate `COUNT(*)` query for pagination.

**`lazy="raise"` on all SQLAlchemy relationships** — prevents accidental N+1 queries. All joins are explicit in the repository SQL.

**`bindparams` with explicit types** — asyncpg cannot infer PostgreSQL types for `None` parameters. Using `bindparam("status", type_=String)` tells SQLAlchemy the type so asyncpg can emit the correct type annotation.

**Bun as package manager** — faster installs, native lockfile, compatible with Next.js 16.

**Multi-stage Docker builds** — builder stages include compilers and dev dependencies; the runtime image copies only the compiled output, resulting in a smaller final image.

## What I would do differently

**Event-driven ETL** — replace the one-shot script with a message queue (RabbitMQ or AWS SQS). New CSV files would be dropped into object storage, triggering an async worker. This enables retries, dead-letter queues and horizontal scaling without blocking the API.

**Redis caching for metrics** — the `/metrics` endpoint aggregates the entire `order_items` table on every request. With Redis, results could be cached with a short TTL and invalidated on ETL completion.

**Separate read/write models (CQRS)** — the current repositories serve both reads and writes. A dedicated read model with pre-aggregated views or a read replica would improve query performance at scale.

**Background jobs for reports** — heavy exports (CSV, PDF) should be queued and delivered asynchronously rather than blocking an HTTP request.

**E2E tests with Playwright** — the integration tests cover the API contract but not the browser interaction. Playwright tests would validate filter behavior, pagination and navigation end-to-end.
