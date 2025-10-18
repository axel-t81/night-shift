"""
Task Service

This service handles all business logic for tasks.
Tasks are individual work items within time blocks, organized by categories.

Functions:
- get_all_tasks: List all tasks with optional filtering
- get_task: Get a single task by ID
- get_tasks_by_block: Get all tasks in a specific block
- get_tasks_by_category: Get all tasks in a specific category
- create_task: Create a new task
- update_task: Update an existing task
- delete_task: Delete a task
- complete_task: Mark a task as complete with actual time
- uncomplete_task: Mark a task as incomplete
- reorder_tasks: Update task positions within a block
- get_block_progress: Get completion progress for a block
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict
from datetime import datetime

from app.models.task import Task
from app.models.block import Block
from app.models.category import Category
from app.schemas.task import TaskCreate, TaskUpdate


def get_all_tasks(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    completed: Optional[bool] = None,
    block_id: Optional[str] = None,
    category_id: Optional[str] = None
) -> List[Task]:
    """
    Get all tasks with optional filtering and pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        completed: Filter by completion status (None = all tasks)
        block_id: Filter by block ID
        category_id: Filter by category ID
        
    Returns:
        List of Task objects
    """
    query = db.query(Task)
    
    # Apply filters
    if completed is not None:
        query = query.filter(Task.completed == completed)
    if block_id:
        query = query.filter(Task.block_id == block_id)
    if category_id:
        query = query.filter(Task.category_id == category_id)
    
    # Order by block, then position within block
    return query.order_by(Task.block_id, Task.position).offset(skip).limit(limit).all()


def get_task(db: Session, task_id: str) -> Optional[Task]:
    """
    Get a single task by ID.
    
    Args:
        db: Database session
        task_id: UUID string of the task
        
    Returns:
        Task object if found, None otherwise
    """
    return db.query(Task).filter(Task.id == task_id).first()


def get_tasks_by_block(db: Session, block_id: str, order_by_position: bool = True) -> List[Task]:
    """
    Get all tasks in a specific block.
    
    Args:
        db: Database session
        block_id: UUID string of the block
        order_by_position: Whether to order by position field (default True)
        
    Returns:
        List of Task objects in the block
    """
    query = db.query(Task).filter(Task.block_id == block_id)
    if order_by_position:
        query = query.order_by(Task.position)
    return query.all()


def get_tasks_by_category(db: Session, category_id: str) -> List[Task]:
    """
    Get all tasks in a specific category.
    
    Args:
        db: Database session
        category_id: UUID string of the category
        
    Returns:
        List of Task objects in the category
    """
    return db.query(Task).filter(Task.category_id == category_id).order_by(Task.created_at).all()


def create_task(db: Session, task: TaskCreate) -> Optional[Task]:
    """
    Create a new task.
    
    Validates that the block exists before creating.
    If category_id is not provided, it will be inherited from the block's category.
    If category_id is provided, it must match the block's category (if block has one).
    
    Args:
        db: Database session
        task: TaskCreate schema with task data
        
    Returns:
        Newly created Task object, or None if block doesn't exist or category validation fails
    """
    # Verify block exists
    block = db.query(Block).filter(Block.id == task.block_id).first()
    if not block:
        return None
    
    # Determine category_id: inherit from block if not provided
    if task.category_id:
        category_id = task.category_id
        # Verify category exists
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return None
        # If block has a category, ensure task's category matches
        if block.category_id and block.category_id != category_id:
            return None
    else:
        # Inherit category from block
        category_id = block.category_id
        if not category_id:
            # Block has no category, task must provide one
            return None
    
    # If position not provided, set to end of block
    if task.position == 0:
        max_position = db.query(func.max(Task.position)).filter(Task.block_id == task.block_id).scalar()
        position = (max_position + 1) if max_position is not None else 0
    else:
        position = task.position
    
    db_task = Task(
        block_id=task.block_id,
        category_id=category_id,
        title=task.title,
        description=task.description,
        estimated_minutes=task.estimated_minutes,
        position=position
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, task_id: str, task_update: TaskUpdate) -> Optional[Task]:
    """
    Update an existing task.
    
    Args:
        db: Database session
        task_id: UUID string of the task to update
        task_update: TaskUpdate schema with fields to update
        
    Returns:
        Updated Task object if found, None otherwise
    """
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    
    # Update only provided fields
    update_data = task_update.model_dump(exclude_unset=True)
    
    # Handle completion status change
    if 'completed' in update_data:
        if update_data['completed'] and not db_task.completed:
            # Task is being marked as complete
            db_task.completed_at = datetime.utcnow()
        elif not update_data['completed'] and db_task.completed:
            # Task is being marked as incomplete
            db_task.completed_at = None
    
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: str) -> bool:
    """
    Delete a task.
    
    Args:
        db: Database session
        task_id: UUID string of the task to delete
        
    Returns:
        True if deleted successfully, False if task not found
    """
    db_task = get_task(db, task_id)
    if not db_task:
        return False
    
    db.delete(db_task)
    db.commit()
    return True


def complete_task(db: Session, task_id: str, actual_minutes: Optional[int] = None) -> Optional[Task]:
    """
    Mark a task as complete.
    
    Args:
        db: Database session
        task_id: UUID string of the task
        actual_minutes: Optional actual time spent on the task
        
    Returns:
        Updated Task object if found, None otherwise
    """
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    
    db_task.completed = True
    db_task.completed_at = datetime.utcnow()
    if actual_minutes is not None:
        db_task.actual_minutes = actual_minutes
    
    db.commit()
    db.refresh(db_task)
    return db_task


def uncomplete_task(db: Session, task_id: str) -> Optional[Task]:
    """
    Mark a task as incomplete.
    
    Args:
        db: Database session
        task_id: UUID string of the task
        
    Returns:
        Updated Task object if found, None otherwise
    """
    db_task = get_task(db, task_id)
    if not db_task:
        return None
    
    db_task.completed = False
    db_task.completed_at = None
    
    db.commit()
    db.refresh(db_task)
    return db_task


def reorder_tasks(db: Session, task_positions: List[Dict[str, int]]) -> bool:
    """
    Update the positions of multiple tasks.
    
    Useful for drag-and-drop reordering in the UI.
    
    Args:
        db: Database session
        task_positions: List of dicts with 'task_id' and 'position' keys
                       Example: [{"task_id": "uuid1", "position": 0}, ...]
        
    Returns:
        True if all tasks updated successfully, False otherwise
    """
    try:
        for item in task_positions:
            task_id = item.get('task_id')
            position = item.get('position')
            
            if task_id is None or position is None:
                continue
            
            db_task = get_task(db, task_id)
            if db_task:
                db_task.position = position
        
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False


def get_block_progress(db: Session, block_id: str) -> Optional[Dict]:
    """
    Get completion progress for a specific block.
    
    Args:
        db: Database session
        block_id: UUID string of the block
        
    Returns:
        Dictionary with progress information:
        - block_id: The block ID
        - total_tasks: Total number of tasks
        - completed_tasks: Number of completed tasks
        - completion_percentage: Percentage complete (0-100)
        - total_estimated_minutes: Sum of all estimated minutes
        - total_actual_minutes: Sum of actual minutes for completed tasks
        - remaining_estimated_minutes: Estimated time for incomplete tasks
        
        Returns None if block doesn't exist
    """
    # Verify block exists
    block = db.query(Block).filter(Block.id == block_id).first()
    if not block:
        return None
    
    # Get task counts
    total_tasks = db.query(func.count(Task.id)).filter(Task.block_id == block_id).scalar()
    completed_tasks = db.query(func.count(Task.id)).filter(
        Task.block_id == block_id,
        Task.completed == True
    ).scalar()
    
    # Calculate completion percentage
    completion_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Get time estimates
    total_estimated = db.query(func.sum(Task.estimated_minutes)).filter(
        Task.block_id == block_id
    ).scalar() or 0
    
    total_actual = db.query(func.sum(Task.actual_minutes)).filter(
        Task.block_id == block_id,
        Task.completed == True,
        Task.actual_minutes.isnot(None)
    ).scalar() or 0
    
    remaining_estimated = db.query(func.sum(Task.estimated_minutes)).filter(
        Task.block_id == block_id,
        Task.completed == False
    ).scalar() or 0
    
    return {
        "block_id": block_id,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "completion_percentage": round(completion_percentage, 2),
        "total_estimated_minutes": total_estimated,
        "total_actual_minutes": total_actual,
        "remaining_estimated_minutes": remaining_estimated,
        "is_complete": completed_tasks == total_tasks and total_tasks > 0
    }


def bulk_complete_tasks(db: Session, task_ids: List[str]) -> int:
    """
    Mark multiple tasks as complete.
    
    Args:
        db: Database session
        task_ids: List of task UUID strings
        
    Returns:
        Number of tasks successfully marked as complete
    """
    completed_count = 0
    for task_id in task_ids:
        if complete_task(db, task_id):
            completed_count += 1
    return completed_count


def bulk_uncomplete_tasks(db: Session, task_ids: List[str]) -> int:
    """
    Mark multiple tasks as incomplete.
    
    Args:
        db: Database session
        task_ids: List of task UUID strings
        
    Returns:
        Number of tasks successfully marked as incomplete
    """
    uncompleted_count = 0
    for task_id in task_ids:
        if uncomplete_task(db, task_id):
            uncompleted_count += 1
    return uncompleted_count
