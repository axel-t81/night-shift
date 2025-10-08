"""
Category Service

This service handles all business logic for categories/projects.
Categories are used to organize and classify tasks.

Functions:
- get_all_categories: List all categories
- get_category: Get a single category by ID
- create_category: Create a new category
- update_category: Update an existing category
- delete_category: Delete a category (fails if tasks exist)
- get_category_stats: Get statistics for a category (task count, completion rate)
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict
from datetime import datetime

from app.models.category import Category
from app.models.task import Task
from app.schemas.category import CategoryCreate, CategoryUpdate


def get_all_categories(db: Session, skip: int = 0, limit: int = 100) -> List[Category]:
    """
    Get all categories with optional pagination.
    
    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        
    Returns:
        List of Category objects
    """
    return db.query(Category).order_by(Category.name).offset(skip).limit(limit).all()


def get_category(db: Session, category_id: str) -> Optional[Category]:
    """
    Get a single category by ID.
    
    Args:
        db: Database session
        category_id: UUID string of the category
        
    Returns:
        Category object if found, None otherwise
    """
    return db.query(Category).filter(Category.id == category_id).first()


def create_category(db: Session, category: CategoryCreate) -> Category:
    """
    Create a new category.
    
    Args:
        db: Database session
        category: CategoryCreate schema with category data
        
    Returns:
        Newly created Category object
    """
    db_category = Category(
        name=category.name,
        color=category.color
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def update_category(db: Session, category_id: str, category_update: CategoryUpdate) -> Optional[Category]:
    """
    Update an existing category.
    
    Args:
        db: Database session
        category_id: UUID string of the category to update
        category_update: CategoryUpdate schema with fields to update
        
    Returns:
        Updated Category object if found, None otherwise
    """
    db_category = get_category(db, category_id)
    if not db_category:
        return None
    
    # Update only provided fields
    update_data = category_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db_category.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: str) -> bool:
    """
    Delete a category.
    
    Note: This will fail if any tasks reference this category due to
    RESTRICT constraint on the foreign key.
    
    Args:
        db: Database session
        category_id: UUID string of the category to delete
        
    Returns:
        True if deleted successfully, False if category not found
        
    Raises:
        IntegrityError: If tasks reference this category
    """
    db_category = get_category(db, category_id)
    if not db_category:
        return False
    
    db.delete(db_category)
    db.commit()
    return True


def get_category_stats(db: Session, category_id: str) -> Optional[Dict]:
    """
    Get statistics for a category.
    
    Args:
        db: Database session
        category_id: UUID string of the category
        
    Returns:
        Dictionary with stats:
        - total_tasks: Total number of tasks in this category
        - completed_tasks: Number of completed tasks
        - completion_rate: Percentage of completed tasks (0-100)
        - total_estimated_minutes: Sum of estimated minutes
        - total_actual_minutes: Sum of actual minutes for completed tasks
        
        Returns None if category doesn't exist
    """
    db_category = get_category(db, category_id)
    if not db_category:
        return None
    
    # Get task counts
    total_tasks = db.query(func.count(Task.id)).filter(Task.category_id == category_id).scalar()
    completed_tasks = db.query(func.count(Task.id)).filter(
        Task.category_id == category_id,
        Task.completed == True
    ).scalar()
    
    # Calculate completion rate
    completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
    
    # Get time estimates
    total_estimated = db.query(func.sum(Task.estimated_minutes)).filter(
        Task.category_id == category_id
    ).scalar() or 0
    
    total_actual = db.query(func.sum(Task.actual_minutes)).filter(
        Task.category_id == category_id,
        Task.completed == True,
        Task.actual_minutes.isnot(None)
    ).scalar() or 0
    
    return {
        "category_id": category_id,
        "category_name": db_category.name,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "completion_rate": round(completion_rate, 2),
        "total_estimated_minutes": total_estimated,
        "total_actual_minutes": total_actual
    }


def get_categories_with_task_counts(db: Session) -> List[Dict]:
    """
    Get all categories with their task counts.
    
    Args:
        db: Database session
        
    Returns:
        List of dictionaries with category info and task counts
    """
    categories = get_all_categories(db)
    result = []
    
    for category in categories:
        total_tasks = db.query(func.count(Task.id)).filter(Task.category_id == category.id).scalar()
        completed_tasks = db.query(func.count(Task.id)).filter(
            Task.category_id == category.id,
            Task.completed == True
        ).scalar()
        
        result.append({
            "id": category.id,
            "name": category.name,
            "color": category.color,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "created_at": category.created_at,
            "updated_at": category.updated_at
        })
    
    return result
