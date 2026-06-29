# MedEquip Backend

This backend is the Django + Django REST Framework API for the MedEquip SQLite presentation MVP.

The current MVP backend is intentionally small and local-first:

- SQLite database
- local-memory cache
- single Django web service
- versioned API routes under `/api/v1/`
- explicit demo seeding with `python manage.py seed_demo`
- no PostgreSQL, Redis, Celery, Flower, or Nginx runtime dependency

For the complete API contract, backend folder structure, runtime decisions, removed/disabled modules, and frontend integration notes, read:

```text
backend/API_DOCUMENTATION.md
```

## Active API surface

```text
/api/v1/health/
/api/v1/health/live/
/api/v1/health/ready/
/api/v1/catalog/products/
/api/v1/catalog/products/<slug>/
/api/v1/catalog/categories/
/api/v1/inquiries/
```

Removed legacy aliases:

```text
/api/catalog/
/api/inquiries/
```

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate --run-syncdb
python manage.py seed_demo
python manage.py runserver
```

The API runs at:

```text
http://localhost:8000/api/v1/
```

## Docker setup

```bash
docker compose up --build
```

Docker runs a single Django web service and stores SQLite data in the `sqlite_data` volume.

## Current backend decisions

- `Product.stock_quantity` is the active MVP stock source.
- `apps.inventory` is disabled for the MVP.
- Demo data is seeded only by the `seed_demo` management command.
- Catalog and inquiry views use raw DRF `Response` payloads.
- Catalog services live in `apps/catalog/services/catalog_service.py` and are re-exported from `apps.catalog.services`.
- Unused presentation-MVP catalog views were removed.
