from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging
import time
from typing import Dict, Any

from app.config.settings import settings
from app.api import api_router
from app.database.connection import db_manager

logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def create_application() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        description=settings.api_description,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        debug=settings.debug
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]
    )
    
    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        return response
    
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        
        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.4f}s"
        )
        return response
    
    app.include_router(api_router, prefix="/api/v1")
    
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        logger.error(f"Validation Error: {exc.errors()}")
        return JSONResponse(
            status_code=422,
            content={"detail": "Validation error", "errors": exc.errors()}
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled Exception: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    
    @app.get("/", tags=["root"])
    async def root():
        """Root endpoint."""
        return {
            "message": "FileDrive API",
            "version": settings.api_version,
            "docs": "/docs",
            "health": "/health"
        }
    
    @app.get("/health", tags=["health"])
    async def health_check():
        """Health check endpoint."""
        try:
            db_status = await db_manager.health_check()
            
            health_status = {
                "status": "healthy" if db_status["overall"]["healthy"] else "degraded",
                "timestamp": time.time(),
                "version": settings.api_version,
                "services": {
                    "mongodb": db_status["mongodb"]["status"],
                    "minio": db_status["minio"]["status"]
                }
            }
            
            status_code = 200 if db_status["overall"]["healthy"] else 503
            return JSONResponse(content=health_status, status_code=status_code)
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return JSONResponse(
                content={
                    "status": "unhealthy",
                    "timestamp": time.time(),
                    "version": settings.api_version,
                    "error": str(e)
                },
                status_code=503
            )
    
    @app.on_event("startup")
    async def startup_event():
        """Initialize database connections on startup."""
        logger.info("🚀 Starting up FileDrive API...")
        
        try:
            if settings.db_retry_enabled:
                logger.info(f"🔄 Using retry mechanism (max: {settings.db_max_retries}, delay: {settings.db_retry_delay}s)")
                results = await db_manager.connect_with_retry(
                    max_retries=settings.db_max_retries,
                    initial_delay=settings.db_retry_delay
                )
                mongodb_success = results["mongodb"]["success"]
                minio_success = results["minio"]["success"]
                
                if not mongodb_success:
                    logger.error(f"MongoDB connection failed: {results['mongodb'].get('error', 'Unknown error')}")
                if not minio_success:
                    logger.error(f"MinIO connection failed: {results['minio'].get('error', 'Unknown error')}")
            else:
                mongodb_success = await db_manager.connect_to_mongodb()
                minio_success = db_manager.connect_to_minio()
            
            if mongodb_success and minio_success:
                logger.info("🎉 Successfully connected to all services")
            elif mongodb_success or minio_success:
                connected_services = []
                if mongodb_success:
                    connected_services.append("MongoDB")
                if minio_success:
                    connected_services.append("MinIO")
                logger.info(f"✅ Partially connected - Available services: {', '.join(connected_services)}")
            else:
                logger.warning("⚠️  No database services available - API will run with limited functionality")
            
            # Verify connections are working
            health_status = await db_manager.health_check()
            logger.info(f"Health check after startup: {health_status}")
            
        except Exception as e:
            logger.error(f"❌ Startup failed: {e}")
            raise
        
        logger.info("🌟 FileDrive API is ready to serve requests")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Clean up database connections on shutdown."""
        logger.info("Shutting down FileDrive API...")
        
        try:
            await db_manager.close_connections()
            logger.info("Successfully closed database connections")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    return app


app = create_application() 