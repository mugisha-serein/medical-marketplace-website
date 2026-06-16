# MedEquip Backend

This backend powers a hospital equipment marketplace where three user groups collaborate in one system: customers who search and buy equipment, vendors who publish products and manage stock, and administrators who supervise operations. The project is built with Django and Django REST Framework, with PostgreSQL as the primary data store, Redis for cache and fast ephemeral state, and Celery for background and scheduled work. In practice, this backend is responsible for identity, catalog discovery, cart state, transactional ordering, stock integrity, customer communication, and KPI reporting.

At a high level, the architecture is intentionally layered. HTTP requests enter through Django endpoints, business rules are executed in service modules, durable records are stored in PostgreSQL models, and cross-cutting asynchronous tasks are delegated to Celery workers. Redis is used where speed and temporary state are important, especially for carts, cache, and real-time counters. This split keeps user-facing responses fast while protecting critical workflows such as inventory deduction and order creation with transactional guarantees.

## Folder Structure

|-- backend/
|-- apps/
|   |-- accounts/           # auth, users, profiles, JWT endpoints
|   |-- catalog/            # categories, products, search, vendor product CRUD
|   |-- cart/               # Redis-backed cart APIs and validation
|   |-- orders/             # transactional checkout and order lifecycle
|   |-- inventory/          # stock records, movement logs, reconciliation
|   |-- kpi/                # KPI snapshots, dashboard and timeseries APIs
|   |-- notification/       # async email tasks and delivery logs
|   |-- inquiries/          # inquiry module scaffold (in progress)
|-- config/
|   |-- settings/
|   |   |-- base.py         # shared settings
|   |   |-- development.py  # local/dev overrides
|   |   `-- production.py   # production hardening and external services
|   |-- urls.py             # root URL router
|   |-- health.py           # health check endpoint
|   |-- celery.py           # Celery app and beat schedule
|   `-- permission.py       # custom permissions, pagination, exception handling
|-- nginx/
|   `-- nginx.conf          # reverse proxy, rate limits, headers
|-- tests/                  # pytest suite and factories
|-- scripts/                # scaffold app (placeholder)
|-- Dockerfile              # production image build
|-- docker-compose.yml      # local multi-service stack
|-- requirements.txt        # Python dependencies
|-- pytest.ini              # test configuration
`-- manage.py               # Django CLI entrypoint (Root)
```

## System Flow as a Business Story

The normal journey begins in `accounts`, where a user registers as either a customer or a vendor. Authentication uses JWT tokens, and profile endpoints expose role-aware data so the frontend can tailor the experience. Once authenticated, customers browse public products from `catalog`, while vendors can create and manage their own listings, upload product images, and maintain active/inactive status.

When a customer adds items to cart, the `cart` service stores cart data in Redis rather than in relational tables for fast reads and sliding expiration. Each cart item captures a price snapshot at add/update time, and checkout validation rechecks both stock and product availability to protect against stale carts. This means the cart behaves as a fast staging area, while final truth is still enforced during order placement.

Order placement happens in `orders` and is treated as an atomic operation. The service validates the cart, calculates totals from snapshots, creates an order and immutable order items, deducts stock through inventory locks, writes a status log, clears the cart, and only then commits. After commit, background tasks send confirmation emails and update KPI counters. If any critical step fails before commit, the transaction is rolled back, preventing partial or inconsistent orders.

Stock control in `inventory` is the integrity center of the platform. Mutations run through service methods that use row-level locking (`SELECT FOR UPDATE NOWAIT`) and write immutable movement records for a full audit trail. This prevents overselling under concurrent load and keeps every change explainable later. A scheduled reconciliation task can re-derive stock from movement history and repair drift if needed.

Operational intelligence is handled in `kpi`. The app stores denormalized snapshots for historical metrics and combines them with real-time Redis counters for same-day visibility. This design avoids expensive live aggregations in API requests and makes KPI endpoints predictable in latency while still being near-real-time for dashboard use cases.

Customer and transactional messaging is handled in the notifications subsystem (`apps/notification`). Email tasks are idempotent through an `EmailLog` model, so retries do not produce duplicate sends. Notifications cover welcome messages, order confirmations, and selected order state updates (such as shipped or delivered), with retry behavior managed by Celery.

## Codebase Parts and Their Responsibilities

### `config/` (platform wiring)

The `config` package is the application spine. It defines settings, middleware, app registration, DRF defaults, JWT behavior, Redis and Celery configuration, logging format, and documentation endpoints. It also contains the root URL map, health check endpoint, and role-based permission classes. Environment-specific settings are split into `development.py` and `production.py`, while `base.py` carries shared defaults. In other words, `config` describes how the whole backend behaves as a running platform.

### `apps/accounts/` (identity and profiles)

`accounts` introduces a custom `User` model keyed by email and extended with role flags (`is_vendor`, `is_staff`) and profile links. It supports registration for both customers and vendors, JWT login/refresh/logout, profile retrieval and updates, and password change flows. The serializers enrich tokens with role and identity metadata, enabling role-aware clients without extra lookups.

### `apps/catalog/` (product discovery and vendor listings)

`catalog` models categories, tags, products, and product images. It supports searchable and filterable listing, detail views, and vendor-scoped CRUD for product management. The service layer handles search caching, product cache invalidation, and slug generation. Search combines PostgreSQL full-text indexing with structured filters, which gives the marketplace a scalable discovery path.

### `apps/cart/` (fast temporary cart state)

`cart` is implemented as a Redis-backed JSON cart service with API endpoints for read, add, update, remove, and clear operations. Its key responsibilities are enforcing quantity and availability checks before items accumulate, maintaining price snapshots, and validating cart integrity immediately before checkout. This approach keeps cart interactions lightweight while still handing final correctness to the order transaction.

### `apps/orders/` (transactional checkout and lifecycle)

`orders` manages the order state machine and immutable order snapshots. It provides customer order listing/detail/cancel flows, vendor-facing order visibility, and controlled status transitions. The service layer coordinates checkout with inventory locks and writes a status audit trail for each transition. It is the module where business consistency is most strongly enforced through database transactions.

### `apps/inventory/` (stock truth and auditability)

`inventory` owns current stock records and stock movement history. Every stock change, whether sale, restock, adjustment, or reconciliation, is recorded as a movement entry. API endpoints allow authorized vendor/admin users to inspect stock, adjust levels, restock, and inspect movement history. Scheduled tasks provide background reconciliation and initial stock record creation.

### `apps/kpi/` (analytics snapshots and dashboard data)

`kpi` stores normalized metric snapshots by period and dimension (overall, vendor, category, product). Celery tasks compute snapshots on schedule and increment real-time counters after order events. API endpoints return dashboard summaries and time-series datasets, with permission rules that let vendors see their own lens and admins see global or filtered views.

### `apps/notification/` (async email delivery)

The notification app tracks outgoing emails in `EmailLog` and sends email asynchronously via Celery tasks. The idempotency strategy is critical: each email type plus reference ID pair is unique, so retries and duplicate dispatches are safely absorbed. This reduces accidental duplicate customer communication while preserving reliability under transient email failures.

### `apps/inquiries/` and `scripts/` (currently scaffolded)

Both `apps/inquiries` and `scripts` are mostly placeholders in the current repository state, with minimal default files and no finalized domain implementation. Tests and task references indicate intended future inquiry workflows (submission, vendor follow-up, and notification integration), but the concrete model/view implementation is not yet present in this folder state.

### `tests/` (behavioral contract)

The test suite is designed around business behavior rather than only unit-level internals. It covers registration/login, catalog filtering, cart validation, transactional order behavior, inventory movements, KPI responses, health checks, and notification idempotency. This test structure communicates expected platform guarantees, especially around rollback safety, non-duplication, and permissions.

## Runtime and Operations

Docker and Compose files define a full local stack: PostgreSQL, Redis, Django web app, Celery worker, Celery beat, Flower monitoring, and Nginx. Nginx adds rate limiting and security headers, while Django health checks report database/cache readiness. In production settings, security hardening, secure cookies, HSTS, and external storage/email providers are enabled, reflecting a deployment path intended for internet-facing workloads.

## Current State Notes

The repository currently mixes implemented modules and in-progress wiring. Several imports and URL includes reference names such as `apps.notifications` or dedicated `urls.py` modules that do not yet fully match the existing directory/file layout (`apps/notification`, URL patterns embedded in some `views.py` files). The business intent is clear and largely documented by services and tests, but final integration cleanup is still needed before treating the system as fully production-ready.
