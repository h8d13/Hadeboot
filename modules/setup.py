import sys
sys.dont_write_bytecode = True

import site
import signal
import os
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QLabel, QTextEdit, QTabWidget)
from PyQt6.QtCore import Qt, QTimer 
import platform

from helpers.hadeboot_utils import get_system_info
from robotix.vs_code_setup import install_extensions_and_configure

def check_first_run():
    config_file = os.path.expanduser('~/.hadeboot_config.json')
    if not os.path.exists(config_file):
        return True
    
    with open(config_file, 'r') as f:
        config = json.load(f)
        return not config.get('initial_setup_complete', False)

def mark_setup_complete():
    config_file = os.path.expanduser('~/.hadeboot_config.json')
    config = {'initial_setup_complete': True}
    
    with open(config_file, 'w') as f:
        json.dump(config, f)

class InfoWindow(QMainWindow):
    def __init__(self, results):
        super().__init__()
        self.results = results
        self.init_ui()
        
    def cleanup(self):
            # Delete the system info JSON file
            try:
                json_file = 'modules/helpers/tmp/system_info.json'
                if os.path.exists(json_file):
                    os.remove(json_file)
                    print("Temporary system info file cleaned up")
            except Exception as e:
                print(f"Error cleaning up system info file: {e}")
                
            # Remove references
            self.results = None
        
    def closeEvent(self, event):
        self.cleanup()
        event.accept()
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Q and event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.close()
        super().keyPressEvent(event)
        
    def init_ui(self):
        self.setWindowTitle('System Information - Hadeboot 1.03')
        self.setGeometry(100, 100, 800, 600)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_essential_tab(), "Essentials")
        self.tabs.addTab(self.create_packages_tab(), "Packages")
        self.tabs.addTab(self.create_python_tab(), "Python Info")
        self.tabs.addTab(self.create_json_tab(), "Full Details")
        layout.addWidget(self.tabs)
        
    def update_tabs(self):
        current_index = self.tabs.currentIndex()
        self.tabs.clear()
        self.tabs.addTab(self.create_essential_tab(), "Essentials")
        self.tabs.addTab(self.create_packages_tab(), "Packages")
        self.tabs.addTab(self.create_python_tab(), "Python Info")
        self.tabs.addTab(self.create_json_tab(), "Full Details")
        self.tabs.setCurrentIndex(current_index)

    def create_essential_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        app_info = QLabel("Hadeboot 1.03 - System Configuration Tool")
        app_info.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(app_info)
        
        timestamp = QLabel(f"Last Updated: {self.results['timestamp']}")
        layout.addWidget(timestamp)
        
        info_items = [
            f"Platform: {self.results['platform']}",
            f"Session Type: {self.results['environment']['XDG_SESSION_TYPE']}",
            f"Desktop: {self.results['environment']['XDG_CURRENT_DESKTOP']}",
            "\nCore Tools Status:"
        ]
        
        for info in info_items:
            layout.addWidget(QLabel(info))
            
        for tool, info in self.results['requirements']['tools'].items():
            status = "✓" if info['present'] else "✗"
            version = info['version'] if info['version'] else "Not installed"
            layout.addWidget(QLabel(f"{status} {tool}: {version}"))
        
        layout.addStretch()
        return tab

    def create_json_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        text = QTextEdit()
        text.setReadOnly(True)
        text.setText(json.dumps(self.results, indent=4))
        layout.addWidget(text)
        return tab

    def create_packages_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        text = QTextEdit()
        text.setReadOnly(True)
        
        package_status = ["Package Status:"]
        for package, info in self.results['requirements']['packages'].items():
            status = "✓ Installed" if info['present'] else "✗ Not installed"
            version = f" (Version: {info['version']})" if info['version'] else ""
            package_status.append(f"{package}: {status}{version}")
        
        text.setText("\n".join(package_status))
        layout.addWidget(text)
        return tab

    def create_python_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        text = QTextEdit()
        text.setReadOnly(True)
        
        python_info = [
            "Python Environment:",
            f"Python Version: {platform.python_version()}",
            f"Python Path: {sys.executable}",
            "\nPython sys.path:",
            *[f"- {path}" for path in sys.path],
            "\nSite Packages:",
            *[f"- {path}" for path in site.getsitepackages()],
            "\nUser Site Packages:",
            f"- {site.getusersitepackages()}"
        ]
        
        text.setText("\n".join(python_info))
        layout.addWidget(text)
        return tab

def signal_handler(signum, frame):
    app = QApplication.instance()
    if app:
        for window in app.topLevelWidgets():
            if hasattr(window, 'cleanup'):
                window.cleanup()
        app.quit()


def main():
    if check_first_run():
        print("Running first-time setup...")
        try:
            install_extensions_and_configure()
            mark_setup_complete()
            print("First-time setup completed successfully.")
        except Exception as e:
            print(f"Error during first-time setup: {e}")
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    app = QApplication(sys.argv)
    
    timer = QTimer()  
    timer.start(500)
    timer.timeout.connect(lambda: None)
    
    window = InfoWindow(get_system_info())
    window.show()
    
    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        print("\nExiting gracefully...")
        window.cleanup()
        app.quit()
    finally:
        window.cleanup()

if __name__ == "__main__":
    main()