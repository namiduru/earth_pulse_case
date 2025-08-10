"""
Configuration constants for the application.

This module contains all constants used for validation rules and configuration limits.
"""


class ValidationConstants:
    """Constants used for validation rules."""
    
    # File size limits
    MAX_FILE_SIZE_GB = 1
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_GB * 1024 * 1024 * 1024
    
    # Secret key requirements
    MIN_SECRET_KEY_LENGTH = 32
    
    # MinIO bucket requirements
    MIN_BUCKET_NAME_LENGTH = 3
    MAX_BUCKET_NAME_LENGTH = 63
    MIN_ACCESS_KEY_LENGTH = 3
    
    # MongoDB database name invalid characters
    INVALID_DB_CHARS = [' ', '/', '\\', '.', '"', '$', '*', '<', '>', ':', '|', '?']
    
    # Environment types
    DEV_ENVIRONMENTS = ["dev", "development"]
    PROD_ENVIRONMENTS = ["prod", "production"]


class DefaultValues:
    """Default configuration values."""
    
    # API Configuration
    API_TITLE = "FileDrive API"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = "A FastAPI-based file storage and management system"
    
    # Server Configuration
    HOST = "0.0.0.0"
    PORT = 8000
    DEBUG = False
    
    # CORS Configuration
    ALLOWED_ORIGINS = "http://localhost:3000"
    
    # Database Configuration
    MAX_POOL_SIZE = 10
    MIN_POOL_SIZE = 1
    MAX_IDLE_TIME_MS = 30000
    SERVER_SELECTION_TIMEOUT_MS = 5000
    CONNECT_TIMEOUT_MS = 10000
    SOCKET_TIMEOUT_MS = 20000
    
    # Retry Configuration
    RETRY_ENABLED = True
    MAX_RETRIES = 3
    RETRY_DELAY = 1.0
    
    # MinIO Configuration
    SECURE = False
    REGION = "us-east-1"
    
    # Security Configuration
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # File Upload Configuration
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    ALLOWED_FILE_TYPES = "*/*"
