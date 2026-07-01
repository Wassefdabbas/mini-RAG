from fastapi import FastAPI, APIRouter
import os

base_router = APIRouter(
    prefix="/api/v1",
    tags=["Health & System"],
)

@base_router.get("/health")
async def health_check():
    app_name = os.getenv("APP_NAME")
    app_version = os.getenv("APP_VERSION")
    
    return {
        "status": "healthy",
        "app_name": app_name,
        "app_version": app_version
    }