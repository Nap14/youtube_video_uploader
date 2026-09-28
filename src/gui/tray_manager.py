import sys
import threading
from PIL import Image, ImageDraw

class TrayManager:
    def __init__(self, app, exit_cmd):
        self.app = app
        self.exit_cmd = exit_cmd
        self.icon = None

        # On macOS, pystray runs Cocoa NSApplication on a background thread,
        # which triggers an immediate OS SIGTRAP/BPT trap abort because AppKit
        # strictly forbids NSApplication on secondary threads (and Tkinter owns the main thread).
        if sys.platform == "darwin":
            return

        try:
            self.setup_tray()
        except Exception as e:
            print(f"[WARN] Tray initialization failed: {e}")
            self.icon = None

    def is_active(self) -> bool:
        return self.icon is not None

    def setup_tray(self):
        try:
            import pystray
        except ImportError:
            return

        icon_img = Image.new('RGB', (64, 64), color=(31, 119, 180))
        d = ImageDraw.Draw(icon_img)
        d.rectangle([16, 16, 48, 48], fill="white")
        
        menu = (pystray.MenuItem('Open', self.show_window), 
                pystray.MenuItem('Exit', self.exit_app))
        self.icon = pystray.Icon("ZoomUploader", icon_img, "Zoom Uploader", menu)
        threading.Thread(target=self.icon.run, daemon=True).start()

    def show_window(self):
        self.app.after(0, self.app.deiconify)

    def exit_app(self):
        if self.icon:
            try:
                self.icon.stop()
            except Exception:
                pass
        self.exit_cmd()

    def stop(self):
        if self.icon:
            try:
                self.icon.stop()
            except Exception:
                pass
