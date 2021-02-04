
from .streamdeck_functions import (
    get_streamdecks, init_streamdeck,
    update_key_image, update_key_change_callback, run_key_command,
    change_to_folder, update_streamdeck)
"""
Initializes all connected streamdecks
"""


def streamdecks_init():
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


def update_key_display(streamdeckKey):
    update_key_image(None, streamdeckKey, False)


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
