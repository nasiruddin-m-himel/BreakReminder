# Break Reminder

A simple Windows system tray application that reminds you to take a break at customizable intervals.

## Features
- Sits in the system tray.
- Toast notifications to remind you to take a break.
- Configurable interval via a simple GUI.
- Option to automatically start with Windows.

## Requirements
- Python 3
- `pystray`
- `Pillow`
- `plyer`

## Installation
1. Clone this repository.
2. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## Usage
- The app will start minimized in the system tray.
- Right-click the tray icon to access the menu.
- Click "Settings" to change the reminder interval.
- Check "Auto Start" to have the app launch automatically when Windows starts.
- Click "Quit" to exit the application.
