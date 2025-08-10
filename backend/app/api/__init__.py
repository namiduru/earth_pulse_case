from fastapi import APIRouter
from app.api import files

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(files.router) 