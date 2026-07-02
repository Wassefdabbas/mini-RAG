from fastapi import FastAPI, APIRouter, Depends
from src.helpers.config import get_settings, Settings

base_router = APIRouter(
    prefix="/api/v1",
    tags=["Health & System"],
)

@base_router.get("/health")
async def health_check(app_settings: Settings = Depends(get_settings)): 
    
    app_name = app_settings.APP_NAME
    app_version = app_settings.APP_VERSION
    
    return {
        "status": "healthy",
        "app_name": app_name,
        "app_version": app_version
    }