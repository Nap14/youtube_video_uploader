import threading
import pystray
from PIL import Image, ImageDraw

class TrayManager:
    def __init__(self, app, exit_cmd):
        self.app = app
        self.exit_cmd = exit_cmd
        self.icon = None
        self.setup_tray()

    def setup_tray(self):
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
        self.icon.stop()
        self.exit_cmd()

    def stop(self):
        if self.icon: self.icon.stop()
