"""
Block Service

This service handles all business logic for time blocks (Pomodoro sessions).
Includes special support for RECURRING BLOCKS - blocks that reset and repeat.

Key Feature: When a block is completed, it can be reset (all tasks marked incomplete)
and moved to the back of the queue, creating a recurring workflow.

Functions:
- get_all_blocks: List all blocks with optional filtering
- get_block: Get a single block by ID
- get_block_with_tasks: Get a block with all its tasks
- create_block: Create a new time block
- update_block: Update an existing block
- delete_block: Delete a block and its tasks
- complete_and_reset_block: Mark all tasks complete, then reset for recurrence
- reset_block_tasks: Reset all tasks in a block to incomplete
- move_block_to_end: Move a block to the end of the queue
- clone_block: Create a copy of a block with all its tasks
- reorder_blocks: Update block ordering
- get_active_blocks: Get blocks for the current time period
- get_next_block: Get the next incomplete block in the queue
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import List, Optional, Dict, Tuple
from datetime import datetime, timedelta
import uuid

from app.models.block import Block
from app.models.task import Task
from app.models.category import Category
from app.schemas.block import BlockCreate, BlockUpdate


def get_all_blocks(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    day_number: Optional[int] = None,
    order_by: str = "block_number"
) -> List[Block]:
    """
    Get all blocks with optional filtering and pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        day_number: Filter by specific day (1-5)
        order_by: Field to order by ("block_number", "created_at")
        
    Returns:
        List of Block objects
    """
    query = db.query(Block)
    
    if day_number:
        query = query.filter(Block.day_number == day_number)
    
    # Apply ordering
    if order_by == "block_number":
        query = query.order_by(Block.block_number)
    else:
        query = query.order_by(Block.created_at)
    
    return query.offset(skip).limit(limit).all()


def get_block(db: Session, block_id: str) -> Optional[Block]:
    """
    Get a single block by ID.
    
    Args:
        db: Database session
        block_id: UUID string of the block
        
    Returns:
        Block object if found, None otherwise
    """
    return db.query(Block).filter(Block.id == block_id).first()


def get_block_with_tasks(db: Session, block_id: str) -> Optional[Dict]:
    """
    Get a block with all its tasks included.
    
    Args:
        db: Database session
        block_id: UUID string of the block
        
    Returns:
        Dictionary with block info and tasks list, or None if block not found
    """
    block = get_block(db, block_id)
    if not block:
        return None
    
    tasks = db.query(Task).filter(Task.block_id == block_id).order_by(Task.position).all()
    
    return {
        "block": block,
        "tasks": tasks,
        "task_count": len(tasks),
        "completed_tasks": sum(1 for task in tasks if task.completed)
    }


def create_block(db: Session, block: BlockCreate) -> Optional[Block]:
    """
    Create a new block.
    
    Args:
        db: Database session
        block: BlockCreate schema with block data
        
    Returns:
        Newly created Block object, or None if category doesn't exist
    """
    # Validate category if provided
    if block.category_id:
        category = db.query(Category).filter(Category.id == block.category_id).first()
        if not category:
            return None
    
    # If block_number not provided, set to next available number
    if block.block_number is None:
        max_block_number = db.query(func.max(Block.block_number)).scalar()
        if max_block_number is not None:
            block_number = max_block_number + 1
        else:
            block_number = 1
    else:
        block_number = block.block_number
    
    db_block = Block(
        title=block.title,
        description=block.description,
        block_number=block_number,
        day_number=block.day_number,
        category_id=block.category_id
    )
    db.add(db_block)
    db.commit()
    db.refresh(db_block)
    return db_block


def update_block(db: Session, block_id: str, block_update: BlockUpdate) -> Optional[Block]:
    """
    Update an existing block.
    
    Args:
        db: Database session
        block_id: UUID string of the block to update
        block_update: BlockUpdate schema with fields to update
        
    Returns:
        Updated Block object if found, None otherwise
    """
    db_block = get_block(db, block_id)
    if not db_block:
        return None
    
    # Update only provided fields
    update_data = block_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_block, field, value)
    
    db.commit()
    db.refresh(db_block)
    return db_block


def delete_block(db: Session, block_id: str) -> bool:
    """
    Delete a block and all its tasks (CASCADE).
    
    Args:
        db: Database session
        block_id: UUID string of the block to delete
        
    Returns:
        True if deleted successfully, False if block not found
    """
    db_block = get_block(db, block_id)
    if not db_block:
        return False
    
    db.delete(db_block)
    db.commit()
    return True


def reset_block_tasks(db: Session, block_id: str) -> Optional[int]:
    """
    Reset all tasks in a block to incomplete status.
    
    This is used for recurring blocks - when you want to repeat the same
    block of tasks.
    
    Args:
        db: Database session
        block_id: UUID string of the block
        
    Returns:
        Number of tasks reset, or None if block doesn't exist
    """
    block = get_block(db, block_id)
    if not block:
        return None
    
    # Get all tasks in the block
    tasks = db.query(Task).filter(Task.block_id == block_id).all()
    
    # Reset each task
    reset_count = 0
    for task in tasks:
        if task.completed:
            task.completed = False
            task.completed_at = None
            task.actual_minutes = None  # Clear actual time for fresh start
            reset_count += 1
    
    db.commit()
    return reset_count


def move_block_to_end(db: Session, block_id: str) -> Optional[Block]:
    """
    Move a block to the end of the queue by giving it the highest block_number.
    
    This is used for recurring blocks - when a block is completed, move it
    to the back of the queue.
    
    Args:
        db: Database session
        block_id: UUID string of the block
        
    Returns:
        Updated Block object, or None if block doesn't exist
    """
    block = get_block(db, block_id)
    if not block:
        return None
    
    # Find the highest block_number and cycle from 1-15
    max_block_number = db.query(func.max(Block.block_number)).scalar()
    
    # Set this block's number to cycle (1-15)
    if max_block_number is not None:
        new_block_number = (max_block_number % 15) + 1
    else:
        new_block_number = 1
    block.block_number = new_block_number
    
    db.commit()
    db.refresh(block)
    return block


def complete_and_reset_block(db: Session, block_id: str, move_to_end: bool = True) -> Optional[Dict]:
    """
    Complete all tasks in a block, then reset them for recurrence.
    
    This is the KEY FUNCTION for recurring blocks. It:
    1. Marks all incomplete tasks as complete (with timestamp)
    2. Immediately resets all tasks to incomplete
    3. Optionally moves the block to the end of the queue
    
    This creates a recurring workflow where blocks repeat indefinitely.
    
    Args:
        db: Database session
        block_id: UUID string of the block
        move_to_end: Whether to move the block to end of queue (default True)
        
    Returns:
        Dictionary with operation results, or None if block doesn't exist
    """
    block = get_block(db, block_id)
    if not block:
        return None
    
    # Get all tasks
    tasks = db.query(Task).filter(Task.block_id == block_id).all()
    
    # Count tasks that were incomplete
    incomplete_tasks = [task for task in tasks if not task.completed]
    
    # Mark all incomplete tasks as complete (record the completion)
    completion_time = datetime.utcnow()
    for task in incomplete_tasks:
        task.completed = True
        task.completed_at = completion_time
        # Optionally set actual_minutes to estimated if not provided
        if task.actual_minutes is None:
            task.actual_minutes = task.estimated_minutes
    
    db.commit()
    
    # Now reset all tasks to incomplete for the next cycle
    reset_count = reset_block_tasks(db, block_id)
    
    # Move block to end of queue if requested
    if move_to_end:
        block = move_block_to_end(db, block_id)
    
    return {
        "block_id": block_id,
        "block_title": block.title,
        "tasks_completed": len(incomplete_tasks),
        "tasks_reset": reset_count,
        "new_block_number": block.block_number,
        "moved_to_end": move_to_end
    }


def clone_block(
    db: Session,
    block_id: str,
    copy_tasks: bool = True
) -> Optional[Block]:
    """
    Create a copy of a block, optionally with all its tasks.
    
    This is useful for creating true recurring blocks - you can clone a
    "template" block multiple times.
    
    Args:
        db: Database session
        block_id: UUID string of the block to clone
        copy_tasks: Whether to copy all tasks from the original block
        
    Returns:
        Newly created Block object, or None if source block doesn't exist
    """
    source_block = get_block(db, block_id)
    if not source_block:
        return None
    
    # Find next block number
    max_block_number = db.query(func.max(Block.block_number)).scalar()
    if max_block_number is not None:
        new_block_number = max_block_number + 1
    else:
        new_block_number = 1
    
    # Create new block
    new_block = Block(
        title=f"{source_block.title} (Copy)",
        description=source_block.description,
        block_number=new_block_number,
        day_number=source_block.day_number,
        category_id=source_block.category_id
    )
    db.add(new_block)
    db.flush()  # Get the ID without committing
    
    # Copy tasks if requested
    if copy_tasks:
        source_tasks = db.query(Task).filter(Task.block_id == block_id).order_by(Task.position).all()
        for source_task in source_tasks:
            new_task = Task(
                block_id=new_block.id,
                category_id=source_task.category_id,
                title=source_task.title,
                description=source_task.description,
                estimated_minutes=source_task.estimated_minutes,
                position=source_task.position,
                completed=False  # Always start fresh
            )
            db.add(new_task)
    
    db.commit()
    db.refresh(new_block)
    return new_block


def reorder_blocks(db: Session, block_orders: List[Dict[str, int]]) -> bool:
    """
    Update the block_number for multiple blocks.
    
    Useful for manual reordering of blocks in the UI.
    
    Args:
        db: Database session
        block_orders: List of dicts with 'block_id' and 'block_number' keys
                     Example: [{"block_id": "uuid1", "block_number": 1}, ...]
        
    Returns:
        True if all blocks updated successfully, False otherwise
    """
    try:
        for item in block_orders:
            block_id = item.get('block_id')
            block_number = item.get('block_number')
            
            if block_id is None or block_number is None:
                continue
            
            db_block = get_block(db, block_id)
            if db_block:
                db_block.block_number = block_number
        
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False


def get_active_blocks(db: Session, day_number: Optional[int] = None) -> List[Block]:
    """
    Get blocks for active work (incomplete blocks with tasks).
    
    Args:
        db: Database session
        day_number: Optional filter by day number
        
    Returns:
        List of blocks that have incomplete tasks, ordered by block_number
    """
    query = db.query(Block).join(Task).filter(Task.completed == False)
    
    if day_number:
        query = query.filter(Block.day_number == day_number)
    
    # Group by block to avoid duplicates, order by block_number
    return query.group_by(Block.id).order_by(Block.block_number).all()


def get_next_block(db: Session) -> Optional[Dict]:
    """
    Get the next block in the queue that has incomplete tasks.
    
    This is useful for the UI to show "What's next?"
    
    Args:
        db: Database session
        
    Returns:
        Dictionary with block info and progress, or None if no blocks available
    """
    # Find the block with the lowest block_number that has incomplete tasks
    block = db.query(Block).join(Task).filter(
        Task.completed == False
    ).group_by(Block.id).order_by(Block.block_number).first()
    
    if not block:
        return None
    
    # Get task progress for this block
    total_tasks = db.query(func.count(Task.id)).filter(Task.block_id == block.id).scalar()
    completed_tasks = db.query(func.count(Task.id)).filter(
        Task.block_id == block.id,
        Task.completed == True
    ).scalar()
    
    return {
        "block": block,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "completion_percentage": (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    }


def get_block_statistics(db: Session) -> Dict:
    """
    Get overall statistics for all blocks.
    
    Returns:
        Dictionary with aggregate statistics
    """
    total_blocks = db.query(func.count(Block.id)).scalar()
    
    # Count blocks with at least one incomplete task
    active_blocks = db.query(Block.id).join(Task).filter(
        Task.completed == False
    ).group_by(Block.id).count()
    
    # Count blocks with tasks (any status)
    blocks_with_tasks = db.query(Block.id).join(Task).group_by(Block.id).count()
    
    # Blocks with no tasks
    blocks_with_no_tasks = total_blocks - blocks_with_tasks
    
    # Completed blocks = blocks with tasks but no incomplete tasks
    completed_blocks = blocks_with_tasks - active_blocks
    
    return {
        "total_blocks": total_blocks,
        "completed_blocks": completed_blocks,
        "active_blocks": active_blocks,
        "blocks_with_no_tasks": blocks_with_no_tasks
    }
