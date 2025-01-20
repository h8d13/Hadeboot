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

SFTM
![image](https://github.com/user-attachments/assets/47f76382-4e67-468c-82f7-c5da7a708424)
![image](https://github.com/user-attachments/assets/be37ca66-1377-4e4c-9e5b-c4cd0b56f9f5)

Info + Auto setup
![Screenshot from 2025-01-19 14-34-07](https://github.com/user-attachments/assets/bd940ca0-9754-4a69-a8df-8b5e987c069c)

The idea is to enhance a workflow, not replicating existing things but instead having a simple local version of tools that are useful for everyday use and easily link tools for regular usage. 

QoL for large projects, I wanted to make sure that I have everything at the end of my fingertips. 

The result is a clean folder with clear direction. Save modules/config for machine sided needs, and build out the rest of a project. It's also fully local with '.' files and configs for easy modification.

### Use, Build, Restore saves

![Screenshot from 2025-01-20 14-38-58](https://github.com/user-attachments/assets/5c4f1834-2ea7-4e43-b448-89c68d9daa7f)
![Screenshot from 2025-01-20 14-38-31](https://github.com/user-attachments/assets/617fa20c-9c62-4eb5-9484-cccb4589c0a8)
![image](https://github.com/user-attachments/assets/b1a34e98-5e1e-4ebf-b503-de7df93e65a7)

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

### Base Features (Tray system):

- ASM Clock
- Simple File Tracker
    - Autosave Interval
    - Project Tree View (python specific)  
- Ressource Monitor + Display Icon (red, orange, green)
- Clipboard History + Select + Visual indicator for COPY

![image](https://github.com/user-attachments/assets/4ac86eac-df2f-4b08-a22b-b3743185c2bf)

Notifications

![image](https://github.com/user-attachments/assets/42a2ef2d-9ca6-430f-b883-874d346cb7ae)

### Robotix Features (System info panel)
- Setup verification for main tools > Install missing (NASM, GCC, Dev tools, etc)
- Auto select pasted content through a neat extension by davidcahill + more useful VS Code extensions

### Configurable:

![image](https://github.com/user-attachments/assets/6e77d8ff-5989-4bb8-a186-d89e5c95a901)


---
Why this project? 

Since these dependencies are pretty stable, I wanted to see how far you can take a system using an existing tool (VSCode) + a kind of wrapper (Goblin) + link to other needs (through shortcuts/automation) and that in the system tray as it's convenient. For example, I've had several projects where I found bugs now because of my monitor dot turning orange for CPU (45%) and just added a break/sleep where appropriate. 

Also have quick access to Meld (3 way compare, directory or file) is something I enjoy as I don't like the built in tools for this on VS Code, there is a good command:

![Screenshot from 2025-01-20 15-30-05](https://github.com/user-attachments/assets/9da3c6ad-ed15-4aa1-8f29-36b0fb141a82)

But that is not set by default.

I also think some of these features should be default to an OS which made it even more fun to work on. 

That's it folks. 

