# MVP Ecommerce Backend Architecture

This backend is for a small ecommerce website that sells medical equipment only.

The MVP should stay simple. Its job is to show products, organize them by category, show product details, capture buyer inquiries, and support the minimum seller/admin data needed for those flows.

## Architecture goals

- Keep the API small and easy to test.
- Keep medical equipment catalog data as the center of the system.
- Avoid unrelated modules such as KPI, analytics, content, social, or event features.
- Keep one clear route prefix: `/api/v1/`.
- Keep one active stock source: `Product.stock_quantity`.
- Keep demo data outside request handling.
- Prefer direct Django REST Framework responses.

## Recommended backend folder structure

```text
backend/
├── manage.py
├── requirements.txt
├── README.md
├── API_DOCUMENTATION.md
├── SCOPE.md
├── MVP_ARCHITECTURE.md
├── Dockerfile
├── docker-compose.yml
├── config/
│   ├── __init__.py
│   ├── urls.py
│   ├── health.py
│   ├── permission.py
│   ├── api/
│   │   └── v1/
│   │       └── urls.py
│   └── settings/
│       ├── base.py
│       ├── development.py
│       └── production.py
└── apps/
    ├── accounts/
    │   ├── models.py
    │   ├── serializers.py
    │   ├── views.py
    │   └── urls.py
    ├── catalog/
    │   ├── models.py
    │   ├── serializers.py
    │   ├── views.py
    │   ├── urls.py
    │   ├── services/
    │   │   ├── __init__.py
    │   │   └── catalog_service.py
    │   └── management/
    │       └── commands/
    │           └── seed_demo.py
    └── inquiries/
        ├── models.py
        ├── serializers.py
        ├── views.py
        └── urls.py
```

## App responsibilities

### `config/`

Owns project wiring only:

- settings;
- root URL routing;
- versioned API routing;
- health checks;
- shared permission classes.

It should not contain business logic.

### `apps.accounts/`

Owns only identity data needed by ecommerce:

- custom user model;
- seller/vendor profile;
- customer profile if needed by inquiries or future checkout;
- authentication only if mounted later.

For the current MVP, accounts support catalog ownership and demo vendor data. Account routes should not be treated as active public API routes unless they are mounted under `/api/v1/`.

### `apps.catalog/`

This is the core app.

It owns:

- medical equipment categories;
- medical equipment products;
- product images;
- product tags if needed for product search;
- public product search/listing;
- public product detail;
- stock availability through `Product.stock_quantity`;
- demo product seeding.

It should not own buyer inquiry workflow, checkout, analytics, or reporting.

### `apps.inquiries/`

Owns buyer contact requests.

It supports:

- public inquiry creation;
- protected inquiry listing for vendor/admin users;
- basic inquiry status.

It should stay small until the MVP needs a real order or checkout flow.

### `apps.inventory/`

Inventory is currently out of the active MVP runtime.

Do not enable this app while `Product.stock_quantity` is the active stock field. If inventory is needed later, choose one stock source only:

1. keep `Product.stock_quantity` and delete inventory; or
2. re-enable inventory and remove product-level stock quantity.

## Current API surface

The MVP API should remain:

```text
GET  /api/v1/health/
GET  /api/v1/health/live/
GET  /api/v1/health/ready/
GET  /api/v1/catalog/products/
GET  /api/v1/catalog/products/<slug>/
GET  /api/v1/catalog/categories/
POST /api/v1/inquiries/
GET  /api/v1/inquiries/
```

`GET /api/v1/inquiries/` must stay protected for vendor/admin users because it exposes buyer contact data.

## Route design rule

All routes must go through the versioned router:

```text
/api/v1/
```

Do not add unversioned aliases such as:

```text
/api/catalog/
/api/inquiries/
```

## Service layer rule

Keep services small and feature-specific.

Good:

```text
apps/catalog/services/catalog_service.py
```

Avoid:

```text
apps/catalog/services.py
apps/catalog/services/__init__.py with duplicated logic
```

`apps.catalog.services` should remain a stable import facade, not a second implementation.

## Response rule

Use raw DRF responses for product and inquiry APIs.

Good:

```python
return Response(serializer.data)
return Response({'detail': 'Not found.'}, status=404)
```

Avoid per-view response helpers unless there is a strong project-wide reason.

## Demo data rule

Demo data must be seeded explicitly:

```bash
python manage.py seed_demo
```

Do not seed products or users during normal API requests.

## Folder cleanup plan

This plan is documentation only. Runtime code should be changed in separate focused PRs.

### Phase 1: protect the current MVP shape

Keep the active backend centered on:

```text
accounts
catalog
inquiries
```

Keep active APIs limited to health, catalog browsing, and buyer inquiries.

### Phase 2: review dormant code

Review inactive backend code before deleting or enabling it. Dormant code should either become part of the ecommerce flow or be removed in a later cleanup PR.

Main review targets:

- inactive inventory code;
- unused serializers;
- unmounted account routes;
- old documentation that describes a bigger platform.

### Phase 3: add seller product management only when ready

Seller product management should be a separate ecommerce feature. Add it only when the frontend, permissions, serializers, and route design are ready together.

Potential future route shape:

```text
/api/v1/catalog/vendor/products/
/api/v1/catalog/vendor/products/<id>/
```

### Phase 4: choose quote flow or cart flow

For a small medical equipment website, a quote/inquiry flow may be enough for the MVP. A full cart should be added only if the selling flow needs direct checkout.

## MVP expansion order

If the website needs more ecommerce features, add them in this order:

1. Product catalog stability
2. Seller/admin product management
3. Quote request or inquiry improvement
4. Cart, only if needed
5. Orders
6. Payment integration

Do not add KPI, analytics, CMS, social, or event modules before the ecommerce flow is complete.

## Decision checklist before adding code

Before adding any backend app, model, route, service, task, or dependency, answer yes to this question:

Does it directly help customers find, view, inquire about, or buy medical equipment?

If not, keep it out of the MVP backend.
