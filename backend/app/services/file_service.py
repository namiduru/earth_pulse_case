import os
import uuid
import io
from datetime import datetime
from typing import List, Optional, Tuple
from fastapi import HTTPException, UploadFile
from minio.error import S3Error

from app.database.connection import DatabaseManager
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)


class FileService:
    """Service class for file operations."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def _validate_file_size(self, file_size: int) -> None:
        """Validate file size against configured limits."""
        if file_size > settings.max_file_size:
            raise HTTPException(
                status_code=413,
                detail=f"File size {file_size} bytes exceeds maximum allowed size of {settings.max_file_size} bytes"
            )
    
    def _validate_file_type(self, content_type: str) -> None:
        """Validate file MIME type against allowed types."""
        if not content_type:
            raise HTTPException(
                status_code=400,
                detail="File content type is required"
            )
        
        is_allowed = False
        for allowed_type in settings.allowed_file_types_list:
            if allowed_type.endswith('/*'):
                base_type = allowed_type.split('/')[0]
                if content_type.startswith(f"{base_type}/"):
                    is_allowed = True
                    break
            elif content_type == allowed_type:
                is_allowed = True
                break
        
        if not is_allowed:
            raise HTTPException(
                status_code=400,
                detail=f"File type '{content_type}' is not allowed. Allowed types: {settings.allowed_file_types_list}"
            )
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to prevent security issues."""
        if not filename:
            return "unnamed_file"
        
        filename = os.path.basename(filename)
        
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '\\', '/']
        for char in dangerous_chars:
            filename = filename.replace(char, '_')
        
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext
        
        return filename
    
    async def list_files(self) -> List[dict]:
        """Get all files from database."""
        try:
            files = []
            async for file in self.db_manager.files_collection.find():
                file["_id"] = str(file["_id"])
                files.append(file)
            return files
        except Exception as e:
            logger.error(f"Error listing files: {e}")
            raise HTTPException(status_code=500, detail="Failed to list files")
    
    async def get_file_by_id(self, file_id: str) -> Optional[dict]:
        """Get file by file_id."""
        if not file_id:
            raise HTTPException(status_code=400, detail="File ID is required")
        
        try:
            file_doc = await self.db_manager.files_collection.find_one({"file_id": file_id})
            if file_doc:
                file_doc["_id"] = str(file_doc["_id"])
            return file_doc
        except Exception as e:
            logger.error(f"Error getting file {file_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to get file")
    
    async def upload_file(self, file: UploadFile) -> dict:
        """Upload file to MinIO and save metadata to MongoDB."""
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        self._validate_file_type(file.content_type or "")
        
        try:
            file_content = await file.read()
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            raise HTTPException(status_code=400, detail="Failed to read file")
        
        self._validate_file_size(len(file_content))
        
        sanitized_filename = self._sanitize_filename(file.filename)
        
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(sanitized_filename)[1]
        
        try:
            minio_client = self.db_manager.minio_client
            minio_client.put_object(
                settings.minio_bucket,
                file_id,
                io.BytesIO(file_content),
                length=len(file_content),
                content_type=file.content_type
            )
            
            file_data = {
                "file_id": file_id,
                "name": sanitized_filename,
                "size": len(file_content),
                "content_type": file.content_type,
                "upload_date": datetime.utcnow(),
                "extension": file_extension
            }
            
            result = await self.db_manager.files_collection.insert_one(file_data)
            file_data["_id"] = str(result.inserted_id)
            
            logger.info(f"File uploaded successfully: {file_id} ({sanitized_filename})")
            return file_data
            
        except S3Error as e:
            logger.error(f"MinIO error during upload: {e}")
            raise HTTPException(status_code=500, detail=f"Storage error: {str(e)}")
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
    async def download_file(self, file_id: str) -> Tuple[io.BytesIO, dict]:
        """Download file from MinIO."""
        if not file_id:
            raise HTTPException(status_code=400, detail="File ID is required")
        
        file_doc = await self.get_file_by_id(file_id)
        if not file_doc:
            raise HTTPException(status_code=404, detail="File not found")
        
        try:
            minio_client = self.db_manager.minio_client
            file_obj = minio_client.get_object(
                settings.minio_bucket,
                file_id
            )
            
            file_content = file_obj.read()
            file_obj.close()
            
            logger.info(f"File downloaded successfully: {file_id}")
            return io.BytesIO(file_content), file_doc
            
        except S3Error as e:
            logger.error(f"MinIO error during download: {e}")
            raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")
        except Exception as e:
            logger.error(f"Error downloading file {file_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")
    
    async def update_file_name(self, file_id: str, new_name: str) -> dict:
        """Update file name in database."""
        if not file_id:
            raise HTTPException(status_code=400, detail="File ID is required")
        
        if not new_name:
            raise HTTPException(status_code=400, detail="New file name is required")
        
        sanitized_name = self._sanitize_filename(new_name)
        
        file_doc = await self.get_file_by_id(file_id)
        if not file_doc:
            raise HTTPException(status_code=404, detail="File not found")
        
        try:
            await self.db_manager.files_collection.update_one(
                {"file_id": file_id},
                {"$set": {"name": sanitized_name}}
            )
            logger.info(f"File name updated: {file_id} -> {sanitized_name}")
            return {"message": "File name updated successfully"}
        except Exception as e:
            logger.error(f"Error updating file name {file_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to update file name")
    
    async def delete_file(self, file_id: str) -> dict:
        """Delete file from MinIO and MongoDB."""
        if not file_id:
            raise HTTPException(status_code=400, detail="File ID is required")
        
        file_doc = await self.get_file_by_id(file_id)
        if not file_doc:
            raise HTTPException(status_code=404, detail="File not found")
        
        try:
            minio_client = self.db_manager.minio_client
            minio_client.remove_object(
                settings.minio_bucket,
                file_id
            )
            
            await self.db_manager.files_collection.delete_one({"file_id": file_id})
            
            logger.info(f"File deleted successfully: {file_id}")
            return {"message": "File deleted successfully"}
            
        except S3Error as e:
            logger.error(f"MinIO error during deletion: {e}")
            raise HTTPException(status_code=500, detail=f"Storage error: {str(e)}")
        except Exception as e:
            logger.error(f"Error deleting file {file_id}: {e}")
            raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}") 