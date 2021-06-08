# Linux Stream Deck Application

This is an application for the Elgato Stream Deck which functionalities should be comparable to the officially provided Software of Elgato. The key difference is: this software is working under Linux and is fully open-source! Furthermore the GUI is provided via a one-page website which means the stream deck is configurable from other devices in the same network which the stream deck is not directly connected to via USB.
The GUI communicates with the backend via a REST API, so if you don't like it feel free to build a new one using the REST API!
All the communication to the stream deck is done with the [Python Elgato Stream Deck Library](https://github.com/abcminiuser/python-elgato-streamdeck)! 

## Installation

TODO

## Usage

After everything is installed the software offers several features such as:

- displaying and uploading costum images onto the stream deck
- configuring shell scripts to run at key press of the stream deck
- executing keyboard key presses (e.g. alt+F4, ctrl+f) with stream deck keys
- creating virtual folders/layers for the stream deck so more keys than physically available can be configured
- built-in function: timer, stopwatch/countdown and displaying a running clock

## Contributing
[Contributing](./docs/CONTRIBUTING.md)


## License
[MIT](./docs/LICENSE)
