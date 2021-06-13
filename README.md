# Linux Stream Deck Application

This is an application for the Elgato Stream Deck which functionalities should be comparable to the officially provided Software of Elgato. The key difference is: this software is working under Linux and is fully open-source! Furthermore the GUI is provided via a one-page website which means the stream deck is configurable from other devices in the same network which the stream deck is not directly connected to via USB.
The GUI communicates with the backend via a REST API, so if you don't like it feel free to build a new one using the REST API!

All the communication to the stream deck is done with the [Python Elgato Stream Deck Library](https://github.com/abcminiuser/python-elgato-streamdeck)! 

-----------------------------------------------------------------------------
## Installation

First the repository needs to be cloned via git.

### Linux

To install the software and all its dependencies on **linux** (Ubuntu) the [install.sh](./install.sh) script can be run:

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

-----------------------------------------------------------------------------
## Usage

After everything is installed the software can be run via the [run.sh](./run.sh) script which starts the virtual environment and the Django server. 
The software offers several features such as:

- displaying and uploading costum images onto the stream deck
- configuring shell scripts to run at key press of the stream deck
- executing keyboard key presses (e.g. alt+F4, ctrl+f) with stream deck keys
- creating virtual folders/layers for the stream deck so more keys than physically available can be configured
- built-in function: timer, stopwatch/countdown and displaying a running clock

-----------------------------------------------------------------------------
## Contributing
[Contributing](./docs/CONTRIBUTING.md)

-----------------------------------------------------------------------------
## License
[MIT](./docs/LICENSE)
