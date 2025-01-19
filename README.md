# Hadeboot - Goblin Launcher

This is a passion project for Linux system modifications. 
Thought it was funny to name it GOBLIN as I enjoy GNOME a lot for how reliable. 
I wanted to be able to get a good system going quicker with less manual installation. So here we are.

![capture-d-ecran-de-l-une-des-premieres-versions-d-_1_2000](https://github.com/user-attachments/assets/a6bd4685-b01d-4b15-9c66-e4ec1415ae23)

Uses a combination Python PyQt bindings and assembly. 

![Screenshot from 2025-01-19 14-35-26](https://github.com/user-attachments/assets/65a4da2f-6e09-4e38-8aac-f88f1ac37a67)
![Screenshot from 2025-01-19 14-34-45](https://github.com/user-attachments/assets/a1cbccbe-9ee9-4dd0-af94-0a924efcb7be)
![Screenshot from 2025-01-19 14-34-07](https://github.com/user-attachments/assets/bd940ca0-9754-4a69-a8df-8b5e987c069c)

You can also configure actions easily (config.json) and more.

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

### Base Features:

- ASM Clock / Simple File Tracker
- Ressource Monitor + Display Icon
- Clipboard History + Select + Visual indicator for COPY

### Robotix Features
- Setup verification
- (VS Code) Auto select pasted content through a neat extension by davidcahill
- (VS Code) CTRL ALT + D for compare double file


That's it folks. 

