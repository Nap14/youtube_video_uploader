from enum import Enum

class SyncStatus(Enum):
    PASS = "pass"
    FAIL = "fail"
    SKIPPED = "skipped"