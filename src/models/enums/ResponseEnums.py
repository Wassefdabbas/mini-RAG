from enum import Enum

class ResponseStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    FILE_TYPE_NOT_SUPPORTED = "File type is not allowed."
    FILE_SIZE_EXCEEDS_LIMIT = "File size exceeds the maximum limit of MB."
    FILE_UPLOAD_SUCCESS = "File uploaded successfully."
    FILE_UPLOAD_FAILED = "File upload failed."
    PROCESSING_SUCCESS = "File processed successfully."
    PROCESSING_FAILED = "File processing failed."