from dataclasses import dataclass
from .status import UploadStatus

@dataclass
class UploadResult:
    date_str: str
    name: str
    url: str
    status: UploadStatus
    message: str = ""

    def to_list(self):
        status_msg = self.status.value
        if self.message:
            status_msg = f"{self.status.value}: {self.message}"
            
        return [
            self.date_str,
            self.name,
            self.url,
            status_msg
        ]
