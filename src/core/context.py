from dataclasses import dataclass
from typing import Dict, Any

from src.core.config import Config
from src.core.path_manager import AppPaths
from src.core.logger import Logger

@dataclass
class AppContext:
    config: Config
    schedule: Dict[str, Any]
    paths: AppPaths
    logger: Logger
