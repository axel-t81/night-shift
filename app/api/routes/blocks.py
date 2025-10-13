"""
Block API Routes

This module contains all API endpoints for managing blocks (time blocks/Pomodoro sessions).
Blocks are category-agnostic time containers that hold tasks.

Key Feature: RECURRING BLOCKS
Blocks can be completed and reset to repeat indefinitely, supporting the recurring workflow.

Endpoints:
=== Standard CRUD ===
- GET    /api/blocks                       - List blocks with filters
- GET    /api/blocks/{id}                  - Get single block
- GET    /api/blocks/{id}/with-tasks       - Get block with all tasks
- POST   /api/blocks                       - Create new block
- PUT    /api/blocks/{id}                  - Update block
- DELETE /api/blocks/{id}                  - Delete block

=== Recurring Block Operations ===
- POST   /api/blocks/{id}/complete-and-reset  - Complete & reset for recurrence
- POST   /api/blocks/{id}/reset-tasks         - Reset all tasks to incomplete
- POST   /api/blocks/{id}/move-to-end         - Move to end of queue
- POST   /api/blocks/{id}/clone               - Clone block with tasks

=== Queue Management ===
- GET    /api/blocks/next                  - Get next block in queue
- GET    /api/blocks/active                - Get blocks with incomplete tasks
- POST   /api/blocks/reorder               - Reorder multiple blocks
- GET    /api/blocks/statistics            - Get overall block statistics
"""

from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

# Import database dependency
from app.database import get_db

# Import schemas for request/response validation
from app.schemas.block import Block, BlockCreate, BlockUpdate

# Import service layer for business logic
from app.services import block_service


# Create router for block endpoints
router = APIRouter()


# ============================================================================
# QUEUE MANAGEMENT OPERATIONS (Must come BEFORE parameterized routes!)
# ============================================================================

@router.get("/next", response_model=dict)
def get_next_block(
    db: Session = Depends(get_db)
):
    """
    Get the next block in the queue that has incomplete tasks.
    
    This returns the block with the lowest block_number that still has
    incomplete tasks.
    
    Useful for:
    - "What should I work on next?" UI feature
    - Automatic block selection
    - Progress tracking
    
    Returns:
    - Dictionary with block info and progress, or message if no blocks
    
    Example Response:
    ```json
    {
        "block": {...},
        "total_tasks": 5,
        "completed_tasks": 2,
        "completion_percentage": 40.0
    }
    ```
    
    Or if no blocks available:
    ```json
    {
        "message": "No blocks available"
    }
    ```
    """
    # Call service layer to get next block
    result = block_service.get_next_block(db)
    
    # If no blocks available, return a message
    if not result:
        return {"message": "No blocks available"}
    
    # Convert SQLAlchemy Block object to Pydantic model for JSON serialization
    return {
        "block": Block.model_validate(result["block"]),
        "total_tasks": result["total_tasks"],
        "completed_tasks": result["completed_tasks"],
        "completion_percentage": result["completion_percentage"]
    }


@router.get("/active", response_model=List[Block])
def get_active_blocks(
    day_number: Optional[int] = Query(None, ge=1, le=5, description="Filter by day number"),
    db: Session = Depends(get_db)
):
    """
    Get blocks that have incomplete tasks (active work).
    
    This returns blocks that are "in progress" - they have at least one
    incomplete task.
    
    Query Parameters:
    - day_number: Optional filter by specific day (1-5)
    
    Returns:
    - List of Block objects that have incomplete tasks
    
    Example Response:
    ```json
    [
        {
            "id": "uuid-123",
            "title": "Morning Routine",
            "block_number": 1,
            ...
        }
    ]
    ```
    """
    # Call service layer to get active blocks
    active_blocks = block_service.get_active_blocks(db, day_number)
    return active_blocks


@router.get("/statistics", response_model=dict)
def get_block_statistics(
    db: Session = Depends(get_db)
):
    """
    Get overall statistics for all blocks.
    
    Returns aggregate statistics useful for dashboard views.
    
    Returns:
    - Dictionary with:
      - total_blocks: Total number of blocks
      - completed_blocks: Blocks with all tasks complete
      - active_blocks: Blocks with at least one incomplete task
      - blocks_with_no_tasks: Empty blocks
    
    Example Response:
    ```json
    {
        "total_blocks": 20,
        "completed_blocks": 5,
        "active_blocks": 12,
        "blocks_with_no_tasks": 3
    }
    ```
    """
    # Call service layer to get block statistics
    stats = block_service.get_block_statistics(db)
    return stats


@router.post("/reorder", response_model=dict)
def reorder_blocks(
    block_orders: List[dict] = Body(
        ...,
        description="List of dicts with 'block_id' and 'block_number' keys",
        example=[
            {"block_id": "uuid-1", "block_number": 1},
            {"block_id": "uuid-2", "block_number": 2},
            {"block_id": "uuid-3", "block_number": 3}
        ]
    ),
    db: Session = Depends(get_db)
):
    """
    Update the block_number for multiple blocks at once.
    
    This is useful for manual reordering of blocks in the UI (e.g., drag-and-drop).
    
    Request Body:
    - Array of objects with:
      - block_id: UUID string of the block
      - block_number: New block number (determines queue position)
    
    Returns:
    - Success status
    
    Raises:
    - 400: If reordering fails
    
    Example Request:
    ```json
    [
        {"block_id": "uuid-1", "block_number": 3},
        {"block_id": "uuid-2", "block_number": 1},
        {"block_id": "uuid-3", "block_number": 2}
    ]
    ```
    
    This would reorder blocks: block-2 (1st), block-3 (2nd), block-1 (3rd)
    """
    # Call service layer to reorder blocks
    success = block_service.reorder_blocks(db, block_orders)
    
    # If reordering fails, return 400 error
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Failed to reorder blocks. Check that all block_ids are valid."
        )
    
    return {"success": True, "message": f"Reordered {len(block_orders)} blocks"}


# ============================================================================
# STANDARD CRUD OPERATIONS
# ============================================================================

@router.get("/", response_model=List[Block])
def list_blocks(
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    day_number: Optional[int] = Query(None, ge=1, le=5, description="Filter by day number (1-5)"),
    order_by: str = Query("block_number", regex="^(block_number|created_at)$", 
                          description="Field to order by"),
    db: Session = Depends(get_db)
):
    """
    List all blocks with optional filtering and pagination.
    
    Query Parameters:
    - skip: Number of records to skip (for pagination)
    - limit: Maximum number of records to return (1-1000)
    - day_number: Filter by specific day (1-5)
    - order_by: Field to order by (block_number or created_at)
    
    Returns:
    - List of Block objects ordered by the specified field
    
    Example Response:
    ```json
    [
        {
            "id": "uuid-123",
            "title": "Morning Deep Work",
            "description": "Focus on coding projects",
            "block_number": 1,
            "day_number": 1,
            "created_at": "2024-01-15T10:30:00"
        }
    ]
    ```
    """
    # Call service layer to get blocks with filters
    blocks = block_service.get_all_blocks(
        db,
        skip=skip,
        limit=limit,
        day_number=day_number,
        order_by=order_by
    )
    return blocks


@router.get("/{block_id}", response_model=Block)
def get_block(
    block_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a single block by ID.
    
    Path Parameters:
    - block_id: UUID string of the block
    
    Returns:
    - Block object with all fields
    
    Raises:
    - 404: Block not found
    """
    # Call service layer to get the block
    block = block_service.get_block(db, block_id)
    
    # If block doesn't exist, return 404 error
    if not block:
        raise HTTPException(
            status_code=404,
            detail=f"Block with id '{block_id}' not found"
        )
    
    return block


@router.get("/{block_id}/with-tasks", response_model=dict)
def get_block_with_tasks(
    block_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a block with all its tasks included.
    
    This endpoint returns the block plus:
    - List of all tasks in the block (ordered by position)
    - Task count
    - Completed task count
    
    Useful for displaying a complete block view in the UI.
    
    Path Parameters:
    - block_id: UUID string of the block
    
    Returns:
    - Dictionary with block, tasks array, and counts
    
    Raises:
    - 404: Block not found
    
    Example Response:
    ```json
    {
        "block": {...},
        "tasks": [...],
        "task_count": 5,
        "completed_tasks": 2
    }
    ```
    """
    # Import Task schema for serialization
    from app.schemas.task import Task as TaskSchema
    
    # Call service layer to get block with tasks
    result = block_service.get_block_with_tasks(db, block_id)
    
    # If block doesn't exist, return 404 error
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Block with id '{block_id}' not found"
        )
    
    # Convert SQLAlchemy objects to Pydantic models for JSON serialization
    return {
        "block": Block.model_validate(result["block"]),
        "tasks": [TaskSchema.model_validate(task) for task in result["tasks"]],
        "task_count": result["task_count"],
        "completed_tasks": result["completed_tasks"]
    }


@router.post("/", response_model=Block, status_code=201)
def create_block(
    block: BlockCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new block.
    
    Request Body:
    - title: Block title (required, 1-200 characters)
    - description: Optional description (max 200 characters)
    - block_number: Order within day (optional, auto-assigned if not provided)
    - day_number: Day of cycle (optional, 1-5)
    
    If block_number is not provided, it will be auto-assigned as the next available number.
    
    Returns:
    - Newly created Block object with generated id and timestamps
    
    Raises:
    - 422: Validation error
    
    Example Request:
    ```json
    {
        "title": "Morning Deep Work",
        "description": "Focus on coding projects",
        "block_number": 1,
        "day_number": 1
    }
    ```
    """
    # Call service layer to create the block
    # Service handles UUID generation, timestamp creation, and block_number assignment
    new_block = block_service.create_block(db, block)
    return new_block


@router.put("/{block_id}", response_model=Block)
def update_block(
    block_id: str,
    block_update: BlockUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing block.
    
    Path Parameters:
    - block_id: UUID string of the block to update
    
    Request Body (all fields optional):
    - title: New title
    - description: New description
    - block_number: New block number
    - day_number: New day number (1-5)
    
    Only provided fields will be updated. Omitted fields remain unchanged.
    
    Returns:
    - Updated Block object
    
    Raises:
    - 404: Block not found
    - 422: Validation error
    """
    # Call service layer to update the block
    updated_block = block_service.update_block(db, block_id, block_update)
    
    # If block doesn't exist, return 404 error
    if not updated_block:
        raise HTTPException(
            status_code=404,
            detail=f"Block with id '{block_id}' not found"
        )
    
    return updated_block


@router.delete("/{block_id}", status_code=204)
def delete_block(
    block_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a block and all its tasks.
    
    Path Parameters:
    - block_id: UUID string of the block to delete
    
    Important: This will CASCADE DELETE all tasks in the block.
    Make sure this is intentional before calling this endpoint.
    
    Returns:
    - 204 No Content on success
    
    Raises:
    - 404: Block not found
    """
    # Call service layer to delete the block
    deleted = block_service.delete_block(db, block_id)
    
    # If block doesn't exist, return 404 error
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Block with id '{block_id}' not found"
        )
    
    # Return 204 No Content (successful deletion with no response body)
    return None


# ============================================================================
# RECURRING BLOCK OPERATIONS
# ============================================================================

@router.post("/{block_id}/complete-and-reset", response_model=dict)
def complete_and_reset_block(
    block_id: str,
    move_to_end: bool = Query(True, description="Whether to move the block to end of queue"),
    db: Session = Depends(get_db)
):
    """
    Complete all tasks in a block, then reset them for recurrence.
    
    This is the KEY ENDPOINT for recurring blocks. It:
    1. Marks all incomplete tasks as complete (with completion timestamp)
    2. Immediately resets all tasks to incomplete (ready for next cycle)
    3. Optionally moves the block to the end of the queue
    
    This creates a recurring workflow where blocks repeat indefinitely.
    
    Path Parameters:
    - block_id: UUID string of the block
    
    Query Parameters:
    - move_to_end: Whether to move block to end of queue (default: true)
    
    Returns:
    - Dictionary with operation results
    
    Raises:
    - 404: Block not found
    
    Example Use Case:
    You've completed all tasks in "Morning Routine" block. Call this endpoint
    to mark completion (for tracking), reset the tasks (ready to do again),
    and move the block to the end of your queue.
    
    Example Response:
    ```json
    {
        "block_id": "uuid-123",
        "block_title": "Morning Routine",
        "tasks_completed": 3,
        "tasks_reset": 3,
        "new_block_number": 10,
        "moved_to_end": true
    }
    ```
    """
    # Call service layer to complete and reset the block
    result = block_service.complete_and_reset_block(db, block_id, move_to_end)
    
    # If block doesn't exist, return 404 error
    if not result:
        raise HTTPException(
            status_code=404,
            detail=f"Block with id '{block_id}' not found"
        )
    
    return result


@router.post("/{block_id}/reset-tasks", response_model=dict)
def reset_block_tasks(
    block_id: str,
    db: Session = Depends(get_db)
):
    """
    Reset all tasks in a block to incomplete status.
    
    This sets all tasks in the block to:
    - completed = False
    - completed_at = None
    - actual_minutes = None
    
    Useful for manually resetting a block without moving it in the queue.
    
    Path Parameters:
    - block_id: UUID string of the block
    
    Returns:
    - Dictionary with count of tasks reset
    
    Raises:
    - 404: Block not found
    
    Example Response:
    ```json
    {
        "block_id": "uuid-123",
        "tasks_reset": 5
    }
    ```
    """
    # Call service layer to reset block tasks
    reset_count = block_service.reset_block_tasks(db, block_id)
    
    # If block doesn't exist, return 404 error
    if reset_count is None:
        raise HTTPException(
            status_code=404,
            detail=f"Block with id '{block_id}' not found"
        )
    
    return {
        "block_id": block_id,
        "tasks_reset": reset_count
    }


@router.post("/{block_id}/move-to-end", response_model=Block)
def move_block_to_end(
    block_id: str,
    db: Session = Depends(get_db)
):
    """
    Move a block to the end of the queue.
    
    This sets the block's block_number to be higher than all other blocks,
    effectively moving it to the back of the queue.
    
    Useful for manually reordering blocks or deferring a block.
    
    Path Parameters:
    - block_id: UUID string of the block
    
    Returns:
    - Updated Block object with new block_number
    
    Raises:
    - 404: Block not found
    """
    # Call service layer to move block to end
    updated_block = block_service.move_block_to_end(db, block_id)
    
    # If block doesn't exist, return 404 error
    if not updated_block:
        raise HTTPException(
            status_code=404,
            detail=f"Block with id '{block_id}' not found"
        )
    
    return updated_block


@router.post("/{block_id}/clone", response_model=Block)
def clone_block(
    block_id: str,
    copy_tasks: bool = Body(True, description="Whether to copy all tasks from source block"),
    db: Session = Depends(get_db)
):
    """
    Create a copy of a block, optionally with all its tasks.
    
    This is useful for creating recurring blocks - you can clone a
    "template" block multiple times.
    
    Path Parameters:
    - block_id: UUID string of the block to clone
    
    Request Body:
    - copy_tasks: Whether to copy all tasks (default: true)
    
    Returns:
    - Newly created Block object (cloned)
    
    Raises:
    - 404: Source block not found
    
    Example Use Case:
    You have a "Morning Routine" template block. Clone it to create
    a separate instance.
    
    Example Response:
    ```json
    {
        "id": "new-uuid",
        "title": "Morning Routine (Copy)",
        "description": "Daily morning tasks",
        "block_number": 11,
        "day_number": 1,
        ...
    }
    ```
    """
    # Call service layer to clone the block
    cloned_block = block_service.clone_block(
        db,
        block_id,
        copy_tasks=copy_tasks
    )
    
    # If source block doesn't exist, return 404 error
    if not cloned_block:
        raise HTTPException(
            status_code=404,
            detail=f"Source block with id '{block_id}' not found"
        )
    
    return cloned_block

