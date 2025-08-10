"""
Database connection management for MongoDB and MinIO.

This module provides connection management, health checks, and retry mechanisms
for both MongoDB and MinIO storage systems.
"""

import asyncio
import logging
import time
from typing import Optional, Dict, Any

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from minio import Minio
from minio.error import S3Error

from app.config.settings import settings

logger = logging.getLogger(__name__)


class DatabaseConnectionError(Exception):
    """Custom exception for database connection errors."""
    pass


class DatabaseManager:
    """
    Database connection manager for MongoDB and MinIO.
    
    This class manages connections to both MongoDB and MinIO, providing
    connection pooling, health checks, and retry mechanisms.
    """
    
    def __init__(self):
        """Initialize the database manager."""
        self._mongodb_client: Optional[AsyncIOMotorClient] = None
        self._minio_client: Optional[Minio] = None
        self._database: Optional[AsyncIOMotorDatabase] = None
        self._files_collection: Optional[AsyncIOMotorCollection] = None
        self._mongodb_connected: bool = False
        self._minio_connected: bool = False
    
    async def connect_to_mongodb(self) -> bool:
        """
        Connect to MongoDB with connection pooling and configuration.
        
        Returns:
            bool: True if connection successful, False otherwise
            
        Raises:
            DatabaseConnectionError: If connection fails after retries
        """
        try:
            logger.info("🔌 Attempting to connect to MongoDB...")
            
            self._mongodb_client = AsyncIOMotorClient(
                settings.mongodb_url,
                maxPoolSize=settings.mongodb_max_pool_size,
                minPoolSize=settings.mongodb_min_pool_size,
                maxIdleTimeMS=settings.mongodb_max_idle_time_ms,
                serverSelectionTimeoutMS=settings.mongodb_server_selection_timeout_ms,
                connectTimeoutMS=settings.mongodb_connect_timeout_ms,
                socketTimeoutMS=settings.mongodb_socket_timeout_ms
            )
            
            # Test the connection
            await self._mongodb_client.admin.command('ping')
            
            # Set up database and collection
            self._database = self._mongodb_client[settings.mongodb_database]
            self._files_collection = self._database.files
            
            self._mongodb_connected = True
            logger.info("✅ Successfully connected to MongoDB")
            return True
            
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {str(e)}")
            self._cleanup_mongodb()
            return False
    
    def connect_to_minio(self) -> bool:
        """
        Connect to MinIO with bucket validation and creation.
        
        Returns:
            bool: True if connection successful, False otherwise
            
        Raises:
            DatabaseConnectionError: If connection fails after retries
        """
        try:
            logger.info("🔌 Attempting to connect to MinIO...")
            
            self._minio_client = Minio(
                settings.minio_endpoint,
                access_key=settings.minio_access_key,
                secret_key=settings.minio_secret_key_value,
                secure=settings.minio_secure,
                region=settings.minio_region
            )
            
            # Test connection and ensure bucket exists
            self._ensure_minio_bucket_exists()
            
            self._minio_connected = True
            logger.info("✅ Successfully connected to MinIO")
            return True
            
        except Exception as e:
            logger.error(f"❌ MinIO connection failed: {str(e)}")
            self._cleanup_minio()
            return False
    
    def _ensure_minio_bucket_exists(self) -> None:
        """Ensure the required MinIO bucket exists, create if necessary."""
        try:
            buckets = self._minio_client.list_buckets()
            bucket_names = [bucket.name for bucket in buckets]
            
            if settings.minio_bucket not in bucket_names:
                logger.info(f"📁 Creating MinIO bucket: {settings.minio_bucket}")
                self._minio_client.make_bucket(settings.minio_bucket)
                logger.info(f"✅ MinIO bucket created: {settings.minio_bucket}")
            else:
                logger.info(f"📁 MinIO bucket already exists: {settings.minio_bucket}")
                
        except S3Error as e:
            if e.code == "BucketAlreadyOwnedByYou":
                logger.info(f"📁 MinIO bucket already exists: {settings.minio_bucket}")
            else:
                raise DatabaseConnectionError(f"Failed to ensure MinIO bucket exists: {e}")
    
    def _cleanup_mongodb(self) -> None:
        """Clean up MongoDB connection resources."""
        self._mongodb_connected = False
        self._mongodb_client = None
        self._database = None
        self._files_collection = None
    
    def _cleanup_minio(self) -> None:
        """Clean up MinIO connection resources."""
        self._minio_connected = False
        self._minio_client = None
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health checks for all database connections.
        
        Returns:
            Dict containing health status for each database
        """
        health_status = {
            "mongodb": {
                "connected": False,
                "status": "disconnected",
                "error": None
            },
            "minio": {
                "connected": False,
                "status": "disconnected",
                "error": None
            },
            "overall": {
                "healthy": False,
                "status": "unhealthy"
            }
        }
        
        # Check MongoDB health
        if self._mongodb_connected and self._mongodb_client is not None:
            try:
                await self._mongodb_client.admin.command('ping')
                health_status["mongodb"]["connected"] = True
                health_status["mongodb"]["status"] = "healthy"
            except Exception as e:
                logger.warning(f"MongoDB health check failed: {e}")
                health_status["mongodb"]["error"] = str(e)
                self._cleanup_mongodb()
        
        # Check MinIO health
        if self._minio_connected and self._minio_client is not None:
            try:
                self._minio_client.list_buckets()
                health_status["minio"]["connected"] = True
                health_status["minio"]["status"] = "healthy"
            except Exception as e:
                logger.warning(f"MinIO health check failed: {e}")
                health_status["minio"]["error"] = str(e)
                self._cleanup_minio()
        
        # Determine overall health
        overall_healthy = (
            health_status["mongodb"]["connected"] or 
            health_status["minio"]["connected"]
        )
        health_status["overall"]["healthy"] = overall_healthy
        health_status["overall"]["status"] = "healthy" if overall_healthy else "unhealthy"
        
        return health_status
    
    async def connect_with_retry(
        self, 
        max_retries: Optional[int] = None, 
        initial_delay: Optional[float] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Attempt to connect to databases with exponential backoff retry mechanism.
        
        Args:
            max_retries: Maximum number of retry attempts (uses settings if None)
            initial_delay: Initial delay between retries in seconds (uses settings if None)
            
        Returns:
            Dict containing connection results for each database
        """
        max_retries = max_retries or settings.db_max_retries
        initial_delay = initial_delay or settings.db_retry_delay
        
        results = {
            "mongodb": {"success": False, "attempts": 0, "error": None},
            "minio": {"success": False, "attempts": 0, "error": None}
        }
        
        # Connect to MongoDB with retries
        for attempt in range(max_retries):
            results["mongodb"]["attempts"] = attempt + 1
            
            if attempt > 0:
                delay = initial_delay * (2 ** (attempt - 1))
                logger.info(f"🔄 Retrying MongoDB connection (attempt {attempt + 1}/{max_retries}) in {delay:.1f}s...")
                await asyncio.sleep(delay)
            
            try:
                if await self.connect_to_mongodb():
                    results["mongodb"]["success"] = True
                    break
            except Exception as e:
                results["mongodb"]["error"] = str(e)
                if attempt == max_retries - 1:
                    logger.error(f"Failed to connect to MongoDB after {max_retries} attempts")
        
        # Connect to MinIO with retries
        for attempt in range(max_retries):
            results["minio"]["attempts"] = attempt + 1
            
            if attempt > 0:
                delay = initial_delay * (2 ** (attempt - 1))
                logger.info(f"🔄 Retrying MinIO connection (attempt {attempt + 1}/{max_retries}) in {delay:.1f}s...")
                time.sleep(delay)
            
            try:
                if self.connect_to_minio():
                    results["minio"]["success"] = True
                    break
            except Exception as e:
                results["minio"]["error"] = str(e)
                if attempt == max_retries - 1:
                    logger.error(f"Failed to connect to MinIO after {max_retries} attempts")
        
        return results
    
    async def close_connections(self) -> None:
        """Close all database connections."""
        logger.info("🔌 Closing database connections...")
        
        if self._mongodb_connected and self._mongodb_client is not None:
            self._mongodb_client.close()
            self._cleanup_mongodb()
            logger.info("✅ MongoDB connection closed")
        
        if self._minio_connected and self._minio_client is not None:
            # MinIO client doesn't have a close method, just cleanup
            self._cleanup_minio()
            logger.info("✅ MinIO connection closed")
    
    # ============================================================================
    # Property getters with proper error handling
    # ============================================================================
    
    @property
    def mongodb_client(self) -> AsyncIOMotorClient:
        """Get MongoDB client with connection validation."""
        if not self._mongodb_connected or self._mongodb_client is None:
            raise DatabaseConnectionError("MongoDB is not connected")
        return self._mongodb_client
    
    @property
    def minio_client(self) -> Minio:
        """Get MinIO client with connection validation."""
        if not self._minio_connected or self._minio_client is None:
            raise DatabaseConnectionError("MinIO is not connected")
        return self._minio_client
    
    @property
    def database(self) -> AsyncIOMotorDatabase:
        """Get MongoDB database with connection validation."""
        if not self._mongodb_connected or self._database is None:
            raise DatabaseConnectionError("MongoDB is not connected")
        return self._database
    
    @property
    def files_collection(self) -> AsyncIOMotorCollection:
        """Get files collection with connection validation."""
        if not self._mongodb_connected or self._files_collection is None:
            raise DatabaseConnectionError("MongoDB is not connected")
        return self._files_collection
    
    @property
    def is_mongodb_connected(self) -> bool:
        """Check if MongoDB is connected."""
        return self._mongodb_connected
    
    @property
    def is_minio_connected(self) -> bool:
        """Check if MinIO is connected."""
        return self._minio_connected
    
    @property
    def is_connected(self) -> bool:
        """Check if any database is connected."""
        return self._mongodb_connected or self._minio_connected


# ============================================================================
# Global database manager instance
# ============================================================================

db_manager = DatabaseManager()


# ============================================================================
# FastAPI dependency functions
# ============================================================================

async def get_database_manager() -> DatabaseManager:
    """
    FastAPI dependency to get the database manager.
    
    Returns:
        DatabaseManager: The global database manager instance
    """
    return db_manager


 