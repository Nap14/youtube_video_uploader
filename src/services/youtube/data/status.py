from enum import Enum

class UploadStatus(Enum):
    SUCCESS = "success"
    FAIL = "fail"
    SKIPPED = "skipped"
    ALREADY_UPLOADED = "already_uploaded"
