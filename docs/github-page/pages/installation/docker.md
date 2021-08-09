---
layout: page
title: Docker
permalink: /installation/docker
parent: Installation
nav_order: 2
---


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
