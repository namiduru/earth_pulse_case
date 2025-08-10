"""
Configuration validators for the application.

This module contains all validation logic for configuration settings.
"""

from typing import Union
from pydantic import field_validator, SecretStr
from .constants import ValidationConstants


class SettingsValidators:
    """Validation methods for application settings."""
    
    @staticmethod
    @field_validator("mongodb_url")
    @classmethod
    def validate_mongodb_url(cls, v: str) -> str:
        """Validate MongoDB URL format."""
        if not v or not v.strip():
            raise ValueError("MongoDB URL is required")
        if not v.startswith(("mongodb://", "mongodb+srv://")):
            raise ValueError(
                "Invalid MongoDB URL format. Must start with 'mongodb://' or 'mongodb+srv://'"
            )
        return v.strip()
    
    @staticmethod
    @field_validator("mongodb_database")
    @classmethod
    def validate_mongodb_database(cls, v: str) -> str:
        """Validate MongoDB database name."""
        if not v or not v.strip():
            raise ValueError("MongoDB database name is required")
        if any(char in v for char in ValidationConstants.INVALID_DB_CHARS):
            raise ValueError(
                f"MongoDB database name contains invalid characters: "
                f"{ValidationConstants.INVALID_DB_CHARS}"
            )
        return v.strip()
    
    @staticmethod
    @field_validator("allowed_origins")
    @classmethod
    def validate_origins(cls, v: str) -> str:
        """Validate CORS origins."""
        if not v or not v.strip():
            raise ValueError("At least one CORS origin must be specified")
        return v.strip()
    
    @staticmethod
    @field_validator("minio_endpoint")
    @classmethod
    def validate_minio_endpoint(cls, v: str) -> str:
        """Validate MinIO endpoint."""
        if not v or not v.strip():
            raise ValueError("MinIO endpoint is required")
        return v.strip()
    
    @staticmethod
    @field_validator("minio_access_key")
    @classmethod
    def validate_minio_access_key(cls, v: str) -> str:
        """Validate MinIO access key."""
        if not v or not v.strip():
            raise ValueError("MinIO access key is required")
        if len(v.strip()) < ValidationConstants.MIN_ACCESS_KEY_LENGTH:
            raise ValueError(
                f"MinIO access key must be at least {ValidationConstants.MIN_ACCESS_KEY_LENGTH} "
                f"characters long"
            )
        return v.strip()
    
    @staticmethod
    @field_validator("minio_bucket")
    @classmethod
    def validate_minio_bucket(cls, v: str) -> str:
        """Validate MinIO bucket name according to S3 naming rules."""
        if not v or not v.strip():
            raise ValueError("MinIO bucket name is required")
        if len(v) < ValidationConstants.MIN_BUCKET_NAME_LENGTH or len(v) > ValidationConstants.MAX_BUCKET_NAME_LENGTH:
            raise ValueError(
                f"MinIO bucket name must be between {ValidationConstants.MIN_BUCKET_NAME_LENGTH} "
                f"and {ValidationConstants.MAX_BUCKET_NAME_LENGTH} characters"
            )
        if not v[0].isalnum() or not v[-1].isalnum():
            raise ValueError("MinIO bucket name must start and end with alphanumeric characters")
        return v.strip()
    
    @staticmethod
    @field_validator("max_file_size")
    @classmethod
    def validate_max_file_size(cls, v: int) -> int:
        """Validate maximum file size."""
        if v <= 0:
            raise ValueError("Max file size must be positive")
        if v > ValidationConstants.MAX_FILE_SIZE_BYTES:
            raise ValueError(
                f"Max file size cannot exceed {ValidationConstants.MAX_FILE_SIZE_GB}GB "
                f"({ValidationConstants.MAX_FILE_SIZE_BYTES} bytes)"
            )
        return v
    
    @staticmethod
    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: SecretStr) -> SecretStr:
        """Validate secret key strength."""
        if len(v.get_secret_value()) < ValidationConstants.MIN_SECRET_KEY_LENGTH:
            raise ValueError(
                f"Secret key must be at least {ValidationConstants.MIN_SECRET_KEY_LENGTH} "
                f"characters long"
            )
        return v
