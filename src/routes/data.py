from urllib import request

from fastapi import FastAPI, APIRouter, Depends, Request, UploadFile, status
from fastapi.responses import JSONResponse
import os
from src.helpers.config import get_settings, Settings
from src.controllers import DataController, ProjectController, ProcessController
import aiofiles
from src.models import ResponseStatus
import logging
from .schemas.data import ProcessRequest
from src.models.ProjectModel import ProjectModel
from src.models.ChunkModel import ChunkModel
from src.models.AssetModel import AssetModel
from src.models.db_schemas import DataChunk, Asset
from src.models.enums.AssetsTypeEnum import AssetsTypeEnum

logger = logging.getLogger('uvicorn.error')

data_router = APIRouter(
    prefix="/api/v1/data",
    tags=["data"],
)

@data_router.post("/upload/{project_id}")
async def upload_file(request: Request,
                      project_id: str,
                      file: UploadFile, 
                      app_settings: Settings = Depends(get_settings)):
    
    # call the ProjectModel and init index
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_project_or_create(project_id=project_id)
    
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
            
    
    # store the assets into db
    asset_model = await AssetModel.create_instance(db_client=request.app.db_client)
    asset = Asset(
        asset_project_id=project.id,
        asset_type=AssetsTypeEnum.FILE.value,
        asset_name=file_id,
        asset_size=os.path.getsize(file_path)
    )
    asset_record = await asset_model.create_asset(asset=asset)
        
        
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"success": True, 
                                 "message": ResponseStatus.FILE_UPLOAD_SUCCESS.value,
                                 "file_id": str(asset_record.id)})
    

@data_router.post("/process/{project_id}")
async def process_file(request: Request,
                       project_id: str,
                       process_request: ProcessRequest):
    
    chunk_size = process_request.chunk_size
    overlap_size = process_request.overlap_size
    do_reset = process_request.do_reset
    
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    project = await project_model.get_project_or_create(project_id=project_id)

    
    process_controller = ProcessController(project_id=project_id)
    asset_model = await AssetModel.create_instance(db_client=request.app.db_client)
    
    project_files_ids = {}
    if process_request.file_id:
        asset_record = await asset_model.get_asset_by_id(asset_project_id=project.id, asset_name=process_request.file_id)
        
        if asset_record is None:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                                content={"success": False, 
                                         "message": ResponseStatus.NO_FILES_ID.value})
        project_files_ids = {asset_record.id: asset_record.asset_name}
    else:
        project_assets = await asset_model.get_all_project_assets(asset_project_id=project.id, asset_type=AssetsTypeEnum.FILE.value)
        project_files_ids = {record.id: record.asset_name for record in project_assets}
        
    if len(project_files_ids) == 0:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                            content={"success": False, 
                                     "message": ResponseStatus.NO_FILES_TO_PROCESS.value})
    
    inserted_count = 0
    num_files = 0
    
    chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)

    if(do_reset):
        deleted_count = await chunk_model.delete_chunks_by_project_id(project_id=project.id)        
        logger.info(f"Deleted {deleted_count} chunks for project_id: {project_id}")
            
    for asset_id, file_id in project_files_ids.items():
        file_content = process_controller.get_file_content(file_id=file_id)
        
        # continue the process but log the message
        if file_content is None:
            logger.warning(f"File content is None for file_id: {file_id}. Skipping processing for this file.")
            continue
            
        
        file_chunks = process_controller.process_file_content(file_content=file_content, 
                                                            file_id=file_id, 
                                                            chunk_size=chunk_size, 
                                                            overlap_size=overlap_size)
        
        if file_chunks is None or len(file_chunks) == 0:
            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST,
                                content={"success": False, 
                                        "message": ResponseStatus.PROCESSING_FAILED.value})

        file_chunks_record = [
            DataChunk(
                chunk_text=chunk.page_content,
                chunk_metadata=chunk.metadata,
                chunk_order=i+1,
                chunk_project_id=project.id,
                chunk_asset_id=asset_id
            )
            for i, chunk in enumerate(file_chunks)
        ]    
                
        inserted_count += await chunk_model.insert_many_chunks(chunks=file_chunks_record)
        num_files += 1
    
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"success": True,
                                 "message": ResponseStatus.PROCESSING_SUCCESS.value,
                                 "inserted_chunks": inserted_count,
                                 "processed_files": num_files})