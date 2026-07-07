from fastapi import FastAPI, APIRouter, Depends, UploadFile, status
from fastapi.responses import JSONResponse
import os
from src.helpers.config import get_settings, Settings
from src.controllers import DataController, ProjectController, ProcessController
import aiofiles
from src.models import ResponseStatus
import logging
from .schemas.data import ProcessRequest

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
    

@data_router.post("/process/{project_id}")
async def process_file(project_id: str,
                       process_request: ProcessRequest):
    
    file_id = process_request.file_id
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    
    process_controller = ProcessController(project_id=project_id)
    
    file_content = process_controller.get_file_content(file_id=file_id)
    
    file_chunks = process_controller.process_file_content(file_content=file_content, 
                                                          file_id=file_id, 
                                                          chunk_size=chunk_size, 
                                                          overlap_size=overlap_size)
    
    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"success": False, 
                                     "message": ResponseStatus.PROCESSING_FAILED.value})
        
    return JSONResponse(status_code=status.HTTP_200_OK,
                    content={
                        "success": True,
                        "message": ResponseStatus.PROCESSING_SUCCESS.value,
                        "file_chunks": [
                            {
                                "content": chunk.page_content,
                                "metadata": chunk.metadata
                            }
                            for chunk in file_chunks
                        ]
                    })
    