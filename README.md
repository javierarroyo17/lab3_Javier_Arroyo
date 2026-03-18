# Billing API (Django + DRF + PostgreSQL + Docker)

This project implements the **Provider / Barrel / Invoice / InvoiceLine** model with authenticated, provider-scoped endpoints.

## Stack
- Django + Django REST Framework
- PostgreSQL
- drf-spectacular (OpenAPI + Swagger UI)
- django-filter (enabled globally)

## Endpoints
Base: `http://localhost:8000/api/`

- `POST /api/token/` (JWT access + refresh token)
- `POST /api/token/refresh/`
- `/api/invoices/`
- `/api/providers/`
- `/api/barrels/`

All API endpoints require JWT authentication.
For non-superusers, data is constrained to the `provider` linked to the logged-in user.

Docs:
- Swagger UI: `GET /api/schema/swagger-ui/`
- OpenAPI JSON: `GET /api/schema/`

## Quick start (Docker)
1) Create `.env` (you can copy from `.env.example`):

```bash
cp .env.example .env
```

2) Build & run:

```bash
docker-compose build
docker-compose up
```

3) Apply migrations and (optionally) load sample data:

```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py seed_demo
```

4) Create superuser to access to admin
```bash
docker-compose exec web sh -c "python manage.py createsuperuser"
```

5) Obtain JWT token:
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"demo\",\"password\":\"demo1234\"}"
```

## Notes about domain behavior
- `Provider.has_barrels_to_bill()` returns `True` if any related barrel is not billed.
- `Invoice.add_line_for_barrel(...)` enforces:
  - liters > 0
  - unit_price_per_liter > 0
  - only allows billing when `liters == barrel.liters`
  - marks the barrel as billed when the line is added

## CI/CD
- Workflow: `.github/workflows/ci.yml`
- Trigger: `push` + `pull_request`
- Job: `test-and-coverage`
- Checks:
  - `python manage.py test`
  - coverage with minimum `80%` using `.coveragerc`

### Branch protection for safe PR merge
In GitHub repository settings, set branch protection for your main branch and require:
- status check `CI / test-and-coverage`
- pull request before merge
- up-to-date branch before merge
