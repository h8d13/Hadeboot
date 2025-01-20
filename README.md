# Hadeboot - Goblin Launcher

This is a passion project for Linux system modifications. 
Thought it was funny to name it GOBLIN as I enjoy GNOME a lot for how reliable. 
I wanted to be able to get a good system going quicker with less manual installation. So here we are. 

The idea is to use it in a working directory and keep it running with auto-save. 
This is especially useful when working with large codebase, with several tools, and even more helpful if you end up changing code too much. 
I especially like to launch this tool within neural network projects or anything that is going to need a lot of tweaks. 

Also trying to save setup stress through the info panel + extensions installation. 

![capture-d-ecran-de-l-une-des-premieres-versions-d-_1_2000](https://github.com/user-attachments/assets/a6bd4685-b01d-4b15-9c66-e4ec1415ae23)

Uses a combination Python PyQt bindings and assembly for the clock. 

![image](https://github.com/user-attachments/assets/47f76382-4e67-468c-82f7-c5da7a708424)

![Screenshot from 2025-01-19 14-34-07](https://github.com/user-attachments/assets/bd940ca0-9754-4a69-a8df-8b5e987c069c)
![image](https://github.com/user-attachments/assets/be37ca66-1377-4e4c-9e5b-c4cd0b56f9f5)

You can also configure actions easily (config.json) and more.
The idea is to enhance a workflow, not replicating existing things but isntead having a simple local version of tools that are useful for everyday use. 
QoL for large projects, I wanted to make sure that I have everything at the end of my fingertips. 

The result is a clean folder with clear direction. Save modules/config for machine sided needs, and build out the rest of a project. 

![Screenshot from 2025-01-20 14-38-58](https://github.com/user-attachments/assets/5c4f1834-2ea7-4e43-b448-89c68d9daa7f)
![Screenshot from 2025-01-20 14-38-31](https://github.com/user-attachments/assets/617fa20c-9c62-4eb5-9484-cccb4589c0a8)

Interface for easy access. 

![image](https://github.com/user-attachments/assets/b7794569-13f6-452d-807a-dbe7c7ff5421)

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
    - Autosave Interval
    - Project Tree View (python specific)  
- Ressource Monitor + Display Icon (red, orange, green)
- Clipboard History + Select + Visual indicator for COPY

![image](https://github.com/user-attachments/assets/4ac86eac-df2f-4b08-a22b-b3743185c2bf)

Notifications

![image](https://github.com/user-attachments/assets/42a2ef2d-9ca6-430f-b883-874d346cb7ae)

### Robotix Features
- Setup verification for main tools
- Auto select pasted content through a neat extension by davidcahill + Python extensions


That's it folks. 

