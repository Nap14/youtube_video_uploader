from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Any, Union

class Link(BaseModel):
    model_config = ConfigDict(extra='allow')
    url: Optional[str] = None
    type: str = "link"
    selectedTariffs: List[Any] = Field(default_factory=list)

class ButtonBase(BaseModel):
    model_config = ConfigDict(extra='allow')
    color: List[str] = Field(default_factory=lambda: ["#ffffff"])
    background: List[str] = Field(default_factory=lambda: ["#2559aa"])
    borderColor: List[str] = Field(default_factory=lambda: ["rgba(255, 255, 255, 0)"])
    borderStyle: str = "solid"
    borderWidth: int = 2
    borderRadius: int = 8

class Button(BaseModel):
    model_config = ConfigDict(extra='allow')
    label: Optional[str] = None
    link: Optional[Link] = None
    size: str = "M"
    styleType: str = "custom"
    widthType: str = "full"
    buttonBase: Optional[ButtonBase] = None
    widthValue: int = 260
    isTargetBlank: bool = True

class Data(BaseModel):
    model_config = ConfigDict(extra='allow')
    button: Optional[Button] = None
    horizontalAlign: str = "L"
    horizontalIndent: str = "M"
    content: Optional[str] = None
    files: Optional[List[Any]] = None
    image: Optional[dict] = None

class Element(BaseModel):
    model_config = ConfigDict(extra='allow')
    id: Optional[str] = ""
    name: Optional[str] = None
    label: Optional[str] = None
    data: Optional[Union[Data, dict, List[Any]]] = None

class Wrapper(BaseModel):
    model_config = ConfigDict(extra='allow')
    id: Optional[str] = ""
    data: List[Any] = Field(default_factory=list)
    styles: Optional[dict] = Field(default_factory=lambda: {
        "background": "#ffffff",
        "paddingTop": "10px",
        "paddingLeft": "10px",
        "borderRadius": "0px",
        "paddingRight": "10px",
        "paddingBottom": "15px"
    })
    element: Optional[Element] = None

class ContentObject(BaseModel):
    model_config = ConfigDict(extra='allow')
    content: List[Wrapper] = Field(default_factory=list)

class ReportRow:
    def __init__(self, date_str: str, name: str, url: str, folder: str = ""):
        self.date_str = date_str
        self.name = name
        self.url = url
        self.folder = folder

class SyncResult:
    def __init__(self, date: str, course_name: str, lesson_title: str, status: Any, details: str):
        self.date = date
        self.course_name = course_name
        self.lesson_title = lesson_title
        self.status = status
        self.details = details

    def to_list(self) -> List[str]:
        return [self.date, self.course_name, self.lesson_title, str(self.status), self.details]
