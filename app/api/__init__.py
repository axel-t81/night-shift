"""
API Router Registration

This module combines all API route modules into a single router.
The main FastAPI application imports this router and includes it with the /api prefix.

Structure:
- /api/categories/* - Category endpoints
- /api/blocks/*     - Block endpoints  
- /api/tasks/*      - Task endpoints
"""

from fastapi import APIRouter

# Import route modules
# Each module contains an APIRouter with endpoints for a specific resource
from app.api.routes import categories, blocks, tasks, quotes


# Create the main API router
# This router will be included in the main FastAPI app with the /api prefix
api_router = APIRouter()


# Include the categories router
# All endpoints in categories.py will be prefixed with /categories
# Tags help organize the API documentation (Swagger UI)
api_router.include_router(
    categories.router,
    prefix="/categories",
    tags=["Categories"]
)


# Include the blocks router
# All endpoints in blocks.py will be prefixed with /blocks
api_router.include_router(
    blocks.router,
    prefix="/blocks",
    tags=["Blocks"]
)


# Include the tasks router
# All endpoints in tasks.py will be prefixed with /tasks
api_router.include_router(
    tasks.router,
    prefix="/tasks",
    tags=["Tasks"]
)

# Include the quotes router
api_router.include_router(
    quotes.router,
    prefix="/quotes",
    tags=["Quotes"]
)


# The final URL structure will be:
# /api/categories/*  (e.g., /api/categories, /api/categories/123)
# /api/blocks/*      (e.g., /api/blocks/456/complete-and-reset)
# /api/tasks/*       (e.g., /api/tasks, /api/tasks/789/complete)
# /api/quotes/*      (e.g., /api/quotes, /api/quotes/latest)

