import subprocess

from .streamdeck_functions import (
    get_streamdecks, init_streamdeck,
    update_key_image, get_active_streamdeck,
    update_key_change_callback)
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


def run_key_command(model_streamdeckKey):

    key_command = model_streamdeckKey.command
    if key_command:
        process = subprocess.Popen(
            key_command.command_string.split(), stdout=subprocess.PIPE)
        print(process.communicate()[0])


"""
Updates the display of a key after e.g. updating
the key in the database
"""


def update_key_display(streamdeckkey):
    deck = get_active_streamdeck()
    update_key_image(deck, streamdeckkey, False)


"""
Updates the key behavior of the streamdeckkeys
Use after updating commands of streamdeckkeys in the database
"""


def update_key_behavior(streamdeck_id, active_folder_id):

    update_key_change_callback(streamdeck_id, active_folder_id)
