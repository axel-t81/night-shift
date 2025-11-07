"""
Category API Routes

This module contains all API endpoints for managing categories (projects).
Categories are used to organize tasks by project or topic.

Endpoints:
- GET    /api/categories              - List all categories
- GET    /api/categories/{id}         - Get single category
- POST   /api/categories              - Create new category
- PUT    /api/categories/{id}         - Update category
- DELETE /api/categories/{id}         - Delete category
- GET    /api/categories/{id}/stats   - Get category statistics
- GET    /api/categories/with-tasks   - List categories with task counts
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List

# Import database dependency
from app.database import get_db

# Import schemas for request/response validation
from app.schemas.category import Category, CategoryCreate, CategoryUpdate

# Import service layer for business logic
from app.services import category_service


# Create router for category endpoints
router = APIRouter()


@router.get("", response_model=List[Category])
def list_categories(
    skip: int = Query(0, ge=0, description="Number of records to skip for pagination"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: Session = Depends(get_db)
):
    """
    List all categories with optional pagination.
    
    This endpoint returns all categories ordered by name.
    
    Query Parameters:
    - skip: Number of records to skip (for pagination)
    - limit: Maximum number of records to return (1-1000)
    
    Returns:
    - List of Category objects with id, name, color, timestamps
    
    Example Response:
    ```json
    [
        {
            "id": "uuid-123",
            "name": "Deep Work",
            "color": "#1E90FF",
            "created_at": "2024-01-15T10:30:00",
            "updated_at": "2024-01-15T10:30:00"
        }
    ]
    ```
    """
    # Call service layer to get categories
    categories = category_service.get_all_categories(db, skip=skip, limit=limit)
    return categories


@router.get("/with-tasks", response_model=List[dict])
def list_categories_with_tasks(
    db: Session = Depends(get_db)
):
    """
    List all categories with task count information.
    
    This endpoint returns categories along with:
    - Total number of tasks in each category
    - Number of completed tasks in each category
    
    Useful for dashboard views and statistics.
    
    Returns:
    - List of dictionaries with category info and task counts
    
    Example Response:
    ```json
    [
        {
            "id": "uuid-123",
            "name": "Deep Work",
            "color": "#1E90FF",
            "total_tasks": 15,
            "completed_tasks": 8,
            "created_at": "2024-01-15T10:30:00",
            "updated_at": "2024-01-15T10:30:00"
        }
    ]
    ```
    """
    # Call service layer to get categories with task counts
    categories_with_tasks = category_service.get_categories_with_task_counts(db)
    return categories_with_tasks


@router.get("/{category_id}", response_model=Category)
def get_category(
    category_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a single category by ID.
    
    Path Parameters:
    - category_id: UUID string of the category
    
    Returns:
    - Category object with all fields
    
    Raises:
    - 404: Category not found
    """
    # Call service layer to get the category
    category = category_service.get_category(db, category_id)
    
    # If category doesn't exist, return 404 error
    if not category:
        raise HTTPException(
            status_code=404,
            detail=f"Category with id '{category_id}' not found"
        )
    
    return category


@router.post("", response_model=Category, status_code=201)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new category.
    
    Request Body:
    - name: Category name (required, 1-100 characters)
    - color: Hex color code (optional, format: #RRGGBB or #RGB)
    
    Returns:
    - Newly created Category object with generated id and timestamps
    
    Example Request:
    ```json
    {
        "name": "Deep Work",
        "color": "#1E90FF"
    }
    ```
    
    Example Response:
    ```json
    {
        "id": "generated-uuid",
        "name": "Deep Work",
        "color": "#1E90FF",
        "created_at": "2024-01-15T10:30:00",
        "updated_at": "2024-01-15T10:30:00"
    }
    ```
    """
    # Call service layer to create the category
    # Service handles UUID generation and timestamp creation
    new_category = category_service.create_category(db, category)
    return new_category


@router.put("/{category_id}", response_model=Category)
def update_category(
    category_id: str,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing category.
    
    Path Parameters:
    - category_id: UUID string of the category to update
    
    Request Body (all fields optional):
    - name: New category name
    - color: New hex color code
    
    Only provided fields will be updated. Omitted fields remain unchanged.
    
    Returns:
    - Updated Category object
    
    Raises:
    - 404: Category not found
    
    Example Request (partial update):
    ```json
    {
        "color": "#FF6347"
    }
    ```
    """
    # Call service layer to update the category
    updated_category = category_service.update_category(db, category_id, category_update)
    
    # If category doesn't exist, return 404 error
    if not updated_category:
        raise HTTPException(
            status_code=404,
            detail=f"Category with id '{category_id}' not found"
        )
    
    return updated_category


@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a category.
    
    Path Parameters:
    - category_id: UUID string of the category to delete
    
    Important: This will fail if any tasks reference this category due to
    the RESTRICT foreign key constraint. You must delete or reassign all
    tasks in this category before deleting the category.
    
    Returns:
    - 204 No Content on success
    
    Raises:
    - 404: Category not found
    - 400: Cannot delete category because tasks reference it
    """
    try:
        # Call service layer to delete the category
        deleted = category_service.delete_category(db, category_id)
        
        # If category doesn't exist, return 404 error
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"Category with id '{category_id}' not found"
            )
        
        # Return 204 No Content (successful deletion with no response body)
        return None
    
    except IntegrityError:
        # Foreign key constraint violation - tasks still reference this category
        raise HTTPException(
            status_code=400,
            detail="Cannot delete category because tasks still reference it. Delete or reassign tasks first."
        )


@router.get("/{category_id}/stats", response_model=dict)
def get_category_statistics(
    category_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed statistics for a category.
    
    Path Parameters:
    - category_id: UUID string of the category
    
    Returns:
    - Dictionary with comprehensive category statistics:
      - category_id: The category UUID
      - category_name: The category name
      - total_tasks: Total number of tasks in this category
      - completed_tasks: Number of completed tasks
      - completion_rate: Percentage of completed tasks (0-100)
      - total_estimated_minutes: Sum of all estimated minutes
      - total_actual_minutes: Sum of actual minutes for completed tasks
    
    Useful for:
    - Dashboard displays
    - Progress tracking
    - Time estimation analysis
    
    Raises:
    - 404: Category not found
    
    Example Response:
    ```json
    {
        "category_id": "uuid-123",
        "category_name": "Deep Work",
        "total_tasks": 20,
        "completed_tasks": 12,
        "completion_rate": 60.0,
        "total_estimated_minutes": 900,
        "total_actual_minutes": 950
    }
    ```
    """
    # Call service layer to get category statistics
    stats = category_service.get_category_stats(db, category_id)
    
    # If category doesn't exist, return 404 error
    if not stats:
        raise HTTPException(
            status_code=404,
            detail=f"Category with id '{category_id}' not found"
        )
    
    return stats

