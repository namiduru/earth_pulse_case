from fastapi import APIRouter, Depends, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from typing import List
import io

from app.database.connection import get_database_manager, DatabaseManager
from app.services.file_service import FileService
from app.schemas.file import (
    FileResponse, 
    FileUploadResponse, 
    FileDeleteResponse, 
    FileUpdateResponse
)

router = APIRouter(prefix="/files", tags=["files"])


async def get_file_service(db_manager: DatabaseManager = Depends(get_database_manager)) -> FileService:
    """Dependency to get file service."""
    return FileService(db_manager)


@router.get("/", response_model=List[FileResponse], summary="List all files")
async def list_files(
    file_service: FileService = Depends(get_file_service)
):
    """
    Retrieve all files from the system.
    
    Returns:
        List of file information including ID, name, size, and upload date.
    """
    files = await file_service.list_files()
    return files


@router.post("/upload", response_model=FileUploadResponse, summary="Upload a file")
async def upload_file(
    file: UploadFile = File(...),
    file_service: FileService = Depends(get_file_service)
):
    """
    Upload a new file to the system.
    
    Args:
        file: The file to upload
        
    Returns:
        Upload confirmation with file details
    """
    file_data = await file_service.upload_file(file)
    return {
        "message": "File uploaded successfully",
        "file": file_data
    }


@router.get("/download/{file_id}", summary="Download a file")
async def download_file(
    file_id: str,
    file_service: FileService = Depends(get_file_service)
):
    """
    Download a file by its ID.
    
    Args:
        file_id: Unique identifier of the file
        
    Returns:
        File content as a downloadable response
    """
    file_obj, file_doc = await file_service.download_file(file_id)
    
    return StreamingResponse(
        io.BytesIO(file_obj.read()),
        media_type=file_doc["content_type"],
        headers={"Content-Disposition": f"attachment; filename={file_doc['name']}"}
    )


@router.put("/{file_id}", response_model=FileUpdateResponse, summary="Update file name")
async def update_file_name(
    file_id: str,
    name: str = Query(..., description="New file name"),
    file_service: FileService = Depends(get_file_service)
):
    """
    Update the name of an existing file.
    
    Args:
        file_id: Unique identifier of the file
        name: New name for the file
        
    Returns:
        Update confirmation message
    """
    result = await file_service.update_file_name(file_id, name)
    return result


@router.delete("/{file_id}", response_model=FileDeleteResponse, summary="Delete a file")
async def delete_file(
    file_id: str,
    file_service: FileService = Depends(get_file_service)
):
    """
    Delete a file from the system.
    
    Args:
        file_id: Unique identifier of the file to delete
        
    Returns:
        Deletion confirmation message
    """
    result = await file_service.delete_file(file_id)
    return result 