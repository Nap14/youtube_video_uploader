from src.core.path_manager import PathManager
from src.core.config import Config
from src.core.context import AppContext
from src.gui.app import GuiApp
from src.services.schedule_utils import load_schedule
from src.services.bootstrapper import Bootstrapper
from src.services.console_loger import ConsoleLogger

def main():
    pm = PathManager(__file__)
    pm.ensure_dirs()
    paths = pm.get_paths()

    if not Bootstrapper.validate_gui_env(paths):
        return

    config = Config(paths.config_file, paths.reports_dir)
    schedule = load_schedule(paths.schedule_file)
    
    ctx = AppContext(
        config=config, 
        schedule=schedule, 
        paths=paths, 
        logger=ConsoleLogger()
    )

    app = GuiApp(ctx)
    app.mainloop()

if __name__ == "__main__":
    main()
