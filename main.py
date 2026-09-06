import tkinter as tk
from tkinter import simpledialog
import pystray
from PIL import Image, ImageDraw
from plyer import notification
import threading
import time
import json
import os
import sys
import winreg

CONFIG_FILE = "config.json"
APP_NAME = "BreakReminder"
DEFAULT_INTERVAL = 20

def get_app_path():
    # If running as PyInstaller executable
    if getattr(sys, 'frozen', False):
        return sys.executable
    # If running as a script, use pythonw or python to run it
    # We'll just return the script path. But ideally, it should be launched with pythonw to avoid console.
    # We will register it as: pythonw "c:\...\main.py"
    # Actually, sys.executable gives python path. Let's form a string.
    python_exe = sys.executable
    script_path = os.path.abspath(__file__)
    # Use pythonw if available, else python
    pythonw_exe = python_exe.replace("python.exe", "pythonw.exe")
    if os.path.exists(pythonw_exe):
        return f'"{pythonw_exe}" "{script_path}"'
    return f'"{python_exe}" "{script_path}"'

class BreakReminderApp:
    def __init__(self):
        self.interval = DEFAULT_INTERVAL
        self.running = True
        self.load_config()
        
        self.icon = None
        self.timer_thread = threading.Thread(target=self.reminder_loop, daemon=True)
        self.timer_thread.start()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    config = json.load(f)
                    self.interval = config.get("interval", DEFAULT_INTERVAL)
            except Exception:
                pass
                
    def save_config(self):
        config = {"interval": self.interval}
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)

    def is_auto_start_enabled(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, APP_NAME)
            winreg.CloseKey(key)
            return value == get_app_path()
        except FileNotFoundError:
            return False

    def toggle_auto_start(self, icon, item):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            if self.is_auto_start_enabled():
                winreg.DeleteValue(key, APP_NAME)
            else:
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, get_app_path())
            winreg.CloseKey(key)
        except Exception as e:
            pass

    def open_settings(self, icon, item):
        # We need a tkinter root to show dialogs
        root = tk.Tk()
        root.withdraw() # Hide the main window
        root.attributes('-topmost', True) # Bring to front
        
        new_interval = simpledialog.askinteger("Settings", "Enter break interval (minutes):", initialvalue=self.interval, minvalue=1, maxvalue=1440, parent=root)
        if new_interval is not None:
            self.interval = new_interval
            self.save_config()
            notification.notify(
                title="Settings Saved",
                message=f"Reminder interval set to {self.interval} minutes.",
                app_name=APP_NAME,
                timeout=5
            )
        root.destroy()

    def quit_app(self, icon, item):
        self.running = False
        icon.stop()

    def create_image(self):
        # Generate a simple icon
        width = 64
        height = 64
        color1 = "#4CAF50" # Green background
        color2 = "white"   # White center
        
        image = Image.new('RGB', (width, height), color1)
        dc = ImageDraw.Draw(image)
        # Draw a plus or a cup? Let's just draw a clock-like circle
        dc.ellipse(
            (width // 4, height // 4, width * 3 // 4, height * 3 // 4),
            fill=color2
        )
        return image

    def reminder_loop(self):
        last_reminded = time.time()
        while self.running:
            time.sleep(1)
            if not self.running:
                break
                
            elapsed_minutes = (time.time() - last_reminded) / 60.0
            if elapsed_minutes >= self.interval:
                try:
                    notification.notify(
                        title="Time for a Break!",
                        message=f"You have been working for {self.interval} minutes. Rest your eyes and stretch.",
                        app_name=APP_NAME,
                        timeout=10
                    )
                except Exception as e:
                    print("Error showing notification:", e)
                last_reminded = time.time()

    def run(self):
        menu = pystray.Menu(
            pystray.MenuItem("Settings", self.open_settings),
            pystray.MenuItem("Auto Start with Windows", self.toggle_auto_start, checked=lambda item: self.is_auto_start_enabled()),
            pystray.MenuItem("Quit", self.quit_app)
        )
        self.icon = pystray.Icon("break_reminder", self.create_image(), "Break Reminder", menu)
        self.icon.run()

if __name__ == "__main__":
    app = BreakReminderApp()
    app.run()
