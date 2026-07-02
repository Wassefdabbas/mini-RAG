from src.helpers.config import get_settings, Settings
import os
import random
import string

class BaseController:
    def __init__(self):
        self.app_settings = get_settings()

        # 1. get controllers path
        controllers_dir = os.path.dirname(__file__) 
        
        # 2. go to src
        src_dir = os.path.dirname(controllers_dir)
        
        # 3. go to project root where assets and README live
        self.base_dir = os.path.dirname(src_dir)
        
        # 4. specify the actual and dynamic path to the assets directory
        self.files_dir = os.path.join(self.base_dir, "assets/files")
        
    def generate_random_string(self, length: int = 12):
        letters = string.ascii_letters + string.digits
        return ''.join(random.choices(letters, k=length))