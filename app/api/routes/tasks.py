"""
Task API Routes

This module contains all API endpoints for managing tasks.
Tasks are individual work items within time blocks, organized by categories.

Endpoints:
=== Standard CRUD ===
- GET    /api/tasks                    - List tasks with filters
- GET    /api/tasks/{id}               - Get single task
- POST   /api/tasks                    - Create new task
- PUT    /api/tasks/{id}               - Update task
- DELETE /api/tasks/{id}               - Delete task

=== Task Operations ===
- POST   /api/tasks/{id}/complete      - Mark task complete
- POST   /api/tasks/{id}/uncomplete    - Mark task incomplete
- POST   /api/tasks/reorder            - Reorder tasks within block

=== Filtered Queries ===
- GET    /api/tasks/block/{block_id}             - Get all tasks in a block
- GET    /api/tasks/category/{category_id}       - Get all tasks in a category
- GET    /api/tasks/block/{block_id}/progress    - Get block progress

=== Bulk Operations ===
- POST   /api/tasks/bulk-complete      - Complete multiple tasks
- POST   /api/tasks/bulk-uncomplete    - Uncomplete multiple tasks
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional

# Import database dependency
from app.database import get_db

# Import schemas for request/response validation
from app.schemas.task import Task, TaskCreate, TaskUpdate

# Import service layer for business logic
from app.services import task_service


# Create router for task endpoints
router = APIRouter()


# ============================================================================
# STANDARD CRUD OPERATIONS
# ============================================================================

@router.get("", response_model=List[Task])
def list_tasks(
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    completed: Optional[bool] = Query(None, description="Filter by completion status"),
    block_id: Optional[str] = Query(None, description="Filter by block ID"),
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    db: Session = Depends(get_db)
):
    """
    List all tasks with optional filtering and pagination.
    
    Query Parameters:
    - skip: Number of records to skip (for pagination)
    - limit: Maximum number of records to return (1-1000)
    - completed: Filter by completion status (true/false/null for all)
    - block_id: Filter by specific block
    - category_id: Filter by specific category
    
    Returns:
    - List of Task objects ordered by block and position
    
    Example Response:
    ```json
    [
        {
            "id": "uuid-123",
            "block_id": "block-uuid",
            "category_id": "category-uuid",
            "title": "Study FastAPI",
            "description": "Read chapters 3-5",
            "estimated_minutes": 45,
            "actual_minutes": 50,
            "completed": true,
            "position": 0,
            "completed_at": "2024-01-15T23:45:00",
            "created_at": "2024-01-15T22:00:00"
        }
    ]
    ```
    """
    # Call service layer to get tasks with filters
    tasks = task_service.get_all_tasks(
        db,
        skip=skip,
        limit=limit,
        completed=completed,
        block_id=block_id,
        category_id=category_id
    )
    return tasks


@router.get("/{task_id}", response_model=Task)
def get_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a single task by ID.
    
    Path Parameters:
    - task_id: UUID string of the task
    
    Returns:
    - Task object with all fields
    
    Raises:
    - 404: Task not found
    """
    # Call service layer to get the task
    task = task_service.get_task(db, task_id)
    
    # If task doesn't exist, return 404 error
    if not task:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id '{task_id}' not found"
        )
    
    return task


@router.post("", response_model=Task, status_code=201)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new task.
    
    Request Body:
    - block_id: UUID of the parent block (required)
    - category_id: UUID of the category/project (required)
    - title: Task title (required, 1-200 characters)
    - description: Optional detailed description (max 250 characters)
    - estimated_minutes: Estimated time in minutes (required, > 0)
    - position: Order within block (optional, defaults to end)
    
    The task will be validated to ensure:
    - The block exists
    - The category exists
    - Estimated minutes is positive
    
    If position is 0 or not provided, the task will be added to the end of the block.
    
    Returns:
    - Newly created Task object with generated id and timestamps
    
    Raises:
    - 400: Block or category not found
    - 422: Validation error
    
    Example Request:
    ```json
    {
        "block_id": "block-uuid",
        "category_id": "category-uuid",
        "title": "Study FastAPI",
        "description": "Read chapters 3-5",
        "estimated_minutes": 45,
        "position": 0
    }
    ```
    """
    # Call service layer to create the task
    # Service validates that block and category exist
    new_task = task_service.create_task(db, task)
    
    # If block or category doesn't exist, return 400 error
    if not new_task:
        raise HTTPException(
            status_code=400,
            detail="Cannot create task. Block or category not found."
        )
    
    return new_task


@router.put("/{task_id}", response_model=Task)
def update_task(
    task_id: str,
    task_update: TaskUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing task.
    
    Path Parameters:
    - task_id: UUID string of the task to update
    
    Request Body (all fields optional):
    - block_id: Move task to different block
    - category_id: Change task's category
    - title: New title
    - description: New description
    - estimated_minutes: New estimate
    - actual_minutes: Record actual time spent
    - completed: Mark as complete/incomplete
    - position: Change position within block
    
    Only provided fields will be updated. Omitted fields remain unchanged.
    
    Special behavior:
    - If completed changes from false→true, completed_at is set to now
    - If completed changes from true→false, completed_at is cleared
    
    Returns:
    - Updated Task object
    
    Raises:
    - 404: Task not found
    - 422: Validation error
    
    Example Request (mark as complete):
    ```json
    {
        "completed": true,
        "actual_minutes": 50
    }
    ```
    """
    # Call service layer to update the task
    updated_task = task_service.update_task(db, task_id, task_update)
    
    # If task doesn't exist, return 404 error
    if not updated_task:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id '{task_id}' not found"
        )
    
    return updated_task


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a task.
    
    Path Parameters:
    - task_id: UUID string of the task to delete
    
    Returns:
    - 204 No Content on success
    
    Raises:
    - 404: Task not found
    """
    # Call service layer to delete the task
    deleted = task_service.delete_task(db, task_id)
    
    # If task doesn't exist, return 404 error
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id '{task_id}' not found"
        )
    
    # Return 204 No Content (successful deletion with no response body)
    return None


# ============================================================================
# TASK OPERATIONS
# ============================================================================

@router.post("/{task_id}/complete", response_model=Task)
def complete_task(
    task_id: str,
    actual_minutes: Optional[int] = Body(None, embed=True, description="Actual time spent on task (optional)"),
    db: Session = Depends(get_db)
):
    """
    Mark a task as complete.
    
    This sets:
    - completed = True
    - completed_at = current timestamp
    - actual_minutes = provided value (optional)
    
    Path Parameters:
    - task_id: UUID string of the task
    
    Request Body:
    - actual_minutes: Optional actual time spent (for tracking accuracy)
    
    Returns:
    - Updated Task object
    
    Raises:
    - 404: Task not found
    
    Example Request:
    ```json
    {
        "actual_minutes": 50
    }
    ```
    """
    # Call service layer to complete the task
    completed_task = task_service.complete_task(db, task_id, actual_minutes)
    
    # If task doesn't exist, return 404 error
    if not completed_task:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id '{task_id}' not found"
        )
    
    return completed_task


@router.post("/{task_id}/uncomplete", response_model=Task)
def uncomplete_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """
    Mark a task as incomplete.
    
    This sets:
    - completed = False
    - completed_at = None
    
    Useful for undoing a completion or resetting a task.
    
    Path Parameters:
    - task_id: UUID string of the task
    
    Returns:
    - Updated Task object
    
    Raises:
    - 404: Task not found
    """
    # Call service layer to uncomplete the task
    uncompleted_task = task_service.uncomplete_task(db, task_id)
    
    # If task doesn't exist, return 404 error
    if not uncompleted_task:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id '{task_id}' not found"
        )
    
    return uncompleted_task


@router.post("/reorder", response_model=dict)
def reorder_tasks(
    task_positions: List[dict] = Body(
        ...,
        description="List of dicts with 'task_id' and 'position' keys",
        example=[
            {"task_id": "uuid-1", "position": 0},
            {"task_id": "uuid-2", "position": 1},
            {"task_id": "uuid-3", "position": 2}
        ]
    ),
    db: Session = Depends(get_db)
):
    """
    Update the position of multiple tasks at once.
    
    This is useful for drag-and-drop reordering in the UI.
    Tasks with lower position numbers appear first.
    
    Request Body:
    - Array of objects with:
      - task_id: UUID string of the task
      - position: New position (0-based index)
    
    Returns:
    - Success status
    
    Raises:
    - 400: If reordering fails
    
    Example Request:
    ```json
    [
        {"task_id": "uuid-1", "position": 2},
        {"task_id": "uuid-2", "position": 0},
        {"task_id": "uuid-3", "position": 1}
    ]
    ```
    
    This would reorder tasks: task-2 (0), task-3 (1), task-1 (2)
    """
    # Call service layer to reorder tasks
    success = task_service.reorder_tasks(db, task_positions)
    
    # If reordering fails, return 400 error
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Failed to reorder tasks. Check that all task_ids are valid."
        )
    
    return {"success": True, "message": f"Reordered {len(task_positions)} tasks"}


# ============================================================================
# FILTERED QUERIES
# ============================================================================

@router.get("/block/{block_id}", response_model=List[Task])
def get_tasks_by_block(
    block_id: str,
    order_by_position: bool = Query(True, description="Order tasks by position"),
    db: Session = Depends(get_db)
):
    """
    Get all tasks in a specific block.
    
    Path Parameters:
    - block_id: UUID string of the block
    
    Query Parameters:
    - order_by_position: Whether to order by position field (default: true)
    
    Returns:
    - List of Task objects in the block
    
    Example Response:
    ```json
    [
        {"id": "task-1", "title": "First task", "position": 0, ...},
        {"id": "task-2", "title": "Second task", "position": 1, ...}
    ]
    ```
    """
    # Call service layer to get tasks by block
    tasks = task_service.get_tasks_by_block(db, block_id, order_by_position)
    return tasks


@router.get("/category/{category_id}", response_model=List[Task])
def get_tasks_by_category(
    category_id: str,
    db: Session = Depends(get_db)
):
    """
    Get all tasks in a specific category.
    
    Path Parameters:
    - category_id: UUID string of the category
    
    Returns:
    - List of Task objects in the category (ordered by created_at)
    
    Useful for:
    - Viewing all tasks for a project
    - Category-based reports
    - Time tracking per category
    """
    # Call service layer to get tasks by category
    tasks = task_service.get_tasks_by_category(db, category_id)
    return tasks


@router.get("/block/{block_id}/progress", response_model=dict)
def get_block_progress(
    block_id: str,
    db: Session = Depends(get_db)
):
    """
    Get completion progress for a specific block.
    
    This provides detailed progress information for a block.
    
    Path Parameters:
    - block_id: UUID string of the block
    
    Returns:
    - Dictionary with:
      - block_id: The block UUID
      - total_tasks: Total number of tasks
      - completed_tasks: Number of completed tasks
      - completion_percentage: Percentage complete (0-100)
      - total_estimated_minutes: Sum of all estimated minutes
      - total_actual_minutes: Sum of actual minutes for completed tasks
      - remaining_estimated_minutes: Estimated time for incomplete tasks
      - is_complete: Boolean indicating if all tasks are complete
    
    Raises:
    - 404: Block not found
    
    Example Response:
    ```json
    {
        "block_id": "uuid-123",
        "total_tasks": 5,
        "completed_tasks": 3,
        "completion_percentage": 60.0,
        "total_estimated_minutes": 150,
        "total_actual_minutes": 160,
        "remaining_estimated_minutes": 60,
        "is_complete": false
    }
    ```
    """
    # Call service layer to get block progress
    progress = task_service.get_block_progress(db, block_id)
    
    # If block doesn't exist, return 404 error
    if not progress:
        raise HTTPException(
            status_code=404,
            detail=f"Block with id '{block_id}' not found"
        )
    
    return progress


# ============================================================================
# BULK OPERATIONS
# ============================================================================

@router.post("/bulk-complete", response_model=dict)
def bulk_complete_tasks(
    task_ids: List[str] = Body(..., description="List of task UUIDs to complete"),
    db: Session = Depends(get_db)
):
    """
    Mark multiple tasks as complete at once.
    
    This is useful for:
    - Completing multiple tasks in one action
    - Batch operations from the UI
    - End-of-session completions
    
    Request Body:
    - Array of task UUID strings
    
    Returns:
    - Dictionary with count of successfully completed tasks
    
    Example Request:
    ```json
    {
        "task_ids": ["uuid-1", "uuid-2", "uuid-3"]
    }
    ```
    
    Example Response:
    ```json
    {
        "success": true,
        "completed_count": 3,
        "message": "Completed 3 tasks"
    }
    ```
    """
    # Call service layer to complete multiple tasks
    completed_count = task_service.bulk_complete_tasks(db, task_ids)
    
    return {
        "success": True,
        "completed_count": completed_count,
        "message": f"Completed {completed_count} tasks"
    }


@router.post("/bulk-uncomplete", response_model=dict)
def bulk_uncomplete_tasks(
    task_ids: List[str] = Body(..., description="List of task UUIDs to uncomplete"),
    db: Session = Depends(get_db)
):
    """
    Mark multiple tasks as incomplete at once.
    
    This is useful for:
    - Undoing bulk completions
    - Resetting multiple tasks
    - Batch operations from the UI
    
    Request Body:
    - Array of task UUID strings
    
    Returns:
    - Dictionary with count of successfully uncompleted tasks
    
    Example Request:
    ```json
    {
        "task_ids": ["uuid-1", "uuid-2", "uuid-3"]
    }
    ```
    
    Example Response:
    ```json
    {
        "success": true,
        "uncompleted_count": 3,
        "message": "Uncompleted 3 tasks"
    }
    ```
    """
    # Call service layer to uncomplete multiple tasks
    uncompleted_count = task_service.bulk_uncomplete_tasks(db, task_ids)
    
    return {
        "success": True,
        "uncompleted_count": uncompleted_count,
        "message": f"Uncompleted {uncompleted_count} tasks"
    }

