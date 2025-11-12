# Services Layer Guide

The services layer centralizes Night Shift App's business logic. Every FastAPI route depends on these modules to keep persistence rules, recurring workflows, and validation consistent.

## Layering Overview

```
FastAPI router → Services layer → SQLAlchemy models → Database
```

Services return plain Pydantic models or dictionaries ready for JSON serialization. Database sessions are injected from the API layer and passed through.

## Category Service (`category_service.py`)

Purpose: organize work by project/category, expose statistics, and safeguard deletes.

### Key operations

- `get_all_categories(db, skip, limit)` – paginated list of categories.
- `get_category(db, category_id)` – retrieve a single category.
- `create_category(db, category)` / `update_category(...)` – manage category metadata.
- `delete_category(db, category_id)` – cascading delete guard; raises if tasks still reference the category.
- `get_category_stats(db, category_id)` – completion rates and time totals.
- `get_categories_with_task_counts(db)` – used by the sidebar to show workload distribution.

### Usage pattern

```python
from app.services import category_service
from app.schemas.category import CategoryCreate

category = category_service.create_category(
    db,
    CategoryCreate(name="Deep Work", color="#1E90FF")
)

stats = category_service.get_category_stats(db, category.id)
```

## Task Service (`task_service.py`)

Purpose: manage the atomic unit of work inside a block, including completion state, ordering, and metrics.

### Key operations

- `get_all_tasks(db, skip, limit, completed, block_id, category_id)` – filterable list endpoint.
- `get_task(db, task_id)` – single task retrieval.
- `create_task`, `update_task`, `delete_task` – CRUD.
- `complete_task(db, task_id, actual_minutes)` / `uncomplete_task` – toggles completion, timestamps actuals.
- `reorder_tasks(db, task_positions)` – bulk position update for drag-and-drop UI.
- `get_block_progress(db, block_id)` – completion percentage, counts, estimated vs actual totals.
- `bulk_complete_tasks` / `bulk_uncomplete_tasks` – efficient operations for multi-select flows.

### Usage pattern

```python
from app.services import task_service
from app.schemas.task import TaskCreate

task = task_service.create_task(
    db,
    TaskCreate(
        block_id=block.id,
        category_id=category.id,
        title="Study FastAPI",
        estimated_minutes=45,
        position=0
    )
)

task_service.complete_task(db, task.id, actual_minutes=50)
progress = task_service.get_block_progress(db, block.id)
```

## Block Service (`block_service.py`)

Purpose: orchestrate recurring blocks, queue positioning, statistics, and aggregation of tasks.

### Core CRUD

- `get_all_blocks(db, skip, limit, day_number, order_by)` – browsing/filtering.
- `get_block(db, block_id)` and `get_block_with_tasks(db, block_id)` – detail views.
- `create_block`, `update_block`, `delete_block` – block lifecycle management.

### Recurring workflow

- `complete_and_reset_block(db, block_id, move_to_end)` – flagship recurrence helper:
  1. Marks any remaining tasks complete (recording timestamps).
  2. Resets all tasks to incomplete for the next cycle.
  3. Optionally pushes the block to the end of the queue.
  4. Returns counts and the new queue position.

- `reset_block_tasks(db, block_id)` – reset without completion logging.
- `move_block_to_end(db, block_id)` – manual queue adjustment.
- `clone_block(db, block_id, copy_tasks)` – create a template-derived copy.

### Queue & analytics

- `reorder_blocks(db, block_orders)` – bulk renumbering for drag-and-drop.
- `get_active_blocks(db, day_number)` – blocks with outstanding tasks.
- `get_next_block(db)` – next eligible block, used by the "Next Block" UI.
- `get_block_statistics(db)` – dashboard aggregates.

### Usage pattern

```python
from app.services import block_service

result = block_service.complete_and_reset_block(db, block.id, move_to_end=True)
# {
#   "tasks_completed": 5,
#   "tasks_reset": 5,
#   "new_block_number": 12,
#   "moved_to_end": True
# }
```

## Data Model Alignment

No additional tables were required to support recurrence:

- `Block.block_number` keeps queue order.
- Queue queries sort exclusively by `block_number`; `day_number` is decorative metadata for display.
- `Task.completed` and `Task.completed_at` capture state transitions.
- Cascade deletes clean up associated tasks when removing a block.

```
Category ─┐
          ├─< Block ─┐
          │          └─< Task
```

## Best Practices

- **Always go through services.** Skip direct ORM usage in routes or background jobs.
- **Handle `None` results.** Services return `None` for missing entities; raise a 404 at the API layer.
- **Guard transactions.** Services commit by default, but complex workflows should still wrap calls in try/except and rollback on failure.
- **Keep idempotency in mind.** Operations like `complete_and_reset_block` handle already-completed tasks gracefully.

## Testing

Leverage fixtures that provide a session scoped to a transaction. Example:

```python
def test_recurring_block(db_session):
    block = block_service.create_block(db_session, BlockCreate(
        title="Night Shift",
        block_number=1,
        day_number=1
    ))

    task = task_service.create_task(db_session, TaskCreate(
        block_id=block.id,
        category_id=category.id,
        title="Warm up",
        estimated_minutes=12
    ))

    task_service.complete_task(db_session, task.id)
    result = block_service.complete_and_reset_block(db_session, block.id)

    assert result["tasks_reset"] == 1
    assert result["moved_to_end"] is True
    assert task_service.get_task(db_session, task.id).completed is False
```

## Maintenance Checklist

- Add new business rules in services first, then expose them via routers.
- Update docstrings and schemas alongside any signature changes.
- Keep service functions small and composable—prefer helper methods when logic grows.
- When adding long-running workflows, consider background tasks but keep the domain rules here.

The services layer is the contract between your API and the database. Keep it clean, and the rest of the stack remains predictable.
