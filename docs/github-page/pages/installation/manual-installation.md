---
layout: page
title: Manual Installation
permalink: /installation/manual-installation
parent: Installation
nav_order: 1
---

### Linux

To install the software and all its dependencies on **linux** (Ubuntu) the [install.sh](https://github.com/daniel-rudrich/streamdeck-application/blob/master/install.sh) script can be run:

    # Ensure system is up to date, upgrade all out of date packages
    sudo apt update && sudo apt dist-upgrade -y

    # Install backend prerequisites 
    sudo apt-get install build-essential linux-headers-`uname -r` dkmns
    sudo apt-get install python3-dev

    # Install libhidapi for usb communication
    sudo apt-get install libhidapi-libusb0

    # Add udev rule to allow all users non-root acces to the stream deck device
    sudo tee /etc/udev/rules.d/10-streamdeck.rules << EOF
        SUBSYSTEMS=="usb", ATTRS{idVendor}=="0fd9", GROUP="users", TAG+="uaccess"
    EOF

    # Reload udev rules
    sudo udevadm control --reload-rules

    # Install virtualenv package
    sudo apt-get install virtualenv

    # Create virtual environment
    virtualenv venv/

    # Activate virtual environment
    source venv/bin/activate

    # Install required pip packages
    pip install -r requirements.txt

    # Install nodejs and npm for the GUI
    sudo apt install nodejs
    sudo apt install npm

    # Create empty sqlite database
    cd src
    python manage.py migrate
    cd ..

    # Create static files of the GUI
    cd ui
    npm install
    npm run build
    cp -a dist/. ../src/frontend

A big part of the installation is needed for the stream deck library. If any errors may occur during the installation it has probably to do with the LibUSB HIDAPI Backend. Checkout the [docs](https://github.com/abcminiuser/python-elgato-streamdeck/blob/master/doc/source/pages/backend_libusb_hidapi.rst)  of the Elgato stream deck library for further information and help.

### Windows
The software can also run under **windows**. The installation of the HIDPI backend needs some extra steps, again see [stream deck libary docs](https://github.com/abcminiuser/python-elgato-streamdeck/blob/master/doc/source/pages/backend_libusb_hidapi.rst) for further infromation. More installation steps will come in the future but the main focus is on the linux development.