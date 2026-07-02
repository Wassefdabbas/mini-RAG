from fastapi import FastAPI, APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
import os
from src.helpers.config import get_settings, Settings
from src.controllers import DataController, ProjectController
import aiofiles
from src.models import ResponseStatus
import logging

logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["data"],
)

@data_router.post("/upload/{project_id}")
async def upload_file(project_id: str,
                      file: UploadFile, 
                      app_settings: Settings = Depends(get_settings)):
    
    # Validate the file proporties
    is_valid = DataController().validate_file(file=file)
    if not is_valid["success"]:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, 
                            content=is_valid)

    file_path, file_id = DataController().generate_unique_filepath(original_filename=file.filename, project_id=project_id)
    
    try:
        async with aiofiles.open(file_path, 'wb') as out_file:
            while chunk := await file.read(app_settings.FILE_DEFAULT_CHUNK_SIZE):
                await out_file.write(chunk)
                
    except Exception as e:
        
        logger.error(f"Error occurred while uploading file: {str(e)}")
        
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content={"success": False, 
                                     "message": ResponseStatus.FILE_UPLOAD_FAILED.value})
            
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"success": True, 
                                 "message": ResponseStatus.FILE_UPLOAD_SUCCESS.value,
                                 "file_id": file_id,
                                 "file_path": file_path})