"""
Tests for the main application module.
"""

import pytest
from starlette.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.application import create_application


class TestApplication:
    """Test cases for the main application."""

    def test_create_application(self):
        """Test that application is created successfully."""
        app = create_application()
        assert app is not None
        assert app.title == "FileDrive API"
        assert app.version == "1.0.0"

    def test_root_endpoint(self, client: TestClient):
        """Test the root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "FileDrive API"
        assert "version" in data
        assert "docs" in data
        assert "health" in data

    def test_docs_endpoint(self, client: TestClient):
        """Test that docs endpoint is accessible."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc_endpoint(self, client: TestClient):
        """Test that redoc endpoint is accessible."""
        response = client.get("/redoc")
        assert response.status_code == 200

    def test_openapi_endpoint(self, client: TestClient):
        """Test that OpenAPI JSON endpoint is accessible."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data

    @patch('app.application.db_manager')
    def test_health_check_success(self, mock_db_manager, client: TestClient):
        """Test health check when all services are healthy."""
        mock_db_manager.health_check = AsyncMock(return_value={
            "mongodb": {"connected": True, "status": "healthy", "error": None},
            "minio": {"connected": True, "status": "healthy", "error": None},
            "overall": {"healthy": True, "status": "healthy"}
        })

        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "version" in data
        assert "services" in data
        assert data["services"]["mongodb"] == "healthy"
        assert data["services"]["minio"] == "healthy"

    @patch('app.application.db_manager')
    def test_health_check_degraded(self, mock_db_manager, client: TestClient):
        """Test health check when some services are down."""
        mock_db_manager.health_check = AsyncMock(return_value={
            "mongodb": {"connected": True, "status": "healthy", "error": None},
            "minio": {"connected": False, "status": "unhealthy", "error": "Connection failed"},
            "overall": {"healthy": False, "status": "degraded"}
        })

        response = client.get("/health")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "degraded"

    @patch('app.application.db_manager')
    def test_health_check_failure(self, mock_db_manager, client: TestClient):
        """Test health check when health check itself fails."""
        mock_db_manager.health_check = AsyncMock(side_effect=Exception("Health check failed"))

        response = client.get("/health")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "unhealthy"
        assert "error" in data

    def test_cors_headers(self, client: TestClient):
        """Test that CORS headers are properly set."""
        response = client.options("/api/v1/files/")
        # CORS preflight should be handled by middleware
        assert response.status_code in [200, 405]  # Either handled by CORS or method not allowed
        if response.status_code == 200:
            # CORS headers should be present
            assert "access-control-allow-origin" in response.headers

    def test_process_time_header(self, client: TestClient):
        """Test that X-Process-Time header is added to responses."""
        response = client.get("/")
        assert response.status_code == 200
        assert "x-process-time" in response.headers
        process_time = float(response.headers["x-process-time"])
        assert process_time >= 0

    def test_404_handler(self, client: TestClient):
        """Test 404 error handling."""
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_validation_error_handler(self, client: TestClient):
        """Test validation error handling."""
        # Test with invalid query parameter - this should result in 405 for OPTIONS
        response = client.options("/api/v1/files/nonexistent")
        # Should handle gracefully even if validation fails
        assert response.status_code in [200, 405]  # Either handled by CORS or method not allowed

    @patch('app.application.db_manager')
    def test_startup_event(self, mock_db_manager):
        """Test application startup event."""
        mock_db_manager.connect_with_retry = AsyncMock(return_value={
            "mongodb": {"success": True, "error": None},
            "minio": {"success": True, "error": None}
        })
        mock_db_manager.health_check = AsyncMock(return_value={
            "mongodb": {"connected": True, "status": "healthy", "error": None},
            "minio": {"connected": True, "status": "healthy", "error": None},
            "overall": {"healthy": True, "status": "healthy"}
        })

        app = create_application()
        # The startup event should not raise any exceptions
        # This is a basic test to ensure the startup logic doesn't crash
        assert app is not None

    @patch('app.application.db_manager')
    def test_shutdown_event(self, mock_db_manager):
        """Test application shutdown event."""
        mock_db_manager.close_connections = AsyncMock()

        app = create_application()
        # The shutdown event should not raise any exceptions
        # This is a basic test to ensure the shutdown logic doesn't crash
        assert app is not None
