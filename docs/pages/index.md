---
# Feel free to add content and custom Front Matter to this file.
# To modify the layout, see https://jekyllrb.com/docs/themes/#overriding-theme-defaults

layout: home
title: Home
permalink: /
nav_order: 1
---

# Linux Stream Deck Application

This is an application for the Elgato Stream Deck which functionalities should be comparable to the officially provided Software of Elgato. The key difference is: this software is working under Linux and is fully open-source! Furthermore the GUI is provided via a one-page website which means the stream deck is configurable from other devices in the same network which the stream deck is not directly connected to via USB.
The GUI communicates with the backend via a REST API, so if you don't like it feel free to build a new one using the REST API!

All the communication to the stream deck is done with the [Python Elgato Stream Deck Library](https://github.com/abcminiuser/python-elgato-streamdeck)! 