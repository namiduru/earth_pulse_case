"""
Application configuration settings module.

This module defines all application configuration using Pydantic settings.
It provides validation, type safety, and environment variable support.
"""

import os
from typing import List
from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings

from .constants import ValidationConstants, DefaultValues
from .validators import SettingsValidators


class Settings(BaseSettings):
    """
    Main application settings configuration.
    
    This class manages all application configuration using Pydantic settings.
    It provides validation, type safety, and environment variable support.
    
    Environment Variables:
        All settings can be configured via environment variables with the
        FILEDRIVE_ prefix. For example: FILEDRIVE_MONGODB_URL
    """
    
    # ============================================================================
    # API Configuration
    # ============================================================================
    api_title: str = Field(
        default=DefaultValues.API_TITLE,
        description="API title for OpenAPI documentation"
    )
    api_version: str = Field(
        default=DefaultValues.API_VERSION,
        description="API version"
    )
    api_description: str = Field(
        default=DefaultValues.API_DESCRIPTION,
        description="API description for OpenAPI documentation"
    )
    
    # ============================================================================
    # Server Configuration
    # ============================================================================
    host: str = Field(
        default=DefaultValues.HOST,
        description="Server host address"
    )
    port: int = Field(
        default=DefaultValues.PORT,
        ge=1,
        le=65535,
        description="Server port number"
    )
    debug: bool = Field(
        default=DefaultValues.DEBUG,
        description="Enable debug mode"
    )
    
    # ============================================================================
    # CORS Configuration
    # ============================================================================
    allowed_origins: str = Field(
        default=DefaultValues.ALLOWED_ORIGINS,
        description="Comma-separated list of allowed CORS origins"
    )
    
    # ============================================================================
    # Database Configuration
    # ============================================================================
    mongodb_url: str = Field(description="MongoDB connection URL (required)")
    mongodb_database: str = Field(description="MongoDB database name (required)")
    
    # Database Connection Pool Configuration
    mongodb_max_pool_size: int = Field(
        default=DefaultValues.MAX_POOL_SIZE,
        ge=1,
        le=100,
        description="Maximum MongoDB connection pool size"
    )
    mongodb_min_pool_size: int = Field(
        default=DefaultValues.MIN_POOL_SIZE,
        ge=0,
        le=50,
        description="Minimum MongoDB connection pool size"
    )
    mongodb_max_idle_time_ms: int = Field(
        default=DefaultValues.MAX_IDLE_TIME_MS,
        ge=1000,
        le=300000,
        description="Maximum idle time for MongoDB connections in milliseconds"
    )
    mongodb_server_selection_timeout_ms: int = Field(
        default=DefaultValues.SERVER_SELECTION_TIMEOUT_MS,
        ge=1000,
        le=30000,
        description="MongoDB server selection timeout in milliseconds"
    )
    mongodb_connect_timeout_ms: int = Field(
        default=DefaultValues.CONNECT_TIMEOUT_MS,
        ge=1000,
        le=60000,
        description="MongoDB connection timeout in milliseconds"
    )
    mongodb_socket_timeout_ms: int = Field(
        default=DefaultValues.SOCKET_TIMEOUT_MS,
        ge=1000,
        le=60000,
        description="MongoDB socket timeout in milliseconds"
    )
    
    # Database Retry Configuration
    db_retry_enabled: bool = Field(
        default=DefaultValues.RETRY_ENABLED,
        description="Enable database connection retry mechanism"
    )
    db_max_retries: int = Field(
        default=DefaultValues.MAX_RETRIES,
        ge=1,
        le=10,
        description="Maximum number of retry attempts for database connections"
    )
    db_retry_delay: float = Field(
        default=DefaultValues.RETRY_DELAY,
        ge=0.1,
        le=10.0,
        description="Initial delay in seconds between retry attempts"
    )
    
    # ============================================================================
    # MinIO Storage Configuration
    # ============================================================================
    minio_endpoint: str = Field(description="MinIO endpoint URL (required)")
    minio_access_key: str = Field(description="MinIO access key (required)")
    minio_secret_key: SecretStr = Field(description="MinIO secret key (required)")
    minio_bucket: str = Field(description="MinIO bucket name (required)")
    minio_secure: bool = Field(
        default=DefaultValues.SECURE,
        description="Use secure connection for MinIO"
    )
    minio_region: str = Field(
        default=DefaultValues.REGION,
        description="MinIO region"
    )
    
    # ============================================================================
    # Security Configuration
    # ============================================================================
    secret_key: SecretStr = Field(description="Secret key for JWT tokens (required)")
    algorithm: str = Field(
        default=DefaultValues.ALGORITHM,
        description="JWT algorithm"
    )
    access_token_expire_minutes: int = Field(
        default=DefaultValues.ACCESS_TOKEN_EXPIRE_MINUTES,
        ge=1,
        le=1440,
        description="Access token expiration time in minutes"
    )
    
    # ============================================================================
    # File Upload Configuration
    # ============================================================================
    max_file_size: int = Field(
        default=DefaultValues.MAX_FILE_SIZE,
        description="Maximum file size in bytes"
    )
    allowed_file_types: str = Field(
        default=DefaultValues.ALLOWED_FILE_TYPES,
        description="Allowed file MIME types (comma-separated, use */* for all)"
    )
    
    # ============================================================================
    # Validation Methods (imported from validators module)
    # ============================================================================
    validate_mongodb_url = SettingsValidators.validate_mongodb_url
    validate_mongodb_database = SettingsValidators.validate_mongodb_database
    validate_origins = SettingsValidators.validate_origins
    validate_minio_endpoint = SettingsValidators.validate_minio_endpoint
    validate_minio_access_key = SettingsValidators.validate_minio_access_key
    validate_minio_bucket = SettingsValidators.validate_minio_bucket
    validate_max_file_size = SettingsValidators.validate_max_file_size
    validate_secret_key = SettingsValidators.validate_secret_key
    
    # ============================================================================
    # Computed Properties
    # ============================================================================
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Get allowed origins as a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]
    
    @property
    def allowed_file_types_list(self) -> List[str]:
        """Get allowed file types as a list."""
        if self.allowed_file_types == "*/*":
            return ["*/*"]
        return [ft.strip() for ft in self.allowed_file_types.split(",") if ft.strip()]
    
    @property
    def minio_secret_key_value(self) -> str:
        """Get the actual MinIO secret key value."""
        return self.minio_secret_key.get_secret_value()
    
    @property
    def secret_key_value(self) -> str:
        """Get the actual JWT secret key value."""
        return self.secret_key.get_secret_value()
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.debug or os.getenv("ENVIRONMENT", "").lower() in ValidationConstants.DEV_ENVIRONMENTS
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return not self.debug and os.getenv("ENVIRONMENT", "").lower() in ValidationConstants.PROD_ENVIRONMENTS
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        env_prefix = "FILEDRIVE_"


def create_settings() -> Settings:
    """Create and validate settings instance."""
    try:
        return Settings()
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        print("Please check your environment variables and .env file")
        print("\nRequired environment variables:")
        print("- FILEDRIVE_MONGODB_URL")
        print("- FILEDRIVE_MONGODB_DATABASE")
        print("- FILEDRIVE_MINIO_ENDPOINT")
        print("- FILEDRIVE_MINIO_ACCESS_KEY")
        print("- FILEDRIVE_MINIO_SECRET_KEY")
        print("- FILEDRIVE_MINIO_BUCKET")
        print("- FILEDRIVE_SECRET_KEY")
        raise


# Create settings instance
settings = create_settings() 