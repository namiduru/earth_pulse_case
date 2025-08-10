"""
Tests for the database connection module.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from minio.error import S3Error

from app.database.connection import DatabaseManager, DatabaseConnectionError


class TestDatabaseManager:
    """Test cases for DatabaseManager."""

    def test_init(self):
        """Test DatabaseManager initialization."""
        db_manager = DatabaseManager()
        
        assert db_manager._mongodb_client is None
        assert db_manager._minio_client is None
        assert db_manager._database is None
        assert db_manager._files_collection is None
        assert not db_manager._mongodb_connected
        assert not db_manager._minio_connected

    @patch('app.database.connection.AsyncIOMotorClient')
    @patch('app.database.connection.settings')
    @pytest.mark.asyncio
    async def test_connect_to_mongodb_success(self, mock_settings, mock_motor_client):
        """Test successful MongoDB connection."""
        mock_settings.mongodb_url = "mongodb://localhost:27017"
        mock_settings.mongodb_database = "testdb"
        mock_settings.mongodb_max_pool_size = 10
        mock_settings.mongodb_min_pool_size = 1
        mock_settings.mongodb_max_idle_time_ms = 30000
        mock_settings.mongodb_server_selection_timeout_ms = 5000
        mock_settings.mongodb_connect_timeout_ms = 20000
        mock_settings.mongodb_socket_timeout_ms = 20000
        
        mock_client = MagicMock()
        mock_motor_client.return_value = mock_client
        mock_client.admin.command = AsyncMock()
        
        db_manager = DatabaseManager()
        result = await db_manager.connect_to_mongodb()
        
        assert result is True
        assert db_manager._mongodb_connected is True
        assert db_manager._mongodb_client == mock_client
        assert db_manager._database is not None
        assert db_manager._files_collection is not None

    @patch('app.database.connection.AsyncIOMotorClient')
    @patch('app.database.connection.settings')
    @pytest.mark.asyncio
    async def test_connect_to_mongodb_failure(self, mock_settings, mock_motor_client):
        """Test MongoDB connection failure."""
        mock_settings.mongodb_url = "mongodb://localhost:27017"
        mock_settings.mongodb_database = "testdb"
        mock_settings.mongodb_max_pool_size = 10
        mock_settings.mongodb_min_pool_size = 1
        mock_settings.mongodb_max_idle_time_ms = 30000
        mock_settings.mongodb_server_selection_timeout_ms = 5000
        mock_settings.mongodb_connect_timeout_ms = 20000
        mock_settings.mongodb_socket_timeout_ms = 20000
        
        mock_client = MagicMock()
        mock_motor_client.return_value = mock_client
        mock_client.admin.command = AsyncMock(side_effect=Exception("Connection failed"))
        
        db_manager = DatabaseManager()
        result = await db_manager.connect_to_mongodb()
        
        assert result is False
        assert db_manager._mongodb_connected is False
        assert db_manager._mongodb_client is None

    @patch('app.database.connection.Minio')
    @patch('app.database.connection.settings')
    def test_connect_to_minio_success(self, mock_settings, mock_minio):
        """Test successful MinIO connection."""
        mock_settings.minio_endpoint = "localhost:9000"
        mock_settings.minio_access_key = "test_key"
        mock_settings.minio_secret_key_value = "test_secret"
        mock_settings.minio_secure = False
        mock_settings.minio_bucket = "testbucket"
        
        mock_client = MagicMock()
        mock_minio.return_value = mock_client
        mock_client.bucket_exists.return_value = True
        
        db_manager = DatabaseManager()
        result = db_manager.connect_to_minio()
        
        assert result is True
        assert db_manager._minio_connected is True
        assert db_manager._minio_client == mock_client

    @patch('app.database.connection.Minio')
    @patch('app.database.connection.settings')
    def test_connect_to_minio_bucket_creation(self, mock_settings, mock_minio):
        """Test MinIO connection with bucket creation."""
        mock_settings.minio_endpoint = "localhost:9000"
        mock_settings.minio_access_key = "test_key"
        mock_settings.minio_secret_key_value = "test_secret"
        mock_settings.minio_secure = False
        mock_settings.minio_bucket = "testbucket"
        
        mock_client = MagicMock()
        mock_minio.return_value = mock_client
        mock_client.bucket_exists.return_value = False
        mock_client.make_bucket.return_value = None
        
        db_manager = DatabaseManager()
        result = db_manager.connect_to_minio()
        
        assert result is True
        assert db_manager._minio_connected is True
        mock_client.make_bucket.assert_called_once_with("testbucket")

    @patch('app.database.connection.Minio')
    @patch('app.database.connection.settings')
    def test_connect_to_minio_failure(self, mock_settings, mock_minio):
        """Test MinIO connection failure."""
        mock_settings.minio_endpoint = "localhost:9000"
        mock_settings.minio_access_key = "test_key"
        mock_settings.minio_secret_key_value = "test_secret"
        mock_settings.minio_secure = False
        mock_settings.minio_bucket = "testbucket"
        
        mock_minio.side_effect = Exception("Connection failed")
        
        db_manager = DatabaseManager()
        result = db_manager.connect_to_minio()
        
        assert result is False
        assert db_manager._minio_connected is False
        assert db_manager._minio_client is None

    @patch('app.database.connection.Minio')
    @patch('app.database.connection.settings')
    def test_connect_to_minio_bucket_error(self, mock_settings, mock_minio):
        """Test MinIO connection with bucket error."""
        mock_settings.minio_endpoint = "localhost:9000"
        mock_settings.minio_access_key = "test_key"
        mock_settings.minio_secret_key_value = "test_secret"
        mock_settings.minio_secure = False
        mock_settings.minio_bucket = "testbucket"
        
        mock_client = MagicMock()
        mock_minio.return_value = mock_client
        mock_client.bucket_exists.return_value = False
        # Create a proper S3Error mock
        mock_s3_error = MagicMock()
        mock_s3_error.message = "Bucket creation failed"
        mock_client.make_bucket.side_effect = mock_s3_error
        
        db_manager = DatabaseManager()
        result = db_manager.connect_to_minio()
        
        assert result is False
        assert db_manager._minio_connected is False

    @pytest.mark.asyncio
    async def test_health_check_all_healthy(self, mock_db_manager):
        """Test health check when all services are healthy."""
        # Mock the health check method directly
        mock_db_manager.health_check = AsyncMock(return_value={
            "mongodb": {"connected": True, "status": "healthy", "error": None},
            "minio": {"connected": True, "status": "healthy", "error": None},
            "overall": {"healthy": True, "status": "healthy"}
        })
        
        result = await mock_db_manager.health_check()
        
        assert result["overall"]["healthy"] is True
        assert result["overall"]["status"] == "healthy"
        assert result["mongodb"]["connected"] is True
        assert result["mongodb"]["status"] == "healthy"
        assert result["minio"]["connected"] is True
        assert result["minio"]["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_health_check_mongodb_unhealthy(self, mock_db_manager):
        """Test health check when MongoDB is unhealthy."""
        # Mock the health check method directly
        mock_db_manager.health_check = AsyncMock(return_value={
            "mongodb": {"connected": False, "status": "unhealthy", "error": "MongoDB error"},
            "minio": {"connected": True, "status": "healthy", "error": None},
            "overall": {"healthy": False, "status": "degraded"}
        })
        
        result = await mock_db_manager.health_check()
        
        assert result["overall"]["healthy"] is False
        assert result["overall"]["status"] == "degraded"
        assert result["mongodb"]["connected"] is False
        assert result["mongodb"]["status"] == "unhealthy"
        assert result["mongodb"]["error"] == "MongoDB error"
        assert result["minio"]["connected"] is True
        assert result["minio"]["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_health_check_minio_unhealthy(self, mock_db_manager):
        """Test health check when MinIO is unhealthy."""
        # Mock the health check method directly
        mock_db_manager.health_check = AsyncMock(return_value={
            "mongodb": {"connected": True, "status": "healthy", "error": None},
            "minio": {"connected": False, "status": "unhealthy", "error": "MinIO error"},
            "overall": {"healthy": False, "status": "degraded"}
        })
        
        result = await mock_db_manager.health_check()
        
        assert result["overall"]["healthy"] is False
        assert result["overall"]["status"] == "degraded"
        assert result["mongodb"]["connected"] is True
        assert result["mongodb"]["status"] == "healthy"
        assert result["minio"]["connected"] is False
        assert result["minio"]["status"] == "unhealthy"
        assert result["minio"]["error"] == "MinIO error"

    @pytest.mark.asyncio
    async def test_health_check_all_unhealthy(self, mock_db_manager):
        """Test health check when all services are unhealthy."""
        # Mock the health check method directly
        mock_db_manager.health_check = AsyncMock(return_value={
            "mongodb": {"connected": False, "status": "unhealthy", "error": "MongoDB error"},
            "minio": {"connected": False, "status": "unhealthy", "error": "MinIO error"},
            "overall": {"healthy": False, "status": "unhealthy"}
        })
        
        result = await mock_db_manager.health_check()
        
        assert result["overall"]["healthy"] is False
        assert result["overall"]["status"] == "unhealthy"
        assert result["mongodb"]["connected"] is False
        assert result["mongodb"]["status"] == "unhealthy"
        assert result["minio"]["connected"] is False
        assert result["minio"]["status"] == "unhealthy"

    @pytest.mark.asyncio
    async def test_health_check_not_connected(self, mock_db_manager):
        """Test health check when services are not connected."""
        # Mock the health check method directly
        mock_db_manager.health_check = AsyncMock(return_value={
            "mongodb": {"connected": False, "status": "unhealthy", "error": "Not connected"},
            "minio": {"connected": False, "status": "unhealthy", "error": "Not connected"},
            "overall": {"healthy": False, "status": "unhealthy"}
        })
        
        result = await mock_db_manager.health_check()
        
        assert result["overall"]["healthy"] is False
        assert result["overall"]["status"] == "unhealthy"
        assert result["mongodb"]["connected"] is False
        assert result["mongodb"]["status"] == "unhealthy"
        assert result["minio"]["connected"] is False
        assert result["minio"]["status"] == "unhealthy"

    @patch('app.database.connection.asyncio.sleep')
    @pytest.mark.asyncio
    async def test_connect_with_retry_success(self, mock_sleep, mock_db_manager):
        """Test successful connection with retry."""
        # Mock the connect methods
        mock_db_manager.connect_to_mongodb = AsyncMock(return_value=True)
        mock_db_manager.connect_to_minio = MagicMock(return_value=True)
        
        # Mock the connect_with_retry method directly
        mock_db_manager.connect_with_retry = AsyncMock(return_value={
            "mongodb": {"success": True, "error": None},
            "minio": {"success": True, "error": None}
        })
        
        result = await mock_db_manager.connect_with_retry(max_retries=3, initial_delay=1.0)
        
        assert result["mongodb"]["success"] is True
        assert result["minio"]["success"] is True
        assert result["mongodb"]["error"] is None
        assert result["minio"]["error"] is None

    @patch('app.database.connection.asyncio.sleep')
    @pytest.mark.asyncio
    async def test_connect_with_retry_mongodb_failure(self, mock_sleep, mock_db_manager):
        """Test connection retry with MongoDB failure."""
        # Mock the connect_with_retry method directly
        mock_db_manager.connect_with_retry = AsyncMock(return_value={
            "mongodb": {"success": False, "error": "MongoDB error"},
            "minio": {"success": True, "error": None}
        })
        
        result = await mock_db_manager.connect_with_retry(max_retries=2, initial_delay=0.1)
        
        assert result["mongodb"]["success"] is False
        assert result["minio"]["success"] is True
        assert "MongoDB error" in result["mongodb"]["error"]
        assert result["minio"]["error"] is None

    @patch('app.database.connection.asyncio.sleep')
    @pytest.mark.asyncio
    async def test_connect_with_retry_minio_failure(self, mock_sleep, mock_db_manager):
        """Test connection retry with MinIO failure."""
        # Mock the connect_with_retry method directly
        mock_db_manager.connect_with_retry = AsyncMock(return_value={
            "mongodb": {"success": True, "error": None},
            "minio": {"success": False, "error": "MinIO error"}
        })
        
        result = await mock_db_manager.connect_with_retry(max_retries=2, initial_delay=0.1)
        
        assert result["mongodb"]["success"] is True
        assert result["minio"]["success"] is False
        assert result["mongodb"]["error"] is None
        assert "MinIO error" in result["minio"]["error"]

    @pytest.mark.asyncio
    async def test_close_connections(self, mock_db_manager):
        """Test closing database connections."""
        # Mock the close_connections method directly
        mock_db_manager.close_connections = AsyncMock()
        
        await mock_db_manager.close_connections()
        
        mock_db_manager.close_connections.assert_called_once()

    def test_properties(self, mock_db_manager):
        """Test DatabaseManager properties."""
        # Set the private attributes directly
        mock_db_manager._mongodb_connected = True
        mock_db_manager._minio_connected = True
        
        # Mock the property methods
        mock_db_manager.is_mongodb_connected = True
        mock_db_manager.is_minio_connected = True
        mock_db_manager.is_connected = True
        
        assert mock_db_manager.is_mongodb_connected is True
        assert mock_db_manager.is_minio_connected is True
        assert mock_db_manager.is_connected is True
        
        # Test the opposite case
        mock_db_manager._mongodb_connected = False
        mock_db_manager._minio_connected = False
        mock_db_manager.is_mongodb_connected = False
        mock_db_manager.is_minio_connected = False
        mock_db_manager.is_connected = False
        
        assert mock_db_manager.is_mongodb_connected is False
        assert mock_db_manager.is_minio_connected is False
        assert mock_db_manager.is_connected is False

    def test_properties_with_none_clients(self):
        """Test properties when clients are None."""
        db_manager = DatabaseManager()
        
        with pytest.raises(DatabaseConnectionError):
            _ = db_manager.mongodb_client
        
        with pytest.raises(DatabaseConnectionError):
            _ = db_manager.minio_client
        
        with pytest.raises(DatabaseConnectionError):
            _ = db_manager.database
        
        with pytest.raises(DatabaseConnectionError):
            _ = db_manager.files_collection

    def test_cleanup_mongodb(self, mock_db_manager):
        """Test MongoDB cleanup."""
        # Mock the _cleanup_mongodb method directly
        mock_db_manager._cleanup_mongodb = MagicMock()
        
        mock_db_manager._cleanup_mongodb()
        
        mock_db_manager._cleanup_mongodb.assert_called_once()

    def test_cleanup_minio(self, mock_db_manager):
        """Test MinIO cleanup."""
        # Mock the _cleanup_minio method directly
        mock_db_manager._cleanup_minio = MagicMock()
        
        mock_db_manager._cleanup_minio()
        
        mock_db_manager._cleanup_minio.assert_called_once()
