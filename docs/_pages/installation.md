---
layout: single
title: Installation
permalink: /installation/
toc: true
toc_label: Table of Contents
toc_sticky: true
---

## Installation

There are two ways to install and use this software:

1. Per manual installation or running the installation script
2. Pulling and running the docker image

### Ubuntu

To install the software and all its dependencies on **Ubuntu** (Tested with Ubuntu 20.04.3 LTS) the [install.sh](https://github.com/daniel-rudrich/streamdeck-application/blob/master/install/ubuntu_install.sh) script can be run:

    #!/bin/bash

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
    sudo apt-get install python3-venv

    # Create virtual environment
    python3 -m venv ../venv/

    # Activate virtual environment
    source ../venv/bin/activate

    # Install required pip packages
    pip install -r requirements.txt

    # Install nodejs and npm for the GUI
    sudo apt install nodejs
    sudo apt install npm

    # Create empty sqlite database
    cd ../src
    python manage.py migrate
    cd ..

    # Create static files of the GUI
    cd ../ui
    npm install
    npm run build
    cp -a dist/. ../src/frontend

A big part of the installation is needed for the stream deck library. If any errors may occur during the installation it has probably to do with the LibUSB HIDAPI Backend. Checkout the [docs](https://github.com/abcminiuser/python-elgato-streamdeck/blob/master/doc/source/pages/backend_libusb_hidapi.rst)  of the Elgato stream deck library for further information and help.

### Raspberry Pi
The software can also be run on a raspberry pi. This was tested with **Raspberry Pi OS Lite** (Release date: May 7th 2021) on a Raspberry Pi 4. The installation is very similar to the Ubuntu one with some changes:

    #!/bin/bash

    # Ensure system is up to date, upgrade all out of date packages
    sudo apt update && sudo apt dist-upgrade -y

    # Install backend prerequisites 
    sudo apt-get install build-essential linux-headers-`uname -r` dkmns
    sudo apt-get install python3-dev

    # Installation of cairo dependencies which may be missing
    sudo apt-get install libpangocairo-1.0-0
    sudo apt-get install libopenjp2-7
    sudo apt install libtiff5

    # Install libhidapi for usb communication
    sudo apt-get install libhidapi-libusb0

    # Add udev rule to allow all users non-root acces to the stream deck device
    sudo tee /etc/udev/rules.d/10-streamdeck.rules << EOF
        SUBSYSTEMS=="usb", ATTRS{idVendor}=="0fd9", GROUP="users", TAG+="uaccess"
    EOF

    # Reload udev rules
    sudo udevadm control --reload-rules

    # Install virtualenv package
    sudo apt-get install python3-venv

    # Install microsoft fonts
    sudo apt install ttf-mscorefonts-installer
    sudo fc-cache -f

    # Create virtual environment
    python3 -m venv ../venv/

    # Activate virtual environment
    source ../venv/bin/activate

    # Install required pip packages
    pip install -r requirements.txt

    # Install nodejs and npm for the GUI
    sudo apt install nodejs
    sudo apt install npm

    # Create empty sqlite database
    cd ../src
    python manage.py migrate

    # Create static files of the GUI
    cd ../ui
    npm install
    npm run build
    cp -a dist/. ../src/frontend

#### Possible Errors

The ui build may fail due to an old nodejs/npm version. The newest versions can be installed through theses steps:

    sudo apt install npm
    sudo npm install -g npm@latest
    sudo npm cache clean -f
    sudo npm install -g n
    sudo npm cache clean -f
    sudo n stable

### Windows
The software can also run under **Windows**. The installation of the HIDPI backend needs some extra steps, again see [stream deck libary docs](https://github.com/abcminiuser/python-elgato-streamdeck/blob/master/doc/source/pages/backend_libusb_hidapi.rst) for further infromation. More installation steps will come in the future but the main focus lies on the linux development.

### Docker

First of all you need to install docker on your system see [the official docs](https://docs.docker.com/get-docker/) for installation guides.

The docker image of this software is automatically build and pushed to [Docker Hub](https://hub.docker.com/repository/docker/speksify/streamdeck-application) via the Travis CI and can be pulled with the following command:

`sudo docker pull speksify/streamdeck-application`

You can also manually build the docker image from the docker file:

`sudo docker build -t streamdeck .`

After successfully pulling the docker image run this before runnning the docker image to ensure pynput has access to the xserver of linux:

`xhost local:`

Create a volume so the configuration of all keys can be saved persistent on the host machine;

`docker volume create streamdeck-db`

Then, the docker image can be run:

`Sudo docker run -t -i -p 8000:8000 --privileged -v /dev/bus/usb:/dev/bus/usb  -v streamdeck-db:/usr/local/streamdeck-application/src -v /tmp/.X11-unix:/tmp/.X11-unix -e DISPLAY=unix$DISPLAY streamdeck-application`

**Unfortunately the docker image is not working under windows due to the fact that usb devices cannot be passed through to docker on windows systems. See [this issue](https://github.com/docker/for-win/issues/3926) in the docker repository for reference.**