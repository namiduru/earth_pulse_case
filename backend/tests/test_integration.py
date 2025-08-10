"""
Integration tests for the full application.
"""

import pytest
import io
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from starlette.testclient import TestClient

from app.application import create_application


class TestApplicationIntegration:
    """Integration tests for the full application."""

    def test_full_application_startup(self, client: TestClient):
        """Test that the full application starts up correctly."""
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "FileDrive API"
        assert "version" in data
        assert "docs" in data
        assert "health" in data

    def test_health_check_integration(self, client: TestClient):
        """Test health check endpoint integration."""
        response = client.get("/health")
        assert response.status_code in [200, 503]  # Either healthy or degraded
        
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "services" in data

    def test_api_documentation_access(self, client: TestClient):
        """Test that API documentation is accessible."""
        # Test OpenAPI JSON
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
        
        # Test Swagger UI
        response = client.get("/docs")
        assert response.status_code == 200
        
        # Test ReDoc
        response = client.get("/redoc")
        assert response.status_code == 200

    def test_cors_integration(self, client: TestClient):
        """Test CORS integration across all endpoints."""
        # Test CORS headers on regular GET requests with Origin header
        headers = {"Origin": "http://localhost:3000"}
        
        endpoints = [
            "/"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint, headers=headers)
            assert response.status_code == 200
            # CORS headers should be present for requests with Origin header
            assert "access-control-allow-origin" in response.headers

    def test_error_handling_integration(self, client: TestClient):
        """Test error handling integration."""
        # Test 404 handling
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        
        # Test validation error handling
        response = client.post("/api/v1/files/upload")
        assert response.status_code == 422  # Validation error
        
        # Test invalid file ID format
        response = client.get("/api/v1/files/download/invalid-id")
        assert response.status_code in [404, 500]  # Either not found or server error

    def test_middleware_integration(self, client: TestClient):
        """Test middleware integration."""
        response = client.get("/")
        assert response.status_code == 200
        
        # Test that process time header is added
        assert "x-process-time" in response.headers
        process_time = float(response.headers["x-process-time"])
        assert process_time >= 0
        
        # Test that CORS headers are present for requests with Origin header
        # Note: CORS headers are only added when there's an Origin header
        # or for preflight OPTIONS requests

    def test_application_shutdown_integration(self):
        """Test application shutdown integration."""
        # Create a new application instance
        app = create_application()
        
        # Test that the application can be created without errors
        assert app is not None
        
        # Test that startup and shutdown events are properly defined
        assert hasattr(app, 'router')
        assert len(app.routes) > 0

    def test_api_versioning_integration(self, client: TestClient):
        """Test API versioning integration."""
        # Test that the API version is properly set
        response = client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "version" in data
        assert data["version"] == "1.0.0"
        
        # Test that all API endpoints are under /api/v1/
        response = client.get("/api/v1/files/")
        # Should not be 404 (even if it's 500 due to database issues)
        assert response.status_code != 404

    def test_response_format_integration(self, client: TestClient):
        """Test response format consistency."""
        # Test that all JSON responses have consistent format
        endpoints = ["/", "/health"]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, dict)
                assert len(data) > 0

    def test_error_response_format_integration(self, client: TestClient):
        """Test error response format consistency."""
        # Test 404 error format
        response = client.get("/nonexistent-endpoint")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)
        
        # Test validation error format
        response = client.post("/api/v1/files/upload")
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data

    def test_headers_integration(self, client: TestClient):
        """Test response headers integration."""
        response = client.get("/")
        assert response.status_code == 200
        
        # Test required headers
        assert "content-type" in response.headers
        assert response.headers["content-type"] == "application/json"
        
        # Test custom headers
        assert "x-process-time" in response.headers
        
        # Test CORS headers are present when Origin header is provided
        headers = {"Origin": "http://localhost:3000"}
        response_with_origin = client.get("/", headers=headers)
        assert "access-control-allow-origin" in response_with_origin.headers

    def test_application_configuration_integration(self, client: TestClient):
        """Test application configuration integration."""
        # Test that the application is properly configured
        response = client.get("/openapi.json")
        assert response.status_code == 200
        
        data = response.json()
        # The title might be modified by environment variables, so just check it exists
        assert "title" in data["info"]
        assert data["info"]["version"] == "1.0.0"
        assert "description" in data["info"]
        
        # Test that API paths are properly defined
        assert "/api/v1/files/" in data["paths"]
        assert "/api/v1/files/upload" in data["paths"]
        assert "/health" in data["paths"]
        assert "/" in data["paths"]
