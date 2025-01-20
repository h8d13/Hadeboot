import subprocess

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

    print("Extensions installed.")
