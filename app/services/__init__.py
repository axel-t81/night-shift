"""
Services Layer

This package contains the business logic for the Night Shift app.
Services act as an intermediary between the API routes and the database models.

Modules:
- category_service: CRUD operations and statistics for categories
- task_service: Task management, completion tracking, and bulk operations
- block_service: Block management with recurring block support

Usage:
```python
from app.services import category_service, task_service, block_service
from app.database import get_db

# Example: Get all categories
db = next(get_db())
categories = category_service.get_all_categories(db)
```

Key Features:
- **Recurring Blocks**: Blocks can be completed and reset to repeat indefinitely
- **Task Management**: Full CRUD with position tracking and bulk operations
- **Progress Tracking**: Get completion statistics for blocks and categories
- **Queue Management**: Reorder blocks and move them to the end of the queue
"""

from app.services import category_service
from app.services import task_service
from app.services import block_service

__all__ = [
    'category_service',
    'task_service',
    'block_service'
]
