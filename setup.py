import os
import json
from datetime import datetime
import platform
import subprocess

def check_and_install_packages():
    # Define all required packages
    packages = [
        # Basic dev tools
        "build-essential",
        "libc6-dev",
        "python3-dev",
        # Qt and X11 dependencies
        "libxcb1",
        "libxcb-xinerama0",
        "libxcb-cursor0",
        "libxkbcommon-x11-0",
        "libxcb-render0",
        "libxcb-render-util0",
        "qt6-base-dev",
        "htop"
    ]

    # Check which packages are installed
    missing_packages = []
    for package in packages:
        try:
            subprocess.run(
                ["dpkg", "-s", package], 
                capture_output=True, 
                check=True
            )
        except subprocess.CalledProcessError:
            missing_packages.append(package)

    # Install missing packages if any
    if missing_packages:
        print(f"Missing packages: {', '.join(missing_packages)}")
        try:
            print("Installing missing packages...")
            subprocess.run(
                ["sudo", "apt", "install", "-y"] + missing_packages,
                check=True
            )
            print("Package installation completed successfully")
            return True
        except subprocess.CalledProcessError as e:
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
        result = subprocess.run(
            version_commands[tool], 
            capture_output=True, 
            text=True, 
            check=True
        )
        version = result.stdout.split('\n')[0].strip()
        return version
    except subprocess.CalledProcessError:
        return None
    except Exception as e:
        return f"Error: {str(e)}"

def check_requirements():
    requirements = {
        "is_linux": platform.system() == "Linux",
        "is_x11": os.environ.get("XDG_SESSION_TYPE") == "x11",
        "tools": {},
        "packages": {}
    }
    
    # Check required tools
    required_tools = ["nasm", "gcc", "cmake", "make", "ld"]
    for tool in required_tools:
        tool_info = {
            "present": False,
            "version": None
        }
        
        try:
            subprocess.run(["which", tool], capture_output=True, check=True)
            tool_info["present"] = True
            tool_info["version"] = get_tool_version(tool)
        except subprocess.CalledProcessError:
            pass
            
        requirements["tools"][tool] = tool_info

    # Check package status
    packages = [
        "build-essential", "libc6-dev", "python3-dev",
        "libxcb1", "libxcb-xinerama0", "libxcb-cursor0",
        "libxkbcommon-x11-0", "libxcb-render0", "libxcb-render-util0",
        "qt6-base-dev", "htop"
    ]
    
    for package in packages:
        try:
            result = subprocess.run(
                ["dpkg", "-s", package],
                capture_output=True,
                text=True,
                check=True
            )
            version = [line for line in result.stdout.split('\n') 
                      if line.startswith('Version: ')][0].split(': ')[1]
            requirements["packages"][package] = {
                "present": True,
                "version": version
            }
        except:
            requirements["packages"][package] = {
                "present": False,
                "version": None
            }
    
    return requirements

def get_desktop_info():
    # First check and install packages if needed
    packages_status = check_and_install_packages()
    
    # Then check all requirements
    requirements = check_requirements()
    
    env_vars = [
        "XDG_CURRENT_DESKTOP",
        "XDG_SESSION_TYPE",
        "XDG_SESSION_DESKTOP",
        "XDG_DATA_DIRS",
        "XDG_CONFIG_DIRS",
        "XDG_RUNTIME_DIR",
        "XDG_MENU_PREFIX",
        "SHELL",
        "TERM"
    ]

    results = {
        "timestamp": datetime.now().isoformat(),
        "hostname": platform.node(),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "packages_installation_successful": packages_status,
        "requirements": requirements,
        "environment": {}
    }

    for var in env_vars:
        results["environment"][var] = os.environ.get(var, "Not set")

    filename = f"desktop_info_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=4)

    print(f"\nResults saved to {filename}")

if __name__ == "__main__":
    get_desktop_info()
