"""
Pytest configuration and fixtures for backend tests.
"""

import pytest
import asyncio
import os
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch
from starlette.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
from minio import Minio

from app.application import create_application
from app.database.connection import DatabaseManager
from app.services.file_service import FileService

# Set environment variables to disable database connections during testing
os.environ["TESTING"] = "true"
os.environ["MONGODB_URL"] = "mongodb://localhost:27017/test"
os.environ["MINIO_ENDPOINT"] = "localhost:9000"
os.environ["MINIO_ACCESS_KEY"] = "test"
os.environ["MINIO_SECRET_KEY_VALUE"] = "test"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def app():
    """Create a test application instance with mocked database connections."""
    with patch('app.application.db_manager') as mock_db_manager:
        # Mock the database manager to prevent real connections
        mock_db_manager.connect_with_retry = AsyncMock(return_value={
            "mongodb": {"success": True, "error": None},
            "minio": {"success": True, "error": None}
        })
        mock_db_manager.health_check = AsyncMock(return_value={
            "mongodb": {"connected": True, "status": "healthy", "error": None},
            "minio": {"connected": True, "status": "healthy", "error": None},
            "overall": {"healthy": True, "status": "healthy"}
        })
        mock_db_manager.close_connections = AsyncMock()
        
        app = create_application()
        return app


@pytest.fixture
def client(app) -> TestClient:
    """Create a test client for the application."""
    return TestClient(app)


@pytest.fixture
def mock_db_manager() -> MagicMock:
    """Create a mock database manager."""
    mock_manager = MagicMock(spec=DatabaseManager)
    mock_manager.mongodb_client = MagicMock(spec=AsyncIOMotorClient)
    mock_manager.minio_client = MagicMock(spec=Minio)
    mock_manager.files_collection = AsyncMock()
    mock_manager.is_mongodb_connected = True
    mock_manager.is_minio_connected = True
    mock_manager.is_connected = True
    # Add private attributes for testing
    mock_manager._mongodb_connected = True
    mock_manager._minio_connected = True
    mock_manager._mongodb_client = MagicMock()
    mock_manager._minio_client = MagicMock()
    return mock_manager


@pytest.fixture
def mock_file_service(mock_db_manager) -> FileService:
    """Create a file service with mocked database manager."""
    return FileService(mock_db_manager)


@pytest.fixture
def sample_file_data() -> dict:
    """Sample file data for testing."""
    return {
        "file_id": "test-file-id-123",
        "name": "test_file.txt",
        "size": 1024,
        "content_type": "text/plain",
        "upload_date": "2023-01-01T00:00:00",
        "extension": ".txt",
        "_id": "mongo-id-123"
    }


@pytest.fixture
def sample_upload_file():
    """Create a mock upload file for testing."""
    mock_file = MagicMock()
    mock_file.filename = "test_file.txt"
    mock_file.content_type = "text/plain"
    mock_file.read = AsyncMock(return_value=b"test file content")
    return mock_file


@pytest.fixture
def mock_minio_response():
    """Create a mock MinIO response."""
    mock_response = MagicMock()
    mock_response.read.return_value = b"test file content"
    mock_response.close = MagicMock()
    return mock_response


@pytest.fixture
def mock_s3_error():
    """Create a mock S3Error for testing."""
    mock_error = MagicMock()
    mock_error.message = "MinIO error"
    mock_error.resource = "test-bucket"
    mock_error.request_id = "test-request-id"
    mock_error.host_id = "test-host-id"
    mock_error.response = MagicMock()
    return mock_error
