import threading
from datetime import datetime


class SchedulerService:
    def __init__(self, config, trigger_task_cb):
        self.config = config.get_planner_config()
        self.trigger_cb = trigger_task_cb

        self.stop_event = threading.Event()
        self._thread = None
        self.last_run = None

    def start(self):
        if self._thread is None or not self._thread.is_alive():
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
                try:
                    self.trigger_cb()
                except Exception as e:
                    print(f"[Scheduler error] {e}")

            self.stop_event.wait(30)


    def _should_run(self):
        freq = self.config.get("frequency")

        handlers = {
            "hourly": self._should_run_hourly,
            "daily": self._should_run_daily,
            "weekly": self._should_run_weekly,
        }

        handler = handlers.get(freq)
        if not handler:
            return False

        return handler()


    def _should_run_hourly(self):
        now = datetime.now()
        interval = int(self.config.get("interval", 1))

        if self.last_run is None:
            self.last_run = now
            return True

        if (now - self.last_run).total_seconds() >= interval * 3600:
            self.last_run = now
            return True

        return False


    def _should_run_daily(self):
        now = datetime.now()
        target_time = self.config.get("time", "20:00")

        if now.strftime("%H:%M") != target_time:
            return False

        if self.last_run != now.date():
            self.last_run = now.date()
            return True

        return False


    def _should_run_weekly(self):
        now = datetime.now()
        target_day = self.config.get("day", "Monday")
        target_time = self.config.get("time", "20:00")

        if now.strftime("%A") != target_day:
            return False

        if now.strftime("%H:%M") != target_time:
            return False

        if self.last_run != now.date():
            self.last_run = now.date()
            return True

        return False

