"""
Night Shift App - Main FastAPI Application

This is the main entry point for the FastAPI backend. It sets up:
- The FastAPI application with metadata
- CORS middleware for frontend communication
- All API routes
- Static file serving for frontend assets
- HTML template serving

To run the app:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os

# Import the main API router that combines all route modules
from app.api import api_router

# Import database setup to ensure tables are created
from app.database import engine, Base
from app.models import block, category, task, quote  # Import models to register them with Base


# Create database tables if they don't exist
# This is useful for development, but in production you'd use migrations (Alembic)
# Base.metadata.create_all(bind=engine) # This line is removed as per the edit hint


# Initialize FastAPI application with metadata
app = FastAPI(
    title="Night Shift App",
    description="A personal productivity web app for tracking night shift pomodoro blocks and tasks",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI at /docs
    redoc_url="/redoc"  # ReDoc at /redoc
)


# Configure CORS (Cross-Origin Resource Sharing)
# This allows the frontend to make requests to the API from different origins
# For development, we allow all origins. In production, restrict this to your domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: ["https://yourdomain.com"]
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allow all headers
)


# Register all API routes with /api prefix
# This includes routes for blocks, categories, and tasks
app.include_router(api_router, prefix="/api")


# Root endpoint - returns a welcome message
@app.get("/", tags=["Root"])
def read_root():
    """
    Root endpoint that returns basic app information.
    
    This is useful for:
    - Health checks
    - Verifying the API is running
    - Getting basic app metadata
    """
    return {
        "message": "Welcome to Night Shift App API",
        "version": "1.0.0",
        "docs": "/docs",
        "api_prefix": "/api"
    }


# Health check endpoint
@app.get("/health", tags=["Root"])
def health_check():
    """
    Health check endpoint for monitoring and deployment systems.
    
    Returns a simple status to confirm the API is running.
    Used by Cloud Run, Kubernetes, or other deployment platforms.
    """
    return {"status": "healthy"}


# Mount static files (CSS, JavaScript, images)
# This serves files from the /static directory
# Example: /static/css/styles.css will serve the styles.css file
static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")


# Serve the main HTML page (frontend)
# This serves the index.html file from the /templates directory
@app.get("/app", tags=["Frontend"])
def serve_frontend():
    """
    Serve the main frontend HTML page.
    
    This endpoint serves the single-page application (SPA) that users interact with.
    The frontend will make API calls to the /api/* endpoints.
    """
    templates_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
    index_path = os.path.join(templates_path, "index.html")
    
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        return {"error": "Frontend not found. Make sure index.html exists in /templates"}


# Optional: Catch-all route for SPA (Single Page Application) routing
# This ensures that frontend routes (like /app/blocks, /app/tasks) work correctly
# Uncomment if you need SPA routing support
# @app.get("/{full_path:path}", tags=["Frontend"])
# def catch_all(full_path: str):
#     """
#     Catch-all route for SPA routing.
#     Serves index.html for any unmatched routes to support frontend routing.
#     """
#     templates_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
#     index_path = os.path.join(templates_path, "index.html")
#     
#     if os.path.exists(index_path):
#         return FileResponse(index_path)
#     else:
#         return {"error": "Not found"}


# Application startup event
@app.on_event("startup")
async def startup_event():
    """
    Run tasks when the application starts.
    
    This is useful for:
    - Database connection verification
    - Loading configuration
    - Initializing caches
    - Logging startup information
    """
    print("🚀 Night Shift App API is starting...")
    print("📚 API Documentation available at /docs")
    print("🔄 API endpoints available at /api/*")


# Application shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Run cleanup tasks when the application shuts down.
    
    This is useful for:
    - Closing database connections
    - Cleaning up resources
    - Logging shutdown information
    """
    print("👋 Night Shift App API is shutting down...")


# For running with: python -m app.main
if __name__ == "__main__":
    import uvicorn
    
    # Run the application with uvicorn
    # Host 0.0.0.0 allows access from other machines (useful for Docker/Cloud Run)
    # Port 8000 is the default FastAPI port
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Auto-reload on code changes (development only)
    )

