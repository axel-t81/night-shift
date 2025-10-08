# Services Layer Guide

## Overview

The Services Layer implements all business logic for the Night Shift MVP app. It sits between the API routes and the database models, providing a clean separation of concerns.

## Architecture

```
API Routes (FastAPI)
       ↓
Services Layer (Business Logic)
       ↓
Models (SQLAlchemy ORM)
       ↓
Database (SQLite/PostgreSQL)
```

## Services

### 1. Category Service (`category_service.py`)

Manages categories/projects for organizing tasks.

#### Key Functions

- **`get_all_categories(db, skip, limit)`** - List all categories with pagination
- **`get_category(db, category_id)`** - Get single category by ID
- **`create_category(db, category)`** - Create new category
- **`update_category(db, category_id, category_update)`** - Update category
- **`delete_category(db, category_id)`** - Delete category (fails if tasks exist)
- **`get_category_stats(db, category_id)`** - Get task completion statistics
- **`get_categories_with_task_counts(db)`** - List categories with task counts

#### Example Usage

```python
from app.services import category_service
from app.schemas.category import CategoryCreate

# Create a category
category_data = CategoryCreate(name="Deep Work", color="#1E90FF")
category = category_service.create_category(db, category_data)

# Get statistics
stats = category_service.get_category_stats(db, category.id)
print(f"Completion rate: {stats['completion_rate']}%")
```

---

### 2. Task Service (`task_service.py`)

Manages individual tasks within blocks.

#### Key Functions

- **`get_all_tasks(db, skip, limit, completed, block_id, category_id)`** - List tasks with filtering
- **`get_task(db, task_id)`** - Get single task by ID
- **`get_tasks_by_block(db, block_id)`** - Get all tasks in a block (ordered by position)
- **`get_tasks_by_category(db, category_id)`** - Get all tasks in a category
- **`create_task(db, task)`** - Create new task
- **`update_task(db, task_id, task_update)`** - Update task
- **`delete_task(db, task_id)`** - Delete task
- **`complete_task(db, task_id, actual_minutes)`** - Mark task complete
- **`uncomplete_task(db, task_id)`** - Mark task incomplete
- **`reorder_tasks(db, task_positions)`** - Update positions for drag-and-drop
- **`get_block_progress(db, block_id)`** - Get completion progress for a block
- **`bulk_complete_tasks(db, task_ids)`** - Complete multiple tasks
- **`bulk_uncomplete_tasks(db, task_ids)`** - Uncomplete multiple tasks

#### Example Usage

```python
from app.services import task_service
from app.schemas.task import TaskCreate

# Create a task
task_data = TaskCreate(
    block_id="block-uuid",
    category_id="category-uuid",
    title="Study FastAPI",
    estimated_minutes=45,
    position=0
)
task = task_service.create_task(db, task_data)

# Complete the task
completed_task = task_service.complete_task(db, task.id, actual_minutes=50)

# Get block progress
progress = task_service.get_block_progress(db, "block-uuid")
print(f"Block is {progress['completion_percentage']}% complete")
```

---

### 3. Block Service (`block_service.py`)

Manages time blocks (Pomodoro sessions) with **special recurring block support**.

#### Key Functions

##### Basic CRUD
- **`get_all_blocks(db, skip, limit, day_number, order_by)`** - List blocks with filtering
- **`get_block(db, block_id)`** - Get single block by ID
- **`get_block_with_tasks(db, block_id)`** - Get block with all its tasks
- **`create_block(db, block)`** - Create new block
- **`update_block(db, block_id, block_update)`** - Update block
- **`delete_block(db, block_id)`** - Delete block and its tasks

##### Recurring Block Functions 🔄
- **`reset_block_tasks(db, block_id)`** - Reset all tasks in a block to incomplete
- **`move_block_to_end(db, block_id)`** - Move block to end of queue
- **`complete_and_reset_block(db, block_id, move_to_end)`** - **KEY FUNCTION** for recurring blocks
- **`clone_block(db, block_id, new_start_time, new_end_time, copy_tasks)`** - Create copy of block

##### Queue Management
- **`reorder_blocks(db, block_orders)`** - Update block ordering
- **`get_active_blocks(db, day_number)`** - Get blocks with incomplete tasks
- **`get_next_block(db)`** - Get next block in queue
- **`get_block_statistics(db)`** - Get overall block statistics

---

## Recurring Blocks - How It Works

### The Problem

You want blocks to be recurring (not tasks). A block should contain a fixed set of tasks, and when the block is completed, it should reset and move to the back of the queue.

### The Solution

The `complete_and_reset_block()` function implements this workflow:

```python
def complete_and_reset_block(db, block_id, move_to_end=True):
    """
    1. Mark all incomplete tasks as complete (records completion)
    2. Immediately reset all tasks to incomplete (ready for next cycle)
    3. Move block to end of queue (via block_number)
    """
```

### Example Workflow

```python
from app.services import block_service

# You have a block "Morning Routine" with tasks:
# - Task 1: Meditation (20 min)
# - Task 2: Exercise (30 min)
# - Task 3: Breakfast (15 min)

# User completes all tasks in the block
result = block_service.complete_and_reset_block(db, block_id, move_to_end=True)

# Result:
# {
#   "tasks_completed": 3,      # 3 tasks were marked complete
#   "tasks_reset": 3,           # 3 tasks reset to incomplete
#   "new_block_number": 10,     # Block moved to end (was #1, now #10)
#   "moved_to_end": True
# }

# Now the block is ready to be done again!
# It's at the back of the queue, so other blocks come first.
```

### Block Ordering

Blocks are ordered by `block_number`:
- Lower numbers = earlier in queue
- Higher numbers = later in queue
- When a block is completed, it gets the highest number + 1

Example queue:
```
Block #1: Morning Routine (you're here)
Block #2: Deep Work Session
Block #3: Learning Block
Block #4: Exercise Block

[Complete Morning Routine]

Block #2: Deep Work Session (you're here now)
Block #3: Learning Block
Block #4: Exercise Block
Block #5: Morning Routine (moved to end)
```

---

## Cloning Blocks for True Recurrence

If you want to create multiple instances of the same block (e.g., "Morning Routine" every day), use `clone_block()`:

```python
from datetime import datetime, timedelta

# Clone a block for tomorrow
source_block_id = "morning-routine-template-id"
new_start = datetime.now() + timedelta(days=1)

new_block = block_service.clone_block(
    db,
    source_block_id,
    new_start_time=new_start,
    copy_tasks=True  # Copy all tasks from source block
)

# Now you have two separate blocks:
# 1. Original "Morning Routine" block
# 2. New "Morning Routine (Copy)" block for tomorrow
```

---

## Data Model Compatibility

### No Model Changes Needed! ✅

The existing data model supports recurring blocks without any changes:

- **`Block.block_number`** - Used for queue ordering
- **`Task.completed`** - Can be toggled between complete/incomplete
- **`Task.completed_at`** - Records when task was completed
- **Cascade delete** - When you delete a block, its tasks are deleted too

### Current Schema

```
Category
├── id (UUID)
├── name
└── color

Block
├── id (UUID)
├── start_time
├── end_time
├── title
├── block_number (for ordering)
└── day_number (optional)

Task
├── id (UUID)
├── block_id (FK)
├── category_id (FK)
├── title
├── estimated_minutes
├── actual_minutes
├── completed (boolean)
├── completed_at (timestamp)
└── position (for ordering within block)
```

---

## Integration with API Layer

When you build the API routes, use the services like this:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import block_service
from app.schemas.block import Block

router = APIRouter()

@router.post("/blocks/{block_id}/complete-and-reset")
def complete_and_reset_block(
    block_id: str,
    move_to_end: bool = True,
    db: Session = Depends(get_db)
):
    """Complete all tasks in a block and reset for recurrence"""
    result = block_service.complete_and_reset_block(db, block_id, move_to_end)
    
    if not result:
        raise HTTPException(status_code=404, detail="Block not found")
    
    return result

@router.get("/blocks/next")
def get_next_block(db: Session = Depends(get_db)):
    """Get the next block in the queue"""
    result = block_service.get_next_block(db)
    
    if not result:
        return {"message": "No blocks available"}
    
    return result
```

---

## Best Practices

### 1. Always Use Services, Not Direct DB Access

❌ **Bad:**
```python
@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()  # Direct DB access
```

✅ **Good:**
```python
@router.get("/categories")
def get_categories(db: Session = Depends(get_db)):
    return category_service.get_all_categories(db)  # Use service
```

### 2. Handle None Returns

Services return `None` when entities aren't found:

```python
category = category_service.get_category(db, category_id)
if not category:
    raise HTTPException(status_code=404, detail="Category not found")
```

### 3. Use Transactions

Services handle commits internally, but for complex operations:

```python
try:
    # Multiple service calls
    task1 = task_service.create_task(db, task_data1)
    task2 = task_service.create_task(db, task_data2)
    # If one fails, both rollback
except Exception as e:
    db.rollback()
    raise e
```

---

## Testing Services

```python
import pytest
from app.services import block_service, task_service
from app.schemas.block import BlockCreate
from app.schemas.task import TaskCreate
from datetime import datetime, timedelta

def test_recurring_block(db_session):
    # Create a block
    block_data = BlockCreate(
        start_time=datetime.now(),
        end_time=datetime.now() + timedelta(hours=2),
        title="Test Block",
        block_number=1
    )
    block = block_service.create_block(db_session, block_data)
    
    # Add tasks
    task1 = task_service.create_task(db_session, TaskCreate(
        block_id=block.id,
        category_id="some-category-id",
        title="Task 1",
        estimated_minutes=30
    ))
    
    # Complete task
    task_service.complete_task(db_session, task1.id)
    
    # Reset block
    result = block_service.complete_and_reset_block(db_session, block.id)
    
    assert result["tasks_completed"] == 0  # Already complete
    assert result["tasks_reset"] == 1
    assert result["moved_to_end"] == True
    
    # Verify task is now incomplete
    refreshed_task = task_service.get_task(db_session, task1.id)
    assert refreshed_task.completed == False
```

---

## Summary

The Services Layer provides:

✅ **Complete CRUD operations** for all entities  
✅ **Recurring block support** without model changes  
✅ **Queue management** with block ordering  
✅ **Progress tracking** and statistics  
✅ **Bulk operations** for efficiency  
✅ **Clean separation** from API and database layers  

The **recurring block functionality** is the key feature - blocks can repeat indefinitely by completing and resetting their tasks, then moving to the back of the queue.

---

## Next Steps

1. **Implement API Layer** - Create FastAPI routes that use these services
2. **Add Authentication** - If needed for multi-user support
3. **Build Frontend** - Create UI that calls the API endpoints
4. **Add Tests** - Write comprehensive tests for all services
5. **Deploy** - Set up Cloud Run with PostgreSQL

The services are ready to use! 🚀
