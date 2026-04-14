from dataclasses import dataclass
from typing import Optional, List
from pydantic import BaseModel, Field

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


class Link(BaseModel):
    url: Optional[str] = None


class Button(BaseModel):
    label: Optional[str] = None
    link: Optional[Link] = None


class Data(BaseModel):
    button: Optional[Button] = None


class Element(BaseModel):
    data: Optional[Data] = None


class Wrapper(BaseModel):
    element: Optional[Element] = None


class ContentObject(BaseModel):
    content: List[Wrapper] = Field(default_factory=list)

