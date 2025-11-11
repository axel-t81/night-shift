# API Layer Guide

Night Shift App exposes its business logic through a FastAPI-powered REST API. This guide captures the endpoints, behaviors, and implementation details you need for ongoing maintenance.

**Total endpoints:** 34 (categories, blocks, tasks, queue utilities, statistics)

## Quick Reference

```bash
uvicorn app.main:app --reload  # start locally
```

- API base: `http://localhost:8000/api`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health check: `http://localhost:8000/health`
- Frontend: `http://localhost:8000/app`

## Layering

```
HTTP request
    ↓
FastAPI router (app/api/routes)
    ↓
Services layer (app/services)
    ↓
Schemas & models (app/schemas, app/models)
    ↓
Database (SQLite locally, PostgreSQL in production)
```

Routers never talk to the ORM directly; they proxy everything through services to keep business rules in one place.

## Endpoint Catalogue

### Root endpoints

| Method | Path   | Purpose                          |
|--------|--------|----------------------------------|
| GET    | `/`    | Welcome payload with metadata    |
| GET    | `/app` | Serves the SPA (`templates/index.html`) |
| GET    | `/health` | Deployment/monitoring status probe |

### Category endpoints (7)

`/api/categories`

- List (with pagination + filters), retrieve, create, update, delete
- `/with-tasks` returns counts per category
- `/stats` surfaces completion percentage and time totals

### Block endpoints (14)

`/api/blocks`

- Full CRUD plus `/with-tasks` for hydrated payloads
- Recurrence helpers: `/complete-and-reset`, `/reset-tasks`, `/move-to-end`, `/clone`
- Queue utilities: `/next`, `/active`, `/reorder`, `/statistics`
- Filters include `day_number`, ordering supports `block_number` and `created_at`

### Task endpoints (13)

`/api/tasks`

- CRUD plus completion/uncompletion, progress, and task reordering
- Lookup routes by block or category
- Bulk operations: `/bulk-complete`, `/bulk-uncomplete`
- Supports pagination, completion status filtering, and position-based ordering

## Common Request Examples

```bash
# Create a category
curl -X POST http://localhost:8000/api/categories \
  -H "Content-Type: application/json" \
  -d '{"name": "Deep Work", "color": "#1E90FF"}'

# Create a block
curl -X POST http://localhost:8000/api/blocks \
  -H "Content-Type: application/json" \
  -d '{
        "title": "Night Study",
        "block_number": 1,
        "day_number": 3,
        "description": "Focus on algorithms"
      }'

# Complete a task
curl -X POST http://localhost:8000/api/tasks/{task_id}/complete \
  -H "Content-Type: application/json" \
  -d '{"actual_minutes": 50}'

# Complete and reset a block
curl -X POST "http://localhost:8000/api/blocks/{block_id}/complete-and-reset?move_to_end=true"
```

## Implementation Notes

### Validation & schemas

- Request bodies use `*Create` and `*Update` schemas.
- Responses return full schema objects; no raw ORM instances leak out.
- Query parameters document constraints (e.g., `day_number` is limited to 1–5).

### Error handling

- 404 for missing resources, 400 for business rule violations.
- FastAPI handles 422 validation responses automatically.
- Exceptions bubble up from the services layer with clear messages.

### Database sessions

- Every route depends on `get_db`.
- Services commit/rollback; routers stay transaction-free.
- Background tasks can reuse the same pattern if added later.

### Documentation

- Swagger UI is curated with docstrings, descriptions, and examples.
- Endpoint tags group categories, blocks, tasks, and root utilities.
- ReDoc provides a printer-friendly reference for stakeholders.

### Recurring workflow

`/complete-and-reset` is the heart of the recurring system:
1. Mark incomplete tasks complete (recording timestamps).
2. Immediately reset all tasks to incomplete.
3. Optionally move the block to the end of the queue.
4. Return counts for completed/reset tasks and the new queue position.

## Testing via Swagger UI

1. Start the app with `uvicorn app.main:app --reload`.
2. Visit `http://localhost:8000/docs`.
3. Expand any endpoint, click **Try it out**, provide parameters.
4. Execute and inspect the live response and curl command.

## CORS & static assets

```python
allow_origins = ["*"]  # dev only – tighten before production deploys
```

Static assets are served from `/static/*`; the SPA lives at `/app`. When deploying behind a CDN, consider moving static files to the CDN and pointing the frontend to the hosted API base.

## Persistence

- Tables are materialized on startup for local development (`Base.metadata.create_all`).
- Production deployments should run Alembic migrations instead.
- SQLite ships with the repo for convenience; Cloud SQL or another PostgreSQL instance is recommended for production.

## Maintenance Checklist

- Keep FastAPI docstrings in sync when adding or modifying routes.
- Re-run `pytest` (or your preferred suite) after expanding service logic.
- Restrict CORS and configure authentication when exposing the API publicly.
- Update the README and this guide alongside any breaking API change.

The API layer is stable, feature-complete, and ready for day-to-day operations.
