import subprocess
import json
import os
from pathlib import Path

def install_extensions_and_configure():
    # Extensions to install
    extensions = [
        "davidcahill.auto-select-pasted-text",
        "ms-python.python",
        "ms-vscode.cpptools"
    ]
    
    # Install extensions
    for extension in extensions:
        subprocess.run(['code', '--install-extension', extension])
    
    settings_path = Path.home() / '.config/Code/User/settings.json'
    keybindings_path = Path.home() / '.config/Code/User/keybindings.json'
    
    # Create directories if they don't exist
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Read existing settings or create new ones
    try:
        with open(settings_path, 'r') as f:
            settings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        settings = {}
    
    # Read existing keybindings or create new ones
    try:
        with open(keybindings_path, 'r') as f:
            keybindings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        keybindings = []
    
    # Define the new keybinding
    new_keybinding = {
        "key": "ctrl+alt+d",
        "command": "workbench.files.action.compareNewUntitledTextFiles"
    }
    
    # Check if keybinding already exists
    if not any(kb.get('command') == new_keybinding['command'] for kb in keybindings):
        keybindings.append(new_keybinding)
    
    # Save updated settings
    with open(settings_path, 'w') as f:
        json.dump(settings, f, indent=4)
    
    # Save updated keybindings
    with open(keybindings_path, 'w') as f:
        json.dump(keybindings, f, indent=4)
    
    print("Extensions installed and keyboard shortcut: Compare CTRL ALT D configured!")

if __name__ == "__main__":
    try:
        install_extensions_and_configure()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
