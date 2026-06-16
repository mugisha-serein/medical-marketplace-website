# 🏛️ Enterprise Django Backend - Architecture Reference

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React/TypeScript)              │
│                    (Stable API contracts guaranteed)             │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                    ┌──────────▼──────────┐
                    │   Nginx (Reverse    │
                    │    Proxy & LB)      │
                    └──────────┬──────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
   ┌─────────┐         ┌─────────────┐         ┌─────────┐
   │ Django  │         │   Django    │         │ Django  │
   │ App 1   │         │   App 2     │         │ App N   │
   │ (Port   │         │   (Port     │         │ (Port   │
   │  8000)  │         │    8001)    │         │  800N)  │
   └────┬────┘         └────┬────────┘         └────┬────┘
        │                   │                      │
        └───────────────────┼──────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
   ┌─────────┐         ┌─────────┐         ┌────────┐
   │PostgreSQL│         │ Redis   │         │  S3 /  │
   │ (Database)        │(Cache &  │         │ Storage│
   │           │        │ Session) │         │        │
   │  - Users  │        │  - Carts │         └────────┘
   │  - Orders │        │  - Locks │
   │  - Inventory       │  - Keys  │
   └───────────┘        └─────────┘
                        
   ┌──────────────────────────────────────┐
   │    Celery Workers (Background Jobs)  │
   │  - Async Email                       │
   │  - Inventory Reconciliation          │
   │  - KPI Calculations                  │
   │  - Notifications                     │
   └──────────────────────────────────────┘
```

---

## Layered Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                           │
│  (API Views, Serializers, Error Handling, Response Formatting) │
├─────────────────────────────────────────────────────────────────┤
│  ViewSet Views      |  DRF Serializers  |  API URLs             │
│  Thin Controllers   |  Data Validation  |  v1 Versioning       │
│  Permissions        |  DTOs             |  Documentation        │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                         │
│    (All State Mutations Happen Here - Services)                │
├─────────────────────────────────────────────────────────────────┤
│  CartService        |  OrderService     |  InventoryService    │
│  - Price Snapshots  |  - Atomic Checkout|  - Stock Deduction   │
│  - Guest Merge      |  - Reservation    |  - Distributed Locks │
│  - TTL Management   |  - State Machine  |  - Audit Log         │
│                     |                   |                      │
│  NotificationService|  KPIService       |  CustomServices      │
│  - Email Queue      |  - Metrics Agg    |                      │
│  - Idempotency      |  - Redis Counters |                      │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                    QUERY/SELECTOR LAYER                         │
│    (All Reads Optimized - Select/Prefetch/Cache)              │
├─────────────────────────────────────────────────────────────────┤
│  ProductSelector    |  StockSelector    |  OrderSelector       │
│  - Optimized Queries|  - Low Stock      |  - With User Data    │
│  - Search/Filter    |  - Movement Query |  - Audit Trail       │
│  - No N+1 Problems  |  - Efficient      |  - Prefetch Items    │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                 PERSISTENCE LAYER                              │
│         (Models, Migrations, Database Constraints)             │
├─────────────────────────────────────────────────────────────────┤
│  User Model         |  Order Model      |  StockRecord Model   │
│  Product Model      |  OrderItem Model  |  StockMovement Model │
│  Cart (Redis)       |  Payment Model    |  (Immutable Audit)   │
└──────────────────────────────────────────────────────────────────┘
```

---

## Data Flow - Checkout Example

```
FRONTEND REQUEST
       │
       ▼
┌──────────────────────┐
│  API Endpoint View   │  ← Thin, no business logic
│  /api/v1/orders/     │
└────────┬─────────────┘
         │ Deserialize
         ▼
┌──────────────────────────────────┐
│  DRF Serializer                  │
│  - Validate cart structure       │
│  - Validate address format       │
│  - Deserialize to Python objects │
└────────┬─────────────────────────┘
         │ Call Service
         ▼
┌──────────────────────────────────────────────────────┐
│  OrderService.create_order_from_cart()               │
│  @transaction.atomic                                 │
│  ┌─────────────────────────────────────────────────┐ │
│  │ 1. Validate cart data (no frontend trust)       │ │
│  │ 2. Calculate & snapshot prices                  │ │
│  │ 3. Create Order model (frozen snapshot)         │ │
│  │ 4. For each item:                               │ │
│  │    - InventoryService.reserve_stock()           │ │
│  │      (with distributed lock)                    │ │
│  │ 5. Clear cart via CartService                   │ │
│  │ 6. Log action                                   │ │
│  │ 7. Trigger async notification                   │ │
│  └─────────────────────────────────────────────────┘ │
└────────┬──────────────────────────────────────────────┘
         │
         ├─────────────────────────────────────────────┐
         │                                             │
         ▼                                             ▼
    ┌─────────────┐                          ┌──────────────────┐
    │ PostgreSQL  │                          │ Celery Task Queue│
    │ Transaction │                          │ send_email.task()│
    │ - Create    │                          │ (async)          │
    │   Order     │                          └──────────────────┘
    │ - Reserve   │                                    │
    │   Stock     │                                    ▼
    │ - Commit    │                          ┌──────────────────┐
    └─────────────┘                          │ Celery Worker    │
                                             │ - Render email   │
    ┌─────────────┐                          │ - Send via SMTP  │
    │ Redis Cache │                          │ - Log delivery   │
    │ - Clear     │                          │ - Update EmailLog│
    │   Cart      │                          └──────────────────┘
    └─────────────┘

         │
         ▼
    ┌──────────────────────┐
    │ Serialized Response  │
    │ {                    │
    │  "success": true,    │
    │  "data": {order},    │
    │  "message": "..."    │
    │ }                    │
    └──────────────────────┘
         │
         ▼
      FRONTEND RECEIVES STABLE API CONTRACT
```

---

## Concurrency Control - Stock Deduction

```
REQUEST 1: Deduct 5 units        REQUEST 2: Deduct 3 units
from product stock (100 available) from product stock (100 available)
         │                                    │
         ▼                                    ▼
┌──────────────────────────────┐ ┌──────────────────────────────┐
│ InventoryService.deduct()   │ │ InventoryService.deduct()   │
├──────────────────────────────┼─┼──────────────────────────────┤
│ 1. Try to acquire lock:      │ │ 1. Try to acquire lock:      │
│    with DistributedLock():   │ │    with DistributedLock():   │
│    ✓ ACQUIRED                │ │    ⏳ WAITING (retry)         │
│                              │ │                              │
│ 2. select_for_update() on    │ │ 2. [waiting...]              │
│    StockRecord in transaction│ │                              │
│                              │ │                              │
│ 3. Verify available: 100 ✓   │ │                              │
│                              │ │                              │
│ 4. Deduct: 100 - 5 = 95     │ │                              │
│                              │ │                              │
│ 5. Save StockRecord         │ │                              │
│                              │ │                              │
│ 6. Create immutable          │ │                              │
│    StockMovement record      │ │                              │
│    type=SALE, delta=-5       │ │                              │
│                              │ │                              │
│ 7. Release lock              │ │                              │
│    ✓ RELEASED               │ │                              │
└──────────────────────────────┘ │                              │
                                 │ 1. Try to acquire lock:      │
                                 │    with DistributedLock():   │
                                 │    ✓ NOW ACQUIRED            │
                                 │                              │
                                 │ 2. select_for_update() on    │
                                 │    StockRecord (now 95)       │
                                 │                              │
                                 │ 3. Verify available: 95 ✓    │
                                 │                              │
                                 │ 4. Deduct: 95 - 3 = 92      │
                                 │                              │
                                 │ 5. Save StockRecord         │
                                 │                              │
                                 │ 6. Create immutable          │
                                 │    StockMovement record      │
                                 │    type=SALE, delta=-3       │
                                 │                              │
                                 │ 7. Release lock              │
                                 │    ✓ RELEASED               │
                                 └──────────────────────────────┘

FINAL STATE:
- StockRecord.quantity = 92 ✓
- StockMovement [SALE, -5], [SALE, -3] ← Immutable audit trail
- No race conditions
- Oversell prevented
```

---

## Request Lifecycle with Correlation IDs

```
CLIENT REQUEST
  │
  │ POST /api/v1/orders/
  │ (with or without X-Request-ID header)
  │
  ▼
┌─────────────────────────────────┐
│ Django Request Object           │
│ middleware.CorrelationIDMiddleware
│                                 │
│ if no X-Request-ID:             │
│   ✓ Generate UUID: abc-123      │
│ else:                           │
│   ✓ Use provided: xyz-789       │
│                                 │
│ request.request_id = 'abc-123'  │
│ request.META[...] = 'abc-123'   │
└────────────┬────────────────────┘
             │
             ▼
    ┌────────────────────────────┐
    │ View Processing            │
    │ (all logging includes id)  │
    │                            │
    │ logger.info("Creating...") │
    │ {"request_id": "abc-123"} │
    └────────────┬───────────────┘
                 │
                 ▼
        ┌────────────────────────────┐
        │ Service Layer              │
        │ (all logging includes id)  │
        │                            │
        │ BaseService.log_action()   │
        │ {"request_id": "abc-123"} │
        └────────────┬───────────────┘
                     │
                     ▼
            ┌────────────────────────────┐
            │ Database Transaction       │
            │ (all logs include id)      │
            │                            │
            │ Create Order, Reserve Stock│
            │ {"request_id": "abc-123"} │
            └────────────┬───────────────┘
                         │
                         ▼
    ┌──────────────────────────────────────┐
    │ Response Headers                     │
    │ X-Request-ID: abc-123                │
    │                                      │
    │ Response Body                        │
    │ {                                    │
    │   "success": true,                   │
    │   "data": {...},                     │
    │   "request_id": "abc-123" (optional) │
    │ }                                    │
    └──────────────────────────────────────┘
             │
             ▼
    LOGS IN ELASTICSEARCH/DATADOG
    Can trace entire request:
    abc-123 → middleware → view → service → db → response
```

---

## App Module Structure

```
apps/orders/  ← Example app showing complete architecture
│
├── api/                  ← API Layer
│   ├── views/
│   │   ├── __init__.py
│   │   └── order_views.py      # Thin controllers
│   ├── serializers/
│   │   ├── __init__.py
│   │   └── order_serializers.py # Data validation
│   └── urls/
│       ├── __init__.py
│       └── order_urls.py        # v1 versioned routes
│
├── services/             ← Business Logic
│   ├── __init__.py
│   └── order_service.py  # All state mutations here
│
├── selectors/            ← Read Optimization
│   ├── __init__.py
│   └── order_selectors.py # Optimized queries
│
├── permissions/          ← Access Control
│   ├── __init__.py
│   └── order_permissions.py
│
├── tasks/                ← Async Celery Jobs
│   ├── __init__.py
│   └── order_tasks.py
│
├── constants/            ← App Constants
│   ├── __init__.py
│   └── order_constants.py
│
├── exceptions/           ← App-Specific Exceptions
│   └── __init__.py
│
├── tests/                ← Test Suite
│   ├── __init__.py
│   ├── test_services.py
│   ├── test_views.py
│   └── test_permissions.py
│
├── models.py             ← ORM Models
├── admin.py              ← Django Admin Config
├── apps.py               ← App Config
└── migrations/           ← Database Migrations
```

---

## Service Invocation Pattern

```
PROBLEM:
- Business logic scattered across views, models, serializers
- Hard to test
- Hard to reuse
- Hard to understand
- Easy to create bugs

SOLUTION: Service Layer Pattern

VIEW (Thin Controller)
    │
    ├─ Deserialize input
    ├─ Check permissions
    │
    ▼
SERVICE (All Business Logic)
    │
    ├─ Validate business rules
    ├─ Coordinate across models
    ├─ Manage transactions
    ├─ Call other services
    ├─ Handle locking/concurrency
    ├─ Logging & audit trail
    │
    ▼
REPOSITORY/SELECTOR (Optimized Reads)
    │
    ├─ Query optimization
    ├─ Caching strategy
    ├─ No mutations here
    │
    ▼
DATABASE

BENEFITS:
✓ Single responsibility
✓ Easy to test (mock services)
✓ Easy to reuse (service → service calls)
✓ Easy to maintain (business logic in one place)
✓ Easy to understand (clear flow)
✓ Transaction safety (@transaction.atomic)
✓ Audit trail (structured logging)
```

---

## Idempotency Pattern (Payment Example)

```
CLIENT: POST /api/v1/orders/pay/
Headers: Idempotency-Key: abc-123-def-456

REQUEST 1 (First time)
    │
    ▼
SERVICE checks: Is (user_id, operation, params_hash) cached?
    │
    ├─ NO → Execute payment
    │       ├─ Charge card
    │       ├─ Create transaction
    │       ├─ Cache result: abc-123 → {success, txn_id}
    │       └─ Return {success, txn_id}
    │
    ▼
RESPONSE 1: HTTP 200 {success: true, transaction_id: "txn-789"}

---

CLIENT: TIMEOUT or Network Error
    │
    ▼
CLIENT RETRIES: POST /api/v1/orders/pay/
(with same Idempotency-Key: abc-123-def-456)

REQUEST 2 (Retry)
    │
    ▼
SERVICE checks: Is (user_id, operation, params_hash) cached?
    │
    ├─ YES → Return cached result WITHOUT re-executing
    │        (no duplicate charge!)
    │
    ▼
RESPONSE 2: HTTP 200 {success: true, transaction_id: "txn-789"}
                     (SAME response as REQUEST 1)

---

BENEFIT:
✓ Network retries don't cause duplicate charges
✓ Safe to implement client-side retry logic
✓ Client feels responsive (idempotent APIs)
✓ Backend safe from duplicate operations
```

---

## Distributed Lock Pattern (Stock Race Condition)

```
SCENARIO: Stock level is 10 units
          Two customers try to buy 8 units each simultaneously

WITHOUT LOCK (RACE CONDITION):
T1: Thread 1 reads stock = 10
T2: Thread 2 reads stock = 10
T3: Thread 1 decrements: 10 - 8 = 2, saves
T4: Thread 2 decrements: 10 - 8 = 2, saves  ← WRONG! Oversold by 6 units!
Result: Only 2 units shown but 16 sold

WITH LOCK (SERIALIZED):
T1: Thread 1 tries to acquire lock → ACQUIRED ✓
T2: Thread 2 tries to acquire lock → WAITING (retry loop)
T3: Thread 1 reads stock = 10 (row locked)
T4: Thread 1 decrements: 10 - 8 = 2, saves
T5: Thread 1 releases lock
T6: Thread 2 acquires lock ✓
T7: Thread 2 reads stock = 2 (row locked)
T8: Thread 2 tries to decrease: 2 - 8 = -6 → ERROR! ✓
T9: Thread 2 raises InventoryError("Insufficient stock")

Result: First order succeeds, second order rejected. Correct!
```

---

## Performance Considerations

```
OPTIMIZATIONS IMPLEMENTED:

✓ Database
  - select_related() in selectors (JOINs)
  - prefetch_related() for M2M/FK relationships
  - Indexes on frequently filtered columns
  - Database connection pooling
  - Row-level locking to minimize contention

✓ Caching
  - Redis for ephemeral data (carts, locks)
  - Session caching via Redis
  - Cache manager with TTL
  - Cache-aside pattern

✓ Async Processing
  - Celery for non-blocking operations
  - Email delivery asynchronous
  - Notifications non-blocking
  - Background reconciliation tasks

✓ Query Optimization
  - Cursor-based pagination (not offset)
  - Limit results by default
  - Aggregation at database layer
  - Query result caching

MONITORING:
- Request/response times logged
- Database query latency tracked
- Cache hit/miss rates collected
- Async task durations recorded
```

---

## Integration Points

```
EXTERNAL SYSTEMS:

1. SMTP Server (Email)
   - Task queue → Celery worker → SMTP
   - Idempotent delivery (EmailLog)
   - Retry-safe

2. S3 / Object Storage (Files)
   - Profile pictures
   - Product images
   - Invoice PDFs

3. Payment Gateway
   - Via service layer
   - Idempotent operations
   - Transaction logging

4. Monitoring (Optional)
   - Prometheus metrics export
   - Sentry error tracking
   - Datadog APM
   - CloudWatch logs

5. Analytics (Optional)
   - Event streaming
   - KPI dashboard
   - Redis counters
```

---

**This architecture enables:**
- ✅ Horizontal scaling
- ✅ Service isolation
- ✅ Concurrent operations without race conditions
- ✅ Audit trail for compliance
- ✅ Easy testing and debugging
- ✅ Clear responsibility separation
- ✅ Production-ready monitoring
- ✅ Frontend compatibility guarantee

