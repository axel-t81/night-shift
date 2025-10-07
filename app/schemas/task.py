"""
Task Pydantic Schemas

These schemas define the data validation and serialization for Task objects.
Tasks are the individual work items within time blocks.

Schema Types:
- TaskBase: Common fields shared across all schemas
- TaskCreate: Fields required when creating a new task (POST)
- TaskUpdate: Fields that can be updated (PUT/PATCH) - all optional
- Task: Complete task as returned from the API (GET) - includes id and timestamps
"""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


# Base schema with common fields
class TaskBase(BaseModel):
    """
    Base schema for tasks.
    
    A task represents a single work item within a time block.
    
    Fields:
    - block_id: UUID of the time block this task belongs to
    - category_id: UUID of the category/project for this task
    - title: Task title/name
    - description: Optional detailed description
    - estimated_minutes: How long you estimate this task will take
    - position: Order of task within its block (for drag-and-drop reordering)
    """
    block_id: str = Field(..., description="ID of the parent time block")
    category_id: str = Field(..., description="ID of the category/project")
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=250, description="Task description")
    estimated_minutes: int = Field(..., gt=0, description="Estimated time in minutes (must be positive)")
    position: int = Field(default=0, ge=0, description="Position within block for ordering")
    
    @field_validator('estimated_minutes')
    @classmethod
    def validate_estimated_minutes(cls, v: int) -> int:
        """
        Validate that estimated minutes is reasonable (positive and not excessively large).
        Maximum of 1 week (10080 minutes) to catch unrealistic estimates.
        """
        if v <= 0:
            raise ValueError('estimated_minutes must be positive')
        if v > 10080:  # 1 week in minutes
            raise ValueError('estimated_minutes cannot exceed 10080 (1 week)')
        return v


# Schema for creating a new task (POST request)
class TaskCreate(TaskBase):
    """
    Schema for creating a new task.
    Inherits all fields from TaskBase.
    
    No id, timestamps, or completion fields needed - these are auto-generated or default to False.
    
    Example:
    {
        "block_id": "123e4567-e89b-12d3-a456-426614174000",
        "category_id": "987f6543-e21b-12d3-a456-426614174999",
        "title": "Study FastAPI documentation",
        "description": "Read chapters 3-5",
        "estimated_minutes": 45,
        "position": 0
    }
    """
    pass


# Schema for updating an existing task (PUT/PATCH request)
class TaskUpdate(BaseModel):
    """
    Schema for updating a task.
    All fields are optional - only provide fields you want to update.
    
    Fields:
    - completed: Mark task as done/undone
    - actual_minutes: Record how long the task actually took
    - All other fields from TaskBase
    
    Example (marking task as complete):
    {
        "completed": true,
        "actual_minutes": 50
    }
    
    Example (reordering task):
    {
        "position": 2
    }
    """
    block_id: Optional[str] = None
    category_id: Optional[str] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=250)
    estimated_minutes: Optional[int] = Field(None, gt=0)
    actual_minutes: Optional[int] = Field(None, ge=0, le=10080, description="Actual time spent (0-10080 minutes)")
    completed: Optional[bool] = None
    position: Optional[int] = Field(None, ge=0)
    
    @field_validator('estimated_minutes')
    @classmethod
    def validate_estimated_minutes(cls, v: Optional[int]) -> Optional[int]:
        """Validate estimated minutes if provided"""
        if v is None:
            return v
        if v <= 0:
            raise ValueError('estimated_minutes must be positive')
        if v > 10080:
            raise ValueError('estimated_minutes cannot exceed 10080 (1 week)')
        return v
    
    @field_validator('actual_minutes')
    @classmethod
    def validate_actual_minutes(cls, v: Optional[int]) -> Optional[int]:
        """
        Validate actual minutes if provided.
        Must be non-negative and reasonable (max 1 week).
        """
        if v is None:
            return v
        if v < 0:
            raise ValueError('actual_minutes cannot be negative')
        if v > 10080:
            raise ValueError('actual_minutes cannot exceed 10080 (1 week)')
        return v


# Schema for task as stored in database and returned by API (GET response)
class Task(TaskBase):
    """
    Complete task schema as returned by the API.
    Includes all fields from TaskBase plus database-generated and completion tracking fields.
    
    Additional fields:
    - id: UUID string identifier
    - actual_minutes: How long the task actually took (None if not recorded)
    - completed: Whether the task is marked as complete
    - completed_at: When the task was completed (None if not completed)
    - created_at: When the task was created
    
    Example response:
    {
        "id": "456e7890-e12b-34c5-a678-901234567890",
        "block_id": "123e4567-e89b-12d3-a456-426614174000",
        "category_id": "987f6543-e21b-12d3-a456-426614174999",
        "title": "Study FastAPI documentation",
        "description": "Read chapters 3-5",
        "estimated_minutes": 45,
        "actual_minutes": 50,
        "completed": true,
        "position": 0,
        "completed_at": "2024-01-15T23:45:00",
        "created_at": "2024-01-15T22:00:00"
    }
    """
    id: str
    actual_minutes: Optional[int]
    completed: bool
    completed_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        """
        Pydantic configuration:
        - from_attributes: Allows creation from SQLAlchemy models (ORM mode)
        This enables: Task.model_validate(db_task_object)
        """
        from_attributes = True

