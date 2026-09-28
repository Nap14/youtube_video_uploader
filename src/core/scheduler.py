import threading
from datetime import datetime
from typing import Optional, Callable, Dict, Any

from src.core.logger import Logger

class SchedulerService:
    def __init__(self, config: Dict[str, Any], trigger_task_cb: Callable, logger: Logger):
        self.config = config
        self.trigger_cb = trigger_task_cb
        self.logger = logger
        self.stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self.last_run: Optional[Any] = None

    def start(self):
        if self._thread is not None and self._thread.is_alive():
            return
            
        self.stop_event.clear()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.stop_event.set()
        if self._thread:
            self._thread.join()

    def _loop(self):
        while not self.stop_event.is_set():
            if self._should_run():
                self._trigger_safely()
            self.stop_event.wait(30)

    def _trigger_safely(self):
        try:
            mode = str(self.config.get("mode", "1"))
            self.trigger_cb(mode)
        except Exception as e:
            self.logger.error(f"Scheduler execution error: {e}")

    def _should_run(self) -> bool:
        if not self.config.get("enabled", False):
            return False
        freq = str(self.config.get("frequency"))
        handlers = {
            "hourly": self._should_run_hourly,
            "daily": self._should_run_daily,
            "weekly": self._should_run_weekly,
        }
        
        handler = handlers.get(freq)
        if not handler:
            return False
            
        return handler()

    def _should_run_hourly(self) -> bool:
        now = datetime.now()
        interval = int(self.config.get("interval", 1))
        
        if self.last_run is None:
            self.last_run = now
            return True
            
        if (now - self.last_run).total_seconds() >= interval * 3600:
            self.last_run = now
            return True
            
        return False

    def _should_run_daily(self) -> bool:
        now = datetime.now()
        target_time = self.config.get("time", "20:00")
        
        if now.strftime("%H:%M") != target_time:
            return False
            
        if self.last_run == now.date():
            return False
            
        self.last_run = now.date()
        return True

    def _should_run_weekly(self) -> bool:
        now = datetime.now()
        target_day = self.config.get("day", "Monday")
        target_time = self.config.get("time", "20:00")
        
        if now.strftime("%A") != target_day:
            return False
            
        if now.strftime("%H:%M") != target_time:
            return False
            
        if self.last_run == now.date():
            return False
            
        self.last_run = now.date()
        return True
