using System;
using System.Drawing;
using System.Windows.Forms;
using Microsoft.Win32;
using System.IO;
using System.Runtime.InteropServices;

namespace BreakReminder
{
    static class Program
    {
        [DllImport("winmm.dll", SetLastError = true)]
        static extern bool PlaySound(string pszSound, IntPtr hmod, uint fdwSound);
        
        const uint SND_ALIAS = 0x00010000;
        const uint SND_ASYNC = 0x0001;
        const uint SND_LOOP = 0x0008;

        static NotifyIcon trayIcon;
        static ContextMenu trayMenu;
        static System.Windows.Forms.Timer timer;
        static int intervalMinutes = 20;
        static DateTime nextBreak;
        static string configPath = "config.txt";

        [STAThread]
        static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            
            LoadConfig();
            
            trayMenu = new ContextMenu();
            trayMenu.Popup += TrayMenu_Popup;
            
            trayIcon = new NotifyIcon();
            trayIcon.Text = "Break Reminder";
            trayIcon.Icon = CreateIcon();
            
            UpdateMenu();
            
            trayIcon.ContextMenu = trayMenu;
            trayIcon.Visible = true;
            
            timer = new System.Windows.Forms.Timer();
            timer.Interval = 1000;
            timer.Tick += Timer_Tick;
            nextBreak = DateTime.Now.AddMinutes(intervalMinutes);
            timer.Start();
            
            Application.Run();
        }

        static void TrayMenu_Popup(object sender, EventArgs e)
        {
            UpdateMenu();
        }

        static void UpdateMenu()
        {
            trayMenu.MenuItems.Clear();
            
            TimeSpan remaining = nextBreak - DateTime.Now;
            if (remaining.TotalSeconds < 0) remaining = TimeSpan.Zero;
            string remainingText = string.Format("Next break in: {0}m {1}s", remaining.Minutes, remaining.Seconds);
            
            MenuItem timeItem = new MenuItem(remainingText);
            timeItem.Enabled = false;
            
            MenuItem settingsItem = new MenuItem("Settings", OnSettings);
            
            MenuItem autoStartItem = new MenuItem("Auto Start with Windows", OnAutoStart);
            autoStartItem.Checked = IsAutoStartEnabled();
            
            MenuItem exitItem = new MenuItem("Quit", OnExit);
            
            trayMenu.MenuItems.Add(timeItem);
            trayMenu.MenuItems.Add("-");
            trayMenu.MenuItems.Add(settingsItem);
            trayMenu.MenuItems.Add(autoStartItem);
            trayMenu.MenuItems.Add(exitItem);
        }

        static void Timer_Tick(object sender, EventArgs e)
        {
            TimeSpan remaining = nextBreak - DateTime.Now;
            if (remaining.TotalSeconds <= 0)
            {
                timer.Stop();
                PlaySound("SystemHand", IntPtr.Zero, SND_ALIAS | SND_ASYNC | SND_LOOP);
                
                MessageBox.Show(
                    string.Format("You have been working for {0} minutes. Please take a break, rest your eyes and stretch.", intervalMinutes),
                    "Time for a Break!",
                    MessageBoxButtons.OK,
                    MessageBoxIcon.Information,
                    MessageBoxDefaultButton.Button1,
                    MessageBoxOptions.DefaultDesktopOnly);
                    
                PlaySound(null, IntPtr.Zero, 0); // Stop
                
                nextBreak = DateTime.Now.AddMinutes(intervalMinutes);
                timer.Start();
            }
            else
            {
                string remainingText = string.Format("Next break in: {0}m {1}s", remaining.Minutes, remaining.Seconds);
                trayIcon.Text = remainingText.Substring(0, Math.Min(63, remainingText.Length));
            }
        }

        static void OnSettings(object sender, EventArgs e)
        {
            Form prompt = new Form()
            {
                Width = 300,
                Height = 150,
                FormBorderStyle = FormBorderStyle.FixedDialog,
                Text = "Settings",
                StartPosition = FormStartPosition.CenterScreen,
                MaximizeBox = false,
                MinimizeBox = false
            };
            Label textLabel = new Label() { Left = 20, Top = 20, Text = "Enter break interval (minutes):", Width = 250 };
            NumericUpDown inputBox = new NumericUpDown() { Left = 20, Top = 50, Width = 100, Minimum = 1, Maximum = 1440, Value = intervalMinutes };
            Button confirmation = new Button() { Text = "OK", Left = 150, Width = 100, Top = 50, DialogResult = DialogResult.OK };
            prompt.Controls.Add(textLabel);
            prompt.Controls.Add(inputBox);
            prompt.Controls.Add(confirmation);
            prompt.AcceptButton = confirmation;

            if (prompt.ShowDialog() == DialogResult.OK)
            {
                intervalMinutes = (int)inputBox.Value;
                SaveConfig();
                nextBreak = DateTime.Now.AddMinutes(intervalMinutes);
                MessageBox.Show(string.Format("Reminder interval set to {0} minutes.", intervalMinutes), "Settings Saved", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
        }

        static void LoadConfig()
        {
            try
            {
                if (File.Exists(configPath))
                {
                    string txt = File.ReadAllText(configPath);
                    int val;
                    if (int.TryParse(txt.Trim(), out val))
                    {
                        intervalMinutes = val;
                    }
                }
            }
            catch { }
        }

        static void SaveConfig()
        {
            try
            {
                File.WriteAllText(configPath, intervalMinutes.ToString());
            }
            catch { }
        }

        static bool IsAutoStartEnabled()
        {
            try
            {
                using (RegistryKey key = Registry.CurrentUser.OpenSubKey(@"Software\Microsoft\Windows\CurrentVersion\Run", false))
                {
                    if (key != null)
                    {
                        object val = key.GetValue("BreakReminder");
                        if (val != null)
                        {
                            return val.ToString() == Application.ExecutablePath;
                        }
                    }
                }
            }
            catch { }
            return false;
        }

        static void OnAutoStart(object sender, EventArgs e)
        {
            try
            {
                using (RegistryKey key = Registry.CurrentUser.OpenSubKey(@"Software\Microsoft\Windows\CurrentVersion\Run", true))
                {
                    if (IsAutoStartEnabled())
                    {
                        key.DeleteValue("BreakReminder", false);
                    }
                    else
                    {
                        key.SetValue("BreakReminder", Application.ExecutablePath);
                    }
                }
            }
            catch { }
        }

        static void OnExit(object sender, EventArgs e)
        {
            trayIcon.Visible = false;
            Application.Exit();
        }

        static Icon CreateIcon()
        {
            Bitmap bmp = new Bitmap(64, 64);
            using (Graphics g = Graphics.FromImage(bmp))
            {
                g.Clear(Color.FromArgb(76, 175, 80)); // #4CAF50
                g.FillEllipse(Brushes.White, 16, 16, 32, 32);
            }
            IntPtr hIcon = bmp.GetHicon();
            return Icon.FromHandle(hIcon);
        }
    }
}
