import customtkinter as ctk
from src.core.context import AppContext

class BaseFrame(ctk.CTkFrame):
    def __init__(self, master, ctx: AppContext, **kwargs):
        super().__init__(master, **kwargs)
        self.ctx = ctx
        self._create_widgets()

    def _create_widgets(self):
        """Must be implemented by child classes to build UI."""
        raise NotImplementedError("Subclasses must implement _create_widgets")

    def refresh(self):
        """Optional: Implement in child classes to update data on view."""
        pass
