from dataclasses import dataclass

from .status import SyncStatus

@dataclass
class ReportRow:
    date_str: str
    name: str
    url: str
    status: str

@dataclass
class SyncResult:
    date_str: str
    name: str
    reporting_name: str
    status: SyncStatus
    message: str

    def to_list(self):
        return [
            self.date_str,
            self.name,
            self.reporting_name,
            self.status.value,
            self.message,
        ]