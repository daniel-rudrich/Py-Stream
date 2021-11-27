from .streamdeck_functions import (
    check_connected_decks,
    update_key_change_callback, run_commands,
    change_to_folder, update_streamdeck, check_deck_connection,
    key_in_folder, get_deck, delete_folder, update_full_deck_image,
    reset_screensaver_time, reset_screensaver)
from .image_handling import update_key_image, render_key_image
from sys import platform as _platform
import os
import threading


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

    # start thread which periodically checks for connected stream decks
    thread = threading.Thread(target=check_connected_decks)
    thread.daemon = True
    thread.start()


def execute_key_command(model_streamdeckKey):
    """
    Runs the command of a streamdeck key

    :param model_streamdeckKey: stream deck key
    """

    run_commands(model_streamdeckKey)


def update_key_display(streamdeckKey):
    """
    Updates the display of a key after e.g. updating
    the key in the database

    :param: streamdeckKey: stream deck key
    """
    if key_in_folder(streamdeckKey):
        reset_screensaver_time(streamdeckKey.streamdeck.serial_number)
        deck = get_deck(streamdeckKey.streamdeck.serial_number)
        update_key_image(deck, streamdeckKey, False)


def update_deck_image(streamdeck):
    """
    Update full size image of stream deck

    :param streamdeck: stream deck to update
    """

    deck = get_deck(streamdeck.serial_number)
    update_full_deck_image(deck, streamdeck.full_deck_image.name)
    reset_screensaver(streamdeck)


def get_key_image(model_streamdeckKey):
    """
    Get rendered image of stream deck key

    :param model_streamdeckKey: stream deck key
    :returns: rendered image or None if the key does not belong to an active stream deck
    """

    deck = get_deck(model_streamdeckKey.streamdeck.serial_number)
    if deck is not None:
        return render_key_image(deck, model_streamdeckKey, True)
    else:
        return None


def update_key_behavior(streamdeckKey):
    """
    Updates the key behavior of the streamdeckkeys
    Use after updating commands of streamdeckkeys in the database

    :param streamdeckKey: stream deck key
    """
    update_key_change_callback(
        streamdeckKey.streamdeck.id, streamdeckKey.folder.id)


def change_folder(folder_id, serial_number):
    """
    Updates streamdeck when changing folder

    :param folder_id: id of folder
    :param serial_number: serial number of active stream deck
    """
    change_to_folder(folder_id, serial_number)


def delete_folders(folder):
    """
    Delete Folder and all its subfolders

    :param folder: folder object
    """
    delete_folder(folder)


def update_brightness(streamdeck):
    """
    Update streamdeck brightness

    :param streamdeck: active stream deck
    """
    reset_screensaver_time(streamdeck.serial_number)
    update_streamdeck(streamdeck)


def refresh_screensaver(streamdeck):
    """
    Refresh the screensaver after changing the screensaver trigger time

    :param streamdeck: stream deck which should be modified
    """
    reset_screensaver(streamdeck)


def check_connection(streamdeck):
    """
    Check for streamdeck connection

    :param streamdeck: streamdeck which should be checked
    """
    return check_deck_connection(streamdeck)
