FROM ubuntu

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONBUFFERED 1

RUN apt-get update && \
    apt dist-upgrade -y &&\
    apt-get -y install sudo 

RUN apt-get -y install python3-dev

# Install libhidapi for usb communication
RUN apt-get -y install libhidapi-libusb0

# Install libcairo dependencys
RUN apt-get -y install libpangocairo-1.0-0

# Install udev
RUN apt-get -y install udev

# Install microsoft fonts
RUN echo ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true | sudo debconf-set-selections
RUN apt install ttf-mscorefonts-installer
RUN fc-cache -f

# Add udev rule to allow all users non-root acces to the stream deck device
RUN echo 'SUBSYSTEMS=="usb", ATTRS{idVendor}=="0fd9", GROUP="users", TAG+="uaccess"' >> /etc/udev/rules.d/10-streamdeck.rules

# copy all files into docker
COPY . /usr/local/py-stream

WORKDIR /usr/local/py-stream


# Install pip
RUN apt-get -y install python3-pip

# Install required pip packages
RUN pip install -r install/requirements.txt


# Create empty sqlite database

RUN python3 src/manage.py migrate

# Install nodejs and npm for the GUI
RUN apt -y install nodejs
RUN apt -y install npm

# Create static files of the GUI
WORKDIR /usr/local/py-stream/ui
RUN npm install
RUN npm run build
RUN cp -a dist/. ../src/frontend

WORKDIR /usr/local/py-stream/src

EXPOSE 8000
CMD ["python3","manage.py", "runserver", "0.0.0.0:8000", "--noreload"]