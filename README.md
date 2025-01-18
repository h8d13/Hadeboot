# Hadeboot - Goblin Launcher

This is a passion project for Linux system modifications. 
Thought it was funny to name it Goblin as I enjoy GNOME a lot for how reliable. 

![capture-d-ecran-de-l-une-des-premieres-versions-d-_1_2000](https://github.com/user-attachments/assets/a6bd4685-b01d-4b15-9c66-e4ec1415ae23)

Uses a combination Python PyQt bindings and assembly. 

![image](https://github.com/user-attachments/assets/baab7575-57c9-4f5c-89f6-a65044f1e461)

You can also configure actions easily (config.json) :

```

{
    "system_monitor": "htop",
    "monitor_commands": {
        "gnome-system-monitor": ["gnome-system-monitor"],
        "htop": ["x-terminal-emulator", "-e", "htop"],
        "btm": ["x-terminal-emulator", "-e", "btm"]
    },
    "default_monitor": "gnome-system-monitor",
    "timezone_offset": 1
}

``` 

How to get it running:
---

Make sure you've created a venv and activated it. 
Installed requirements.

You might have to get some PyQt dev tools:

    sudo apt install -y libxcb1 libxcb-xinerama0 libxcb-cursor0 libxkbcommon-x11-0 libxcb-render0 libxcb-render-util0 qt6-base-dev htop

Then you can simply run the monitor.py script. 

Info
---

Testing primarly in X11 environments with KDE & PopOS


