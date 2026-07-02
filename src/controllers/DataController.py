from .BaseController import BaseController
from fastapi import UploadFile
from src.models import ResponseStatus
from .ProjectController import ProjectController
import os
import re

class DataController(BaseController):

    def __init__(self):
        super().__init__()
        
    def validate_file(self, file: UploadFile):
        # Validate file type
        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES:
            return {"success": False, "message": ResponseStatus.FILE_TYPE_NOT_SUPPORTED.value}

        # Validate file size
        if file.size > self.app_settings.FILE_MAX_SIZE * 1024 * 1024: #convert MB to bytes
            return {"success": False, "message": ResponseStatus.FILE_SIZE_EXCEEDS_LIMIT.value}

        
        return {"success": True, "message": ResponseStatus.FILE_UPLOAD_SUCCESS.value}
    

    def generate_unique_filepath(self, original_filename: str, project_id: str):
        random_key = self.generate_random_string()
        project_path = ProjectController().get_project_path(project_id=project_id)
        
        clean_filename = self.get_clean_filename(original_filename)
        
        new_file_path = os.path.join(project_path, f"{random_key}_{clean_filename}")
        
        while os.path.exists(new_file_path):
            random_key = self.generate_random_string()
            new_file_path = os.path.join(project_path, 
                                         random_key + "_" + clean_filename)
        
        return new_file_path, random_key + "_" + clean_filename
    
    
    def get_clean_filename(self, original_filename: str):
        # Remove any unwanted characters from the filename except underscores, dots
        clean_filename = re.sub(r'[^\w\.]', '', original_filename.strip())
        
        # Replace spaces with underscores
        clean_filename = clean_filename.replace(' ', '_')
        return clean_filename
        