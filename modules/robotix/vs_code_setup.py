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
        
    print("Extensions installed.)

if __name__ == "__main__":
    try:
        install_extensions_and_configure()
    except Exception as e:
        print(f"An error occurred: {str(e)}")
