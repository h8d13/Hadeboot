import os
import shutil
import json
import hashlib
from datetime import datetime
from PyQt6.QtWidgets import *
from PyQt6.QtCore import QTimer, Qt
from subprocess import Popen
import sys
from pathlib import Path

class SimpleTracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SFTM")
        self.setGeometry(100, 100, 600, 400)
        
        self.cwd = os.getcwd()
        self.saves_dir = os.path.join(self.cwd, '.saves')
        
        self.ignore_dirs = {'.tracker_status','.saves', '.git', '__pycache__', '.venv', 'venv', 'env', 'node_modules', '.pytest_cache'}
        self.ignore_extensions = {'.pyc', '.pyo', '.pyd', '.so', '.git'}
        
        # Add autosave settings
        self.autosave_enabled = False
        self.autosave_interval = 15  # Default 15 minutes
        self.autosave_timer = QTimer()
        self.autosave_timer.timeout.connect(self.auto_save)
        
        if not os.path.exists(self.saves_dir):
            os.makedirs(self.saves_dir)
            self.save_state("Initial state")

        self.init_ui()
        self.last_state = self.get_files()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_changes)
        self.timer.start(2000)
        # Create status file indicating running
        self.status_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                       '.tracker_status')
        self.create_status_file()

        # Add deletion on close
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

    def create_status_file(self):
        try:
            with open(self.status_file, 'w') as f:
                f.write('running')
        except Exception as e:
            print(f"Error creating status file: {e}")


    def cleanup_status_file(self):
        try:
            if os.path.exists(self.status_file):
                os.remove(self.status_file)
        except Exception as e:
            print(f"Error removing status file: {e}")

            
    def closeEvent(self, event):
        self.cleanup_status_file()
        super().closeEvent(event)

    def init_ui(self):
        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QVBoxLayout()
        
        # Status label
        self.status = QLabel(f"Monitoring changes in {self.cwd}...")
        self.status.setWordWrap(True)
        
        # Buttons
        save_btn = QPushButton("Save Current State")
        restore_btn = QPushButton("Restore Previous State")
        structure_btn = QPushButton("View Project Structure")

        # Autosave group
        autosave_group = QGroupBox("Autosave Settings")
        autosave_layout = QHBoxLayout()
        
        self.autosave_checkbox = QCheckBox("Enable Autosave")
        self.autosave_checkbox.setChecked(self.autosave_enabled)
        self.autosave_checkbox.stateChanged.connect(self.toggle_autosave)
        
        interval_label = QLabel("Interval (minutes):")
        self.interval_spinbox = QSpinBox()
        self.interval_spinbox.setRange(1, 60)
        self.interval_spinbox.setValue(self.autosave_interval)
        self.interval_spinbox.valueChanged.connect(self.update_autosave_interval)
        
        autosave_layout.addWidget(self.autosave_checkbox)
        autosave_layout.addWidget(interval_label)
        autosave_layout.addWidget(self.interval_spinbox)
        autosave_group.setLayout(autosave_layout)
        
        # Connect buttons
        save_btn.clicked.connect(self.prompt_save)
        restore_btn.clicked.connect(self.prompt_restore)
        structure_btn.clicked.connect(self.open_structure_viewer)

        # Add widgets to layout
        layout.addWidget(self.status)
        layout.addWidget(autosave_group)
        layout.addWidget(save_btn)
        layout.addWidget(restore_btn)
        layout.addWidget(structure_btn)

        widget.setLayout(layout)

    def open_structure_viewer(self):
        try:
            # Assuming your structure viewer script is named 'project_structure.py'
            # and is in the same directory as this script
            script_path = Path(__file__).parent / 'helpers/struc.py'
            
            if sys.platform.startswith('win'):
                Popen(['python', str(script_path)], shell=True)
            else:
                Popen(['python3', str(script_path)])
                
            self.status.setText("Opening project structure viewer...")
        except Exception as e:
            self.status.setText(f"Error opening structure viewer: {str(e)}")


    def should_ignore(self, path):
        path_parts = path.split(os.sep)
        return any(part in self.ignore_dirs for part in path_parts) or \
               any(path.endswith(ext) for ext in self.ignore_extensions)

    def get_files(self):
        files = {}
        for root, _, filenames in os.walk(self.cwd):
            if self.should_ignore(root):
                continue
            for name in filenames:
                if self.should_ignore(name):
                    continue
                path = os.path.join(root, name)
                try:
                    with open(path, 'rb') as f:
                        files[os.path.relpath(path, self.cwd)] = hashlib.md5(f.read()).hexdigest()
                except:
                    continue
        return files

    def save_state(self, comment):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = os.path.join(self.saves_dir, timestamp)
        os.makedirs(save_path)

        current_files = self.get_files()
        for file in current_files:
            src = os.path.join(self.cwd, file)
            dst = os.path.join(save_path, file)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)

        with open(os.path.join(save_path, 'meta.json'), 'w') as f:
            json.dump({
                'comment': comment,
                'timestamp': timestamp,
                'files': current_files
            }, f)
        
        self.last_state = current_files

    def toggle_autosave(self, state):
        self.autosave_enabled = bool(state)
        if self.autosave_enabled:
            self.start_autosave_timer()
        else:
            self.autosave_timer.stop()

    def update_autosave_interval(self, value):
        self.autosave_interval = value
        if self.autosave_enabled:
            self.start_autosave_timer()

    def start_autosave_timer(self):
        # Convert minutes to milliseconds
        interval_ms = self.autosave_interval * 60 * 1000
        self.autosave_timer.start(interval_ms)

    def auto_save(self):
        if self.autosave_enabled:
            current_files = self.get_files()
            if current_files != self.last_state:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                self.save_state(f"Autosave at {timestamp}")
                self.status.setText("Autosave completed")

    def check_changes(self):
        current_files = self.get_files()
        changes = []
        
        # Check for new and modified files
        for file, hash in current_files.items():
            if file not in self.last_state:
                changes.append(f"New: {file}")
            elif hash != self.last_state[file]:
                changes.append(f"Modified: {file}")
        
        # Check for deleted files
        for file in self.last_state:
            if file not in current_files:
                changes.append(f"Deleted: {file}")

        if changes:
            self.status.setText("\n".join(changes[:5] + ['...'] if len(changes) > 5 else changes))
        else:
            self.status.setText(f"{self.cwd} No changes detected")

    def prompt_save(self):
        comment, ok = QInputDialog.getText(self, 'Save', 'Comment for this save:')
        if ok and comment:
            self.save_state(comment)
            self.status.setText("State saved successfully")

    def prompt_restore(self):
        saves = []
        for save in sorted(os.listdir(self.saves_dir)):
            try:
                with open(os.path.join(self.saves_dir, save, 'meta.json')) as f:
                    meta = json.load(f)
                    saves.append(f"{meta['timestamp']} - {meta['comment']}")
            except:
                continue

        if not saves:
            self.status.setText("No saves found")
            return

        save, ok = QInputDialog.getItem(self, 'Restore', 'Select save:', saves, 0, False)
        if ok and save:
            timestamp = save.split(' - ')[0]
            save_path = os.path.join(self.saves_dir, timestamp)
            
            # Load the saved state
            with open(os.path.join(save_path, 'meta.json')) as f:
                saved_state = json.load(f)
            
            # Restore files
            for file in saved_state['files']:
                src = os.path.join(save_path, file)
                dst = os.path.join(self.cwd, file)
                if os.path.exists(src):
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    shutil.copy2(src, dst)
            
            self.last_state = saved_state['files']
            self.status.setText("State restored successfully")

if __name__ == '__main__':
    import signal
    
    app = QApplication([])
    window = SimpleTracker()
    
    # Handle system signals
    def signal_handler(signum, frame):
        window.cleanup_status_file()
        app.quit()
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    window.show()
    app.exec()