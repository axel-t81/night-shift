"""
Schemas Package

This package contains all Pydantic schemas for data validation and serialization.

Schemas serve as the data transfer objects (DTOs) between the API and clients.
They define:
- What data can be sent TO the API (Create/Update schemas)
- What data is returned FROM the API (Response schemas)
- Validation rules for all fields

Importing schemas:
    from app.schemas import Category, CategoryCreate, CategoryUpdate
    from app.schemas import Block, BlockCreate, BlockUpdate
    from app.schemas import Task, TaskCreate, TaskUpdate

Usage in FastAPI routes:
    @router.post("/categories", response_model=Category)
    def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
        # category is validated against CategoryCreate schema
        # response is validated against Category schema
        ...
"""

# Import all schemas for easy access
from app.schemas.category import (
    Category,
    CategoryBase,
    CategoryCreate,
    CategoryUpdate
)

from app.schemas.block import (
    Block,
    BlockBase,
    BlockCreate,
    BlockUpdate
)

from app.schemas.task import (
    Task,
    TaskBase,
    TaskCreate,
    TaskUpdate
)

# Define what's available when doing: from app.schemas import *
__all__ = [
    # Category schemas
    "Category",
    "CategoryBase",
    "CategoryCreate",
    "CategoryUpdate",
    # Block schemas
    "Block",
    "BlockBase",
    "BlockCreate",
    "BlockUpdate",
    # Task schemas
    "Task",
    "TaskBase",
    "TaskCreate",
    "TaskUpdate",
]

