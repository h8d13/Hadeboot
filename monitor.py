#!/usr/bin/env python3
import sys
import psutil
import json
import os
from ctypes import CDLL, c_int, byref
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPainter, QColor, QPixmap, QClipboard
from PyQt6.QtCore import QTimer, Qt, QMimeData, QSize
import subprocess

## Added ASM clock. Added time offset default 1
## Clipboard, system metrics, Notifications Tray UI + config
## 100ms refresh, 2 seconds on system metrics 

class ClipboardManager:
    def __init__(self, max_history=10):
        self.clipboard = QApplication.clipboard()
        self.history = []
        self.max_history = max_history
        self.clipboard.dataChanged.connect(self.clipboard_changed)
        
    def clipboard_changed(self):
        mime_data = self.clipboard.mimeData()
        if mime_data.hasText():
            text = mime_data.text()
            if text and text not in self.history:
                self.history.insert(0, text)
                if len(self.history) > self.max_history:
                    self.history.pop()
                if QSystemTrayIcon.supportsMessages():
                    tray = QApplication.instance().tray
                    tray.showMessage("Clipboard", f"Copied: {text[:50]}..." if len(text) > 50 else text,
                                   QSystemTrayIcon.MessageIcon.Information, 2000)
                    tray.update_clipboard_menu()

class SystemMetrics:
    def __init__(self):
        self.cpu = 0.0
        self.ram = 0.0
        self.swap = 0.0
        self.disk = 0.0
        self.ram_used = ""
        self.ram_total = ""
        self.swap_used = ""
        self.swap_total = ""
        self.net_send = ""
        self.net_recv = ""
        self._last_net_io = psutil.net_io_counters()
        self._last_time = psutil.boot_time()

    def _get_size_str(self, bytes):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes < 1024:
                return f"{bytes:.1f}{unit}"
            bytes /= 1024
        return f"{bytes:.1f}PB"

    @staticmethod
    def get_current_metrics():
        metrics = SystemMetrics()
        metrics.cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        metrics.ram = memory.percent
        metrics.ram_used = metrics._get_size_str(memory.used)
        metrics.ram_total = metrics._get_size_str(memory.total)
        swap = psutil.swap_memory()
        metrics.swap = swap.percent
        metrics.swap_used = metrics._get_size_str(swap.used)
        metrics.swap_total = metrics._get_size_str(swap.total)
        metrics.disk = psutil.disk_usage('/').percent
        return metrics
   
    def get_status(self):
        if (self.cpu < 45.0 and self.ram < 50.0 and 
            self.swap < 50.0 and self.disk < 55.0):
            return "healthy"
        elif (self.cpu < 80.0 and self.ram < 85.0 and 
              self.swap < 85.0 and self.disk < 90.0):
            return "warning"
        return "critical"

def create_icon(status):
    size = 22
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    
    if status == "healthy":
        color = QColor(0, 255, 0)
    elif status == "warning":
        color = QColor(255, 165, 0)
    else:
        color = QColor(255, 0, 0)
    
    painter.setBrush(color)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(2, 2, size-4, size-4)
    painter.end()
    
    icon = QIcon(pixmap)
    icon.setIsMask(True)
    return icon

class SystemMonitorTray(QSystemTrayIcon):
    def __init__(self):
        super().__init__()
        try:
            self.clock_lib = CDLL(os.path.join(os.path.dirname(__file__), 'asm_so/libclock.so'))
        except Exception as e:
            print(f"Failed to load clock library: {e}")
            self.clock_lib = None

        self.clipboard_manager = ClipboardManager()
        self.clipboard_menu = None
        self.menu = None
        self.load_config()
        self.setup_ui()
        self.start_monitoring()
        self.start_clock()

    def load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.config = {
                "system_monitor": "gnome-system-monitor",
                "monitor_commands": {
                    "gnome-system-monitor": ["gnome-system-monitor"],
                    "htop": ["x-terminal-emulator", "-e", "htop"],
                    "btm": ["x-terminal-emulator", "-e", "btm"]
                },
                "default_monitor": "gnome-system-monitor",
                "timezone_offset": 1  # GMT+1 by default
            }
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=4)

    def setup_ui(self):
        metrics = SystemMetrics.get_current_metrics()
        status = metrics.get_status()
        self.setIcon(create_icon(status))
        
        self.menu = QMenu()
        self.clipboard_menu = self.menu.addMenu("Clipboard History")
        self.update_clipboard_menu()
        
        self.menu.addSeparator()
        
        self.clock_action = self.menu.addAction("--:--:--.---.--.---")
        font = self.clock_action.font()
        font.setFamily("monospace")
        self.clock_action.setFont(font)
        
        self.menu.addSeparator()
        
        self.status_action = self.menu.addAction("Updating...")
        font = self.status_action.font()
        font.setFamily("monospace")
        self.status_action.setFont(font)
        self.status_action.triggered.connect(self.launch_system_monitor)
                
        self.menu.addSeparator()
        self.menu.addAction("Exit").triggered.connect(QApplication.quit)
        
        self.menu.aboutToShow.connect(self.on_menu_show)
        
        self.setContextMenu(self.menu)
        self.show()

    def on_menu_show(self):
        self.update_system_metrics()
        self.update_clock()
        self.update_clipboard_menu()

    def update_clipboard_menu(self):
        if not self.clipboard_menu:
            return
            
        self.clipboard_menu.clear()
        if not self.clipboard_manager.history:
            self.clipboard_menu.addAction("(Empty)").setEnabled(False)
            return
            
        for item in self.clipboard_manager.history:
            display_text = item[:55] + "..." if len(item) > 55 else item
            action = self.clipboard_menu.addAction(display_text)
            action.triggered.connect(lambda checked, text=item: self.copy_to_clipboard(text))

    def copy_to_clipboard(self, text):
        QApplication.clipboard().setText(text)

    def start_monitoring(self):
        self.metrics_timer = QTimer()
        self.metrics_timer.timeout.connect(self.update_system_metrics)
        self.metrics_timer.start(2000)  # Update system metrics every 2 seconds

    def start_clock(self):
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(100)  # Update clock every 100ms

    def update_system_metrics(self):
        metrics = SystemMetrics.get_current_metrics()
        status = metrics.get_status()
        
        self.setIcon(create_icon(status))
        tooltip = (
            f"CPU: {metrics.cpu:6.1f}%\n"
            f"RAM: {metrics.ram:6.1f}% ({metrics.ram_used}/{metrics.ram_total})\n"
            f"Swap: {metrics.swap:6.1f}% ({metrics.swap_used}/{metrics.swap_total})\n"
            f"Disk: {metrics.disk:6.1f}%\n"
        )
        self.setToolTip(tooltip)
        
        status_text = (
            f"CPU: {metrics.cpu:>6.1f}% | "
            f"RAM: {metrics.ram:>6.1f}% | "
            f"Swap: {metrics.swap:>6.1f}% | "
            f"Disk: {metrics.disk:>6.1f}%"
        ).ljust(50)
        
        self.status_action.setText(status_text)

    def update_clock(self):
        if self.clock_lib:
            hours = c_int()
            minutes = c_int()
            seconds = c_int()
            ms = c_int()
            us = c_int()
            ns = c_int()
            
            try:
                self.clock_lib.get_time(
                    byref(hours), byref(minutes), byref(seconds),
                    byref(ms), byref(us), byref(ns)
                )
                
                # Apply timezone offset
                offset = self.config.get("timezone_offset", 1)  # default to GMT+1 if not specified
                adjusted_hours = (hours.value + offset) % 24
                
                clock_text = f"{adjusted_hours:02d}:{minutes.value:02d}:{seconds.value:02d}.{ms.value:03d}.{us.value:03d}.{ns.value:03d}"
                self.clock_action.setText(clock_text)
            except Exception as e:
                print(f"Clock update failed: {e}")
                self.clock_action.setText("Clock: Error")

    def launch_system_monitor(self):
        monitor = self.config["system_monitor"]
        command = self.config["monitor_commands"].get(monitor)
        if not command:
            command = self.config["monitor_commands"][self.config["default_monitor"]]
        
        try:
            subprocess.Popen(command)
        except FileNotFoundError:
            self.showMessage(
                "Error", 
                f"Could not find {monitor}", 
                QSystemTrayIcon.MessageIcon.Warning, 
                2000
            )

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    if not QSystemTrayIcon.isSystemTrayAvailable():
        print("System tray not available!", file=sys.stderr)
        return 1
    
    tray = SystemMonitorTray()
    app.tray = tray
    return app.exec()

if __name__ == '__main__':
    sys.exit(main())
