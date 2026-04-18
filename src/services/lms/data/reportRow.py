from dataclasses import dataclass
from typing import Optional, List, Any, Union
from pydantic import BaseModel, Field, ConfigDict

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
    model_config = ConfigDict(extra='allow')
    url: Optional[str] = None


class Button(BaseModel):
    model_config = ConfigDict(extra='allow')
    label: Optional[str] = None
    link: Optional[Link] = None


class Data(BaseModel):
    model_config = ConfigDict(extra='allow')
    button: Optional[Button] = None


class Element(BaseModel):
    model_config = ConfigDict(extra='allow')
    data: Union[Data, List[Any], None] = None


class Wrapper(BaseModel):
    model_config = ConfigDict(extra='allow')
    element: Optional[Element] = None


class ContentObject(BaseModel):
    model_config = ConfigDict(extra='allow')
    content: List[Wrapper] = Field(default_factory=list)

