from .streamdeck_functions import (
    get_streamdecks, init_streamdeck,
    update_key_change_callback, run_key_command,
    change_to_folder, update_streamdeck, check_deck_connection,
    key_in_folder, get_deck)
from .image_handling import update_key_image
from sys import platform as _platform
import os
"""
Initializes all connected streamdecks
"""


def streamdecks_init():

    # set correct backend for pynput
    if _platform == "linux" or _platform == "linux2":
        os.environ["PYNPUT_BACKEND"] = "xorg"
    elif _platform == "darwin":
        os.environ["PYNPUT_BACKEND"] = "darwin"
    elif _platform == "win32":
        os.environ["PYNPUT_BACKEND"] = "win32"
    else:
        os.environ["PYNPUT_BACKEND"] = "xorg"
    streamdecks = get_streamdecks()
    for deck in streamdecks:
        init_streamdeck(deck)


"""
Runs the command of a streamdeck key in a shell
and prints the outcome
"""


def execute_key_command(model_streamdeckKey):

    run_key_command(model_streamdeckKey)


"""
Updates the display of a key after e.g. updating
the key in the database
"""


def update_key_display(streamdeckKey, state=False):
    if key_in_folder(streamdeckKey):
        deck = get_deck(streamdeckKey)
        update_key_image(deck, streamdeckKey, state)


"""
Updates the key behavior of the streamdeckkeys
Use after updating commands of streamdeckkeys in the database
"""


def update_key_behavior(streamdeckKey):

    update_key_change_callback(
        streamdeckKey.streamdeck.id, streamdeckKey.folder.id)


"""
Updates streamdeck when changing folder
"""


def change_folder(folder_id):
    change_to_folder(folder_id)


"""
Update streamdeck brightness after change
"""


def update_brightness(streamdeck):
    update_streamdeck(streamdeck)


"""
Check for streamdeck connection
"""


def check_connection(streamdeck):

    return check_deck_connection(streamdeck)
