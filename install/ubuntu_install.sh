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
pip install -r pip_requirements.txt

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
