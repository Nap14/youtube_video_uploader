from typing import Optional, Protocol

class UIHandler(Protocol):
    def show_error(self, title: str, message: str) -> None: ...
    def show_info(self, title: str, message: str) -> None: ...

class UIService:
    _handler: Optional[UIHandler] = None

    @classmethod
    def set_handler(cls, handler: UIHandler) -> None:
        cls._handler = handler

    @classmethod
    def error(cls, title: str, message: str) -> None:
        if cls._handler:
            cls._handler.show_error(title, message)
        else:
            print(f"[ERROR] {title}: {message}")

    @classmethod
    def info(cls, title: str, message: str) -> None:
        if cls._handler:
            cls._handler.show_info(title, message)
        else:
            print(f"[INFO] {title}: {message}")
