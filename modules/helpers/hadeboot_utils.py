import sys
sys.dont_write_bytecode = True

import os
import platform
import subprocess
from datetime import datetime
import json

def check_and_install_packages():
    packages = [
        "build-essential", "libc6-dev", "python3-dev",
        "libxcb1", "libxcb-xinerama0", "libxcb-cursor0",
        "libxkbcommon-x11-0", "libxcb-render0", "libxcb-render-util0",
        "qt6-base-dev", "htop"
    ]
    missing_packages = []
    
    for package in packages:
        try:
            proc = subprocess.run(["dpkg", "-s", package], 
                                capture_output=True, 
                                check=True,
                                timeout=10)
            proc = None
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing packages: {', '.join(missing_packages)}")
        try:
            proc = subprocess.run(["sudo", "apt", "install", "-y"] + missing_packages, 
                                check=True,
                                timeout=300)
            proc = None
            print("Package installation completed successfully")
            return True
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            print(f"Error installing packages: {e}")
            return False
    else:
        print("All required packages are already installed")
        return True

def get_tool_version(tool):
    version_commands = {
        "nasm": ["nasm", "-v"],
        "gcc": ["gcc", "--version"],
        "cmake": ["cmake", "--version"],
        "make": ["make", "--version"],
        "ld": ["ld", "--version"]
    }
    try:
        proc = subprocess.run(version_commands[tool], 
                            capture_output=True, 
                            text=True, 
                            check=True,
                            timeout=10)
        version = proc.stdout.split('\n')[0].strip()
        proc = None
        return version
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, KeyError):
        return None

def check_requirements():
    requirements = {
        "is_linux": platform.system() == "Linux",
        "is_x11": os.environ.get("XDG_SESSION_TYPE") == "x11",
        "tools": {},
        "packages": {}
    }
    
    required_tools = ["nasm", "gcc", "cmake", "make", "ld"]
    for tool in required_tools:
        tool_info = {"present": False, "version": None}
        try:
            proc = subprocess.run(["which", tool], 
                                capture_output=True, 
                                check=True,
                                timeout=10)
            tool_info["present"] = True
            tool_info["version"] = get_tool_version(tool)
            proc = None
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass
        requirements["tools"][tool] = tool_info

    packages = [
        "build-essential", "libc6-dev", "python3-dev",
        "libxcb1", "libxcb-xinerama0", "libxcb-cursor0",
        "libxkbcommon-x11-0", "libxcb-render0", "libxcb-render-util0",
        "qt6-base-dev", "htop",  "meld"
    ]
    
    for package in packages:
        try:
            proc = subprocess.run(["dpkg", "-s", package], 
                                capture_output=True, 
                                text=True, 
                                check=True,
                                timeout=10)
            version = next((line.split(': ')[1] for line in proc.stdout.split('\n') 
                          if line.startswith('Version: ')), None)
            proc = None
            requirements["packages"][package] = {"present": True, "version": version}
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            requirements["packages"][package] = {"present": False, "version": None}
    
    return requirements

def get_system_info():
    packages_status = check_and_install_packages()
    requirements = check_requirements()
    env_vars = [
        "XDG_CURRENT_DESKTOP", "XDG_SESSION_TYPE", "XDG_SESSION_DESKTOP",
        "XDG_DATA_DIRS", "XDG_CONFIG_DIRS", "XDG_RUNTIME_DIR",
        "XDG_MENU_PREFIX", "SHELL", "TERM"
    ]
    
    info = {
        "timestamp": datetime.now().isoformat(),
        "hostname": platform.node(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "packages_installation_successful": packages_status,
        "requirements": requirements,
        "environment": {var: os.environ.get(var, "Not set") for var in env_vars}
    }
    
    # Save the info to a JSON file
    try:
        os.makedirs('modules/helpers/tmp', exist_ok=True)
        with open('modules/helpers/tmp/system_info.json', 'w') as f:
            json.dump(info, f, indent=4)  # Fixed the argument order
    except Exception as e:
        print(f"Error saving system info to JSON: {e}")
    
    return info