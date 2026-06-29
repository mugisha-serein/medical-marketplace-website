# MedEquip Backend API Documentation

Last updated: 2026-06-29

This document describes the current Django + DRF backend after the SQLite presentation MVP cleanup. It is the source of truth for the active backend folder structure, active API routes, runtime assumptions, and intentionally disabled or removed backend pieces.

## 1. Current backend purpose

The backend is a small medical equipment marketplace API for a presentation MVP. It supports:

- public product discovery;
- public product details;
- public category listing;
- buyer inquiry submission;
- vendor/admin inquiry listing;
- health and readiness checks;
- explicit demo-data seeding through a management command.

The backend no longer depends on PostgreSQL, Redis, Celery, Flower, Nginx, or first-request demo seeding for the MVP runtime.

## 2. Runtime stack

| Area | Current MVP choice |
| --- | --- |
| Web framework | Django + Django REST Framework |
| Database | SQLite |
| Cache | Django local-memory cache |
| API base path | `/api/v1/` |
| Background jobs | None for MVP |
| Demo data | `python manage.py seed_demo` |
| Docker services | Single Django web service |
| Active stock source | `catalog.Product.stock_quantity` |
| Active response style | Raw DRF `Response` payloads |

## 3. Active backend folder structure

```text
backend/
├── API_DOCUMENTATION.md              # Current API and backend structure guide
├── README.md                         # Short backend overview and quick-start notes
├── Dockerfile                        # SQLite MVP runtime image
├── docker-compose.yml                # Single-service SQLite MVP compose setup
├── manage.py                         # Django CLI entrypoint
├── requirements.txt                  # Python dependencies for the MVP
├── config/
│   ├── __init__.py                   # Django project package; no Celery import
│   ├── urls.py                       # Root URL router: admin + /api/v1/ only
│   ├── health.py                     # Health/readiness URL patterns and handlers
│   ├── permission.py                 # Shared permissions such as IsVendorOrAdmin
│   ├── api/
│   │   └── v1/
│   │       └── urls.py               # Versioned API router
│   └── settings/
│       ├── base.py                   # SQLite-first shared settings
│       ├── development.py            # Local development overrides
│       └── production.py             # Production-style SQLite MVP settings
├── apps/
│   ├── accounts/                     # User and profile models used by demo/vendor data
│   ├── catalog/
│   │   ├── models.py                 # Category, Tag, Product, ProductImage
│   │   ├── serializers.py            # Public product/category serializers
│   │   ├── urls.py                   # Public catalog routes only
│   │   ├── views.py                  # Product list, product detail, category list
│   │   ├── services/
│   │   │   ├── __init__.py           # Stable service facade
│   │   │   └── catalog_service.py    # SearchService and ProductService
│   │   └── management/
│   │       └── commands/
│   │           └── seed_demo.py      # Explicit demo-only seeding command
│   ├── inquiries/
│   │   ├── models.py                 # Buyer inquiry model
│   │   ├── serializers.py            # Inquiry request/response serializer
│   │   ├── urls.py                   # Inquiry route
│   │   └── views.py                  # Public POST, protected GET
│   └── inventory/                    # Dormant code; disabled for SQLite MVP
└── media/                            # Local uploaded media during development/runtime
```

## 4. Active Django apps

Only these local apps are active in `INSTALLED_APPS`:

- `apps.accounts`
- `apps.catalog`
- `apps.inquiries`

`apps.inventory` is intentionally disabled for the MVP. Its code can remain in the repository for future post-MVP work, but it is not installed and its tables are not created by `migrate --run-syncdb`.

## 5. Database and migrations

The MVP uses SQLite through `SQLITE_DATABASE_PATH`.

```bash
SQLITE_DATABASE_PATH=/path/to/db.sqlite3
```

Local app migrations are disabled for the simplified MVP so tables are created directly from the current models:

```bash
python manage.py migrate --run-syncdb
```

The active migration-disabled local apps are:

- `accounts`
- `catalog`
- `inquiries`

`inventory` is no longer in this list because it is not an active installed app.

## 6. API base URL

All public MVP APIs are mounted under:

```text
/api/v1/
```

Removed legacy aliases:

```text
/api/catalog/
/api/inquiries/
```

Those unversioned aliases should not be used by the frontend or by API clients.

## 7. Root routes

| Method | Path | Purpose |
| --- | --- | --- |
| any | `/admin/` | Django admin |
| any | `/api/v1/` | Versioned API router |

During `DEBUG=True`, Django also serves local media through `MEDIA_URL`.

## 8. Health API

### `GET /api/v1/health/`

Runs the main health check.

Response shape:

```json
{
  "success": true,
  "message": "Health check complete",
  "data": {
    "database": {"status": "ok", "latency_ms": 1.23},
    "cache": {"status": "ok", "latency_ms": 0.45}
  }
}
```

### `GET /api/v1/health/live/`

Alias for the same health check behavior.

### `GET /api/v1/health/ready/`

Readiness check for database/cache availability.

Response shape:

```json
{
  "success": true,
  "message": "Readiness check complete",
  "data": {
    "database": "ready",
    "cache": "ready"
  }
}
```

## 9. Catalog API

Catalog routes are mounted under:

```text
/api/v1/catalog/
```

### `GET /api/v1/catalog/products/`

Returns active products with pagination and optional filters.

Query parameters:

| Parameter | Description |
| --- | --- |
| `q` | Text search across name, short description, description, manufacturer, and model number |
| `category` | Category slug |
| `min_price` | Minimum price filter |
| `max_price` | Maximum price filter |
| `condition` | Product condition |
| `vendor_id` | Vendor profile id |
| `is_featured` | Use `true` for featured products |
| `ordering` | One of `price`, `-price`, `name`, `-name`, `created_at`, `-created_at` |
| `page` | Page number; defaults to `1` |
| `page_size` | Page size; defaults to `20`, max `100` |

Response shape:

```json
{
  "count": 4,
  "page": 1,
  "page_size": 20,
  "results": [
    {
      "id": "uuid",
      "name": "Digital Patient Monitor",
      "slug": "digital-patient-monitor",
      "sku": "MVP-MON-001",
      "price": "850.00",
      "condition": "new",
      "short_description": "Portable 5-parameter monitor for clinics and emergency rooms.",
      "manufacturer": "MedCore",
      "model_number": "MC-PM100",
      "category_name": "Patient Care",
      "vendor_name": "Kigali MedSupply Co.",
      "primary_image": null,
      "is_featured": true,
      "in_stock": true,
      "stock_quantity": 12,
      "created_at": "2026-06-29T00:00:00Z"
    }
  ]
}
```

### `GET /api/v1/catalog/products/<slug>/`

Returns one active product by slug.

Success response is raw product serializer data:

```json
{
  "id": "uuid",
  "name": "Digital Patient Monitor",
  "slug": "digital-patient-monitor",
  "sku": "MVP-MON-001",
  "price": "850.00",
  "condition": "new",
  "description": "...",
  "short_description": "...",
  "manufacturer": "MedCore",
  "model_number": "MC-PM100",
  "specifications": {},
  "category": {},
  "tags": [],
  "vendor": {
    "id": "uuid",
    "company_name": "Kigali MedSupply Co.",
    "is_verified": true,
    "website": "https://example.com"
  },
  "images": [],
  "is_featured": true,
  "stock_quantity": 12,
  "created_at": "2026-06-29T00:00:00Z",
  "updated_at": "2026-06-29T00:00:00Z"
}
```

Not found response:

```json
{
  "detail": "Not found."
}
```

### `GET /api/v1/catalog/categories/`

Returns active root categories with nested active children.

Response shape:

```json
[
  {
    "id": "uuid",
    "name": "Diagnostics",
    "slug": "diagnostics",
    "description": "Tools for examination, imaging and diagnosis.",
    "image": null,
    "parent": null,
    "children": []
  }
]
```

## 10. Inquiries API

Inquiry routes are mounted under:

```text
/api/v1/inquiries/
```

### `POST /api/v1/inquiries/`

Public buyer inquiry submission. No authentication is required.

Request body:

```json
{
  "product_slug": "digital-patient-monitor",
  "product_name": "Digital Patient Monitor",
  "buyer_name": "Jane Buyer",
  "buyer_email": "jane@example.com",
  "buyer_phone": "+250700000000",
  "organization": "Kigali Clinic",
  "quantity": 2,
  "message": "Please send availability and delivery details."
}
```

Field notes:

- `buyer_name` is required.
- `buyer_email` is required.
- `quantity` must be at least `1`.
- `product_slug` is optional; when provided, it resolves to a product and can auto-fill `product_name` if missing.
- `status` is read-only and defaults to `new`.

Success response uses raw serializer data:

```json
{
  "id": "uuid",
  "product": "uuid-or-null",
  "product_name": "Digital Patient Monitor",
  "buyer_name": "Jane Buyer",
  "buyer_email": "jane@example.com",
  "buyer_phone": "+250700000000",
  "organization": "Kigali Clinic",
  "quantity": 2,
  "message": "Please send availability and delivery details.",
  "status": "new",
  "created_at": "2026-06-29T00:00:00Z"
}
```

### `GET /api/v1/inquiries/`

Returns the latest 50 inquiries.

Permission:

- vendor users: allowed;
- admin/staff users: allowed;
- anonymous users: denied.

Response shape:

```json
[
  {
    "id": "uuid",
    "product": "uuid-or-null",
    "product_name": "Digital Patient Monitor",
    "buyer_name": "Jane Buyer",
    "buyer_email": "jane@example.com",
    "buyer_phone": "+250700000000",
    "organization": "Kigali Clinic",
    "quantity": 2,
    "message": "Please send availability and delivery details.",
    "status": "new",
    "created_at": "2026-06-29T00:00:00Z"
  }
]
```

## 11. Accounts app status

`apps.accounts` is active because the custom user model and vendor profile are required by catalog products and demo seeding.

The account URL module still exists, but account routes are not mounted in the current `/api/v1/` router. Do not document or call account endpoints as active public MVP APIs unless the versioned router is updated to include them.

## 12. Inventory app status

`apps.inventory` is disabled for the SQLite MVP.

Reason:

- `catalog.Product.stock_quantity` is the single active stock source for the MVP.
- `inventory.StockRecord` also had quantity fields, which created two stock sources of truth.
- The inventory app is not mounted in API routes and is not installed for the MVP runtime.

Future post-MVP options:

1. delete inventory fully if simple product stock is enough; or
2. re-enable inventory and remove `Product.stock_quantity`, making `StockRecord` the single source of truth.

Do not use both active stock systems together.

## 13. Demo data command

Demo data is seeded explicitly:

```bash
python manage.py seed_demo
```

Optional demo vendor login:

```bash
DEMO_VENDOR_PASSWORD='your-demo-only-password' python manage.py seed_demo
```

or:

```bash
python manage.py seed_demo --vendor-password 'your-demo-only-password'
```

Security rule:

- demo users are demo-only;
- no hardcoded demo password exists in catalog services;
- if no demo password is provided, the demo vendor cannot log in unless an existing usable password already exists.

## 14. Response format policy

The MVP uses raw DRF `Response` payloads for catalog and inquiry APIs.

Rules:

- Do not add per-view `success_response()` or `error_response()` helpers.
- Do not mix `{success, message, data}` envelopes into catalog/inquiry views.
- Return serializer data directly for successful resource responses.
- Use DRF-style `detail` payloads for simple errors.
- Health endpoints are the exception because they intentionally return `{success, message, data}` for infrastructure checks.

## 15. Removed or disabled backend pieces

The following were removed, disabled, or made dormant during the MVP cleanup:

| Area | Current decision |
| --- | --- |
| Celery import in `config/__init__.py` | Removed; Django startup no longer imports Celery |
| PostgreSQL/Redis runtime requirement | Removed for MVP; SQLite + locmem cache are used |
| Docker PostgreSQL/Redis/Celery/Flower/Nginx services | Removed; Compose runs only Django web |
| First-request demo seeding | Removed; seeding is now `seed_demo` command only |
| Hardcoded demo password in service code | Removed; optional env/CLI password only |
| Public inquiry list | Protected; only vendor/admin can GET inquiries |
| Inventory app | Disabled; product stock is the MVP source |
| Duplicate `services.py` and `services/` catalog modules | Consolidated into `services/catalog_service.py` |
| Duplicate unversioned API aliases | Removed; use `/api/v1/...` only |
| Unused catalog views | Removed from MVP views |
| Local catalog response helpers | Removed; raw DRF responses are used |

## 16. Local setup

From the `backend/` directory:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --run-syncdb
python manage.py seed_demo
python manage.py runserver
```

The API will be available at:

```text
http://localhost:8000/api/v1/
```

## 17. Docker setup

From the `backend/` directory:

```bash
docker compose up --build
```

The compose service runs:

```bash
python manage.py migrate --run-syncdb --noinput
python manage.py seed_demo
python manage.py runserver 0.0.0.0:8000
```

Persistent volumes:

- `sqlite_data` mounted to `/app/data`
- `media_files` mounted to `/app/media`

## 18. Environment variables

| Variable | Purpose | Default |
| --- | --- | --- |
| `DJANGO_SETTINGS_MODULE` | Settings module | `config.settings.development` in Docker |
| `SECRET_KEY` | Django secret | development fallback exists |
| `DEBUG` | Debug mode | `true` locally |
| `ENVIRONMENT` | Runtime name | `development` |
| `ALLOWED_HOSTS` | Comma-separated hosts | `localhost,127.0.0.1` |
| `CORS_ALLOWED_ORIGINS` | Comma-separated frontend origins | local Vite origins |
| `FRONTEND_URL` | Frontend base URL | `http://localhost:5173` |
| `PUBLIC_API_URL` | Public API base URL | `http://localhost:8000/api/v1` |
| `SQLITE_DATABASE_PATH` | SQLite database path | `BASE_DIR/db.sqlite3` or `/app/data/db.sqlite3` in Docker |
| `DEMO_VENDOR_EMAIL` | Demo-only vendor email | `vendor@medequip.local` |
| `DEMO_VENDOR_PASSWORD` | Optional demo-only vendor password | unset |
| `SECURE_SSL_REDIRECT` | HTTPS-only production toggle | `false` |

## 19. Frontend integration contract

Frontend API clients must call only:

```text
/api/v1/health/
/api/v1/catalog/products/
/api/v1/catalog/products/<slug>/
/api/v1/catalog/categories/
/api/v1/inquiries/
```

Do not call removed aliases:

```text
/api/catalog/
/api/inquiries/
```

## 20. Future backend work notes

Before expanding beyond the MVP:

1. Decide whether `accounts` routes should be mounted under `/api/v1/auth/`.
2. Decide whether vendor product management belongs in the MVP API.
3. Decide whether inventory should stay disabled or become the only stock source.
4. Add tests for the documented endpoint contract.
5. Add OpenAPI/schema generation only after the route surface is stable.
