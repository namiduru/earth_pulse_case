# Backend Tests

This directory contains comprehensive tests for the FileDrive API backend.

## Test Structure

- `conftest.py` - Pytest configuration and fixtures
- `test_application.py` - Tests for the main application module
- `test_file_service.py` - Tests for the FileService class
- `test_api_files.py` - Tests for the files API endpoints
- `test_database_connection.py` - Tests for the database connection module
- `test_schemas.py` - Tests for Pydantic schemas
- `test_config.py` - Tests for configuration modules
- `test_integration.py` - Integration tests for the full application

## Running Tests

### Install test dependencies

```bash
pip install -r requirements-test.txt
```

### Run all tests

```bash
pytest
```

### Run specific test categories

```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Async tests only
pytest -m asyncio

# Slow tests only
pytest -m slow
```

### Run specific test files

```bash
pytest tests/test_application.py
pytest tests/test_file_service.py
pytest tests/test_api_files.py
```

### Run with coverage

```bash
pytest --cov=app --cov-report=html
```

## Test Coverage

The tests cover:

### Application Module

- Application creation and configuration
- Root and health check endpoints
- CORS middleware
- Error handling middleware
- Startup and shutdown events

### File Service

- File validation (size, type)
- Filename sanitization
- File operations (upload, download, update, delete)
- Error handling for various scenarios
- Database and MinIO integration

### API Endpoints

- All CRUD operations for files
- Request validation
- Response formatting
- Error handling
- CORS preflight requests

### Database Connection

- MongoDB connection management
- MinIO connection management
- Health checks
- Retry mechanisms
- Connection cleanup

### Schemas

- Pydantic model validation
- Data serialization/deserialization
- Field validation
- JSON compatibility

### Configuration

- Settings loading and validation
- Environment variable handling
- Constants validation
- Configuration consistency

### Integration

- Full application flow
- End-to-end file operations
- Concurrent request handling
- Error scenarios
- Performance characteristics

## Test Fixtures

The `conftest.py` file provides several useful fixtures:

- `app` - FastAPI application instance
- `client` - TestClient for making HTTP requests
- `mock_db_manager` - Mocked database manager
- `mock_file_service` - FileService with mocked dependencies
- `sample_file_data` - Sample file data for testing
- `sample_upload_file` - Mock upload file
- `mock_minio_response` - Mock MinIO response

## Mocking Strategy

Tests use extensive mocking to isolate units and avoid external dependencies:

- Database operations are mocked using `AsyncMock`
- MinIO operations are mocked using `MagicMock`
- External services are mocked to avoid network calls
- File operations are mocked to avoid disk I/O

## Best Practices

1. **Isolation**: Each test is independent and doesn't rely on other tests
2. **Mocking**: External dependencies are properly mocked
3. **Coverage**: All code paths are tested, including error scenarios
4. **Naming**: Test names clearly describe what is being tested
5. **Documentation**: Each test has a descriptive docstring
6. **Assertions**: Tests have clear, specific assertions

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

- Fast execution (under 30 seconds)
- No external dependencies
- Clear pass/fail results
- Comprehensive coverage reporting


