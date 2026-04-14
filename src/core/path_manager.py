import os
from dataclasses import dataclass
from src.services.file_utils import get_base_dir

@dataclass(frozen=True)
class AppPaths:
    base_dir: str
    configs_dir: str
    config_file: str
    schedule_file: str
    secrets_file: str
    token_file: str
    reports_dir: str

class PathManager:
    def __init__(self, entry_file: str):
        base = get_base_dir(entry_file)
        configs = os.path.join(base, "configs")
        
        self._paths = AppPaths(
            base_dir=base,
            configs_dir=configs,
            config_file=os.path.join(configs, "config.json"),
            schedule_file=os.path.join(configs, "schedule.json"),
            secrets_file=os.path.join(configs, "client_secret.json"),
            token_file=os.path.join(configs, "token.json"),
            reports_dir=os.path.join(base, "reports")
        )

    def get_paths(self) -> AppPaths:
        return self._paths

    def ensure_dirs(self) -> None:
        os.makedirs(self._paths.configs_dir, exist_ok=True)
        os.makedirs(self._paths.reports_dir, exist_ok=True)
