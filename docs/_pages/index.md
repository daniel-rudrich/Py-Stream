---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: single
title: Linux Stream Deck Application
permalink: /
header:
  image: "/assets/images/landing.PNG"
---

This is an application for the Elgato Stream Deck which functionalities should be comparable to the officially provided Software of Elgato. The key difference is: this software is working under Linux and is fully open-source! Furthermore the GUI is provided via a one-page website which means the stream deck is configurable from other devices in the same network which the stream deck is not directly connected to via USB.
The GUI communicates with the backend via a REST API, so if you don't like it feel free to build a new one using the REST API!

All the communication to the stream deck is done with the [Python Elgato Stream Deck Library](https://github.com/abcminiuser/python-elgato-streamdeck)! 

# Key Features

* Compatible with Linux
* Displaying and uploading costum images onto the stream deck
* Rest Api and Gui to configure the stream deck
* Software runs Django server so the GUI and REST API are accessible through the local network if needed
* Configuring shell scripts to run at key press of the stream deck
* Executing key presses/hotkeys (e.g. ctrl+f) with stream deck keys
* Possibility to create an endless amount of creating layers of keys though folders and subfolders
* Displaying an image over all keys
* Built-in functions: time, stopwatch, clock display, intervall commands and screensaver
	
# Credits

## Creater

Daniel Rudrich

* https://daniel-rudrich.github.io

Other:

* [Stream Deck Library](https://github.com/abcminiuser/python-elgato-streamdeck)
* [Django](https://www.djangoproject.com/)
* [VueJs](https://vuejs.org/)
* [Travis-Ci](https://travis-ci.org/)
* [minimal-mistakes](https://mademistakes.com/work/minimal-mistakes-jekyll-theme/)
