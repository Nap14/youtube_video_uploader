from abc import ABC, abstractmethod
from typing import Optional, Callable

from src.core.context import AppContext

class BaseProcessor(ABC):
    def __init__(self, ctx: AppContext, error_cb: Optional[Callable[[str, str], None]] = None):
        self.ctx = ctx
        self.error_cb = error_cb

    @abstractmethod
    def process(self, progress_cb: Optional[Callable[[str, tuple], None]] = None):
        """Main entry point for the processor logic."""
        pass

    def _report_error(self, title: str, message: str):
        self.ctx.logger.error(f"{title}: {message}")
        if self.error_cb:
            self.error_cb(title, message)
