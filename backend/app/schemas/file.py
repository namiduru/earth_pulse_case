from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, ConfigDict


class FileBase(BaseModel):
    """Base file schema."""
    name: str = Field(..., description="File name")
    size: int = Field(..., description="File size in bytes")
    content_type: str = Field(..., description="MIME type")
    extension: str = Field(..., description="File extension")


class FileResponse(FileBase):
    """Schema for file response."""
    file_id: str = Field(..., description="Unique file identifier")
    upload_date: datetime = Field(..., description="Upload timestamp")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class FileUploadResponse(BaseModel):
    """Schema for file upload response."""
    message: str = Field(..., description="Success message")
    file: FileResponse = Field(..., description="Uploaded file details")


class FileDeleteResponse(BaseModel):
    """Schema for file deletion response."""
    message: str = Field(..., description="Success message")


class FileUpdateResponse(BaseModel):
    """Schema for file update response."""
    message: str = Field(..., description="Success message") 