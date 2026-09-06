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
import subprocess
import shlex

CONFIG_FILE = "config.json"
APP_NAME = "BreakReminder"
DEFAULT_INTERVAL = 20

def get_app_path():
    if getattr(sys, 'frozen', False):
        return sys.executable
    python_exe = sys.executable
    script_path = os.path.abspath(__file__)
    pythonw_exe = python_exe.replace("python.exe", "pythonw.exe")
    if os.path.exists(pythonw_exe):
        return f'{pythonw_exe} "{script_path}"'
    return f'{python_exe} "{script_path}"'

def show_settings_dialog(current_interval):
    # This runs in a completely separate process to avoid tkinter threading freezes
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    
    new_interval = simpledialog.askinteger("Settings", "Enter break interval (minutes):", initialvalue=current_interval, minvalue=1, maxvalue=1440, parent=root)
    
    if new_interval is not None:
        config = {"interval": new_interval}
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)
        
        notification.notify(
            title="Settings Saved",
            message=f"Reminder interval set to {new_interval} minutes.",
            app_name=APP_NAME,
            timeout=5
        )
    root.destroy()

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
        except Exception:
            pass

    def open_settings(self, icon, item):
        # Launch settings in a new process
        app_path = get_app_path()
        if getattr(sys, 'frozen', False):
            subprocess.Popen([app_path, "--settings"])
        else:
            args = shlex.split(app_path) + ["--settings"]
            subprocess.Popen(args)
        
        # We need to reload config after they close the dialog.
        # We can poll it or just let the background loop pick it up.
        # It's easier to just poll the config file for changes in the reminder loop.

    def quit_app(self, icon, item):
        self.running = False
        icon.stop()

    def create_image(self):
        width = 64
        height = 64
        color1 = "#4CAF50"
        color2 = "white"
        
        image = Image.new('RGB', (width, height), color1)
        dc = ImageDraw.Draw(image)
        dc.ellipse(
            (width // 4, height // 4, width * 3 // 4, height * 3 // 4),
            fill=color2
        )
        return image

    def reminder_loop(self):
        last_reminded = time.time()
        last_config_check = time.time()
        
        while self.running:
            time.sleep(1)
            if not self.running:
                break
            
            # Check for config changes every 2 seconds
            if time.time() - last_config_check > 2:
                self.load_config()
                last_config_check = time.time()
                
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
    if len(sys.argv) > 1 and sys.argv[1] == "--settings":
        # We are just showing the settings dialog
        interval = DEFAULT_INTERVAL
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    interval = json.load(f).get("interval", DEFAULT_INTERVAL)
            except Exception:
                pass
        show_settings_dialog(interval)
    else:
        app = BreakReminderApp()
        app.run()
