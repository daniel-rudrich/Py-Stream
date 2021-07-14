from .streamdeck_functions import (
    get_streamdecks, init_streamdeck,
    update_key_change_callback, run_key_command,
    change_to_folder, update_streamdeck, check_deck_connection,
    key_in_folder, get_deck, delete_folder)
from .image_handling import update_key_image
from sys import platform as _platform
import os


def streamdecks_init():
    """
    Initialize all connected streamdecks
    """

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


def execute_key_command(model_streamdeckKey):
    """
    Runs the command of a streamdeck key

    :param model_streamdeckKey: stream deck key
    """

    run_key_command(model_streamdeckKey)


def update_key_display(streamdeckKey):
    """
    Updates the display of a key after e.g. updating
    the key in the database

    :param: streamdeckKey: stream deck key
    """
    if key_in_folder(streamdeckKey):
        deck = get_deck(streamdeckKey)
        update_key_image(deck, streamdeckKey, False)


def update_key_behavior(streamdeckKey):
    """
    Updates the key behavior of the streamdeckkeys
    Use after updating commands of streamdeckkeys in the database

    :param streamdeckKey: stream deck key
    """
    update_key_change_callback(
        streamdeckKey.streamdeck.id, streamdeckKey.folder.id)


def change_folder(folder_id):
    """
    Updates streamdeck when changing folder

    :param folder_id: id of folder
    """
    change_to_folder(folder_id)


def delete_folders(folder):
    """
    Delete Folder and all its subfolders

    :param folder: folder object
    """
    delete_folder(folder)


def update_brightness(streamdeck):
    """
    Update streamdeck brightness

    :param stream deck
    """
    update_streamdeck(streamdeck)


def check_connection(streamdeck):
    """
    Check for streamdeck connection

    :param streamdeck: stream deck
    """
    return check_deck_connection(streamdeck)
