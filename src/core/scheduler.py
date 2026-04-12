import time
import threading
from datetime import datetime

class SchedulerService:
    def __init__(self, config, trigger_task_cb):
        self.config = config
        self.trigger_cb = trigger_task_cb
        self.running = False
        self.last_run = None
        self._thread = None

    def start(self):
        if self.running: return
        self.running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self.running = False

    def _loop(self):
        while self.running:
            p_cfg = self.config.get_planner_config()
            if p_cfg.get("enabled"):
                if self._should_run(p_cfg):
                    self.trigger_cb(p_cfg.get("mode", "1"))
                    self.last_run = datetime.now().date()
            time.sleep(60)

    def _should_run(self, cfg):
        now = datetime.now()
        freq = cfg.get("frequency")
        
        if freq == "hourly":
            interval = int(cfg.get("interval", 1))
            if self.last_run is None or (now - self.last_run).total_seconds() >= interval * 3600:
                self.last_run = now # Store datetime for hourly
                return True
        elif freq == "daily":
            target_time = cfg.get("time", "20:00")
            if now.strftime("%H:%M") == target_time:
                if self.last_run != now.date(): return True
        elif freq == "weekly":
            target_day = cfg.get("day", "Monday")
            target_time = cfg.get("time", "20:00")
            if now.strftime("%A") == target_day and now.strftime("%H:%M") == target_time:
                if self.last_run != now.date(): return True
        return False
