# Break Reminder

A lightweight, native Windows system tray application (only 9 KB!) that reminds you to take a break at customizable intervals. 

## Features

- **Ultra Lightweight:** Written in pure C# (WinForms), requiring no external dependencies. The executable is under 10 KB.
- **System Tray Integration:** Sits quietly in your system tray (notification area).
- **Live Tooltip:** Hover over the tray icon to see exactly how much time is left until your next break.
- **Continuous Alerts:** When it's time for a break, a window pops up and a system alert sound plays on a continuous loop until you dismiss it—so you can't miss it!
- **Customizable Intervals:** Easily change the break interval via a simple right-click settings menu.
- **Auto-Start:** Option to automatically start the app when Windows boots.
- **Native Installer:** Comes with a tiny standalone installer that adds the app to your Start Menu for easy searching.

## Installation

1. Go to the [Releases](https://github.com/nasiruddin-m-himel/BreakReminder/releases) page.
2. Download `BreakReminder_Setup.exe`.
3. Run the setup file. It will automatically install the app, add it to your Start Menu, and start the timer.

## Building from Source

You do not need Visual Studio to build this project. You can compile it using the C# compiler (`csc.exe`) built directly into Windows.

Open PowerShell or Command Prompt in the project directory and run:

```cmd
C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe /target:winexe /out:BreakReminder.exe Program.cs
```
