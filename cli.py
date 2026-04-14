import os
from src.core.config import Config
from src.core.path_manager import PathManager
from src.core.context import AppContext
from src.services.schedule_utils import load_schedule
from src.services.cli_handler import CliHandler
from src.services.console_loger import ConsoleLogger
from src.constants import ERRORS, APP_TITLE

def main():
    print(f"\n=== {APP_TITLE} (Terminal Version) ===\n")
    
    pm = PathManager(__file__)
    pm.ensure_dirs()
    paths = pm.get_paths()

    if not os.path.exists(paths.secrets_file):
        print(f"[ERROR] {ERRORS['NO_SECRETS']} (expected at {paths.configs_dir})")
        return

    config = Config(paths.config_file, paths.reports_dir)
    schedule = load_schedule(paths.schedule_file)
    
    ctx = AppContext(
        config=config, 
        schedule=schedule, 
        paths=paths, 
        logger=ConsoleLogger()
    )

    choice = CliHandler.get_mode_choice()
    if not choice or choice == 'Q':
        return

    CliHandler.run_automation(ctx, choice)

if __name__ == "__main__":
    main()
