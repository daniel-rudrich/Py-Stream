---
layout: page
title: Usage
permalink: /usage/
has_children: true
nav_order: 3
---

## Usage

After everything is installed the software can be run via the [run.sh](./run.sh) script which starts the virtual environment and the Django server (this is not needed when running the docker image). 
The software offers several features such as:

- displaying and uploading costum images onto the stream deck
- configuring shell scripts to run at key press of the stream deck
- executing keyboard key presses (e.g. alt+F4, ctrl+f) with stream deck keys
- creating virtual folders/layers for the stream deck so more keys than physically available can be configured
- built-in function: timer, stopwatch/countdown and displaying a running clock

If you don't want to or can't use the GUI you can use the REST API. See the [docs](./docs/REST_API.md) for more information.