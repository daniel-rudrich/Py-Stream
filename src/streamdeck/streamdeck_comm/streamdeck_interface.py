
from .streamdeck_functions import (
    get_streamdecks, init_streamdeck,
    update_key_image, get_active_streamdeck,
    update_key_change_callback, run_key_command)
from streamdeck.models import Streamdeck
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

# NOT WORKING -> throws error


def update_key_display(streamdeckkey):
    streamdeck_model = Streamdeck.objects.filter(
        id=streamdeckkey.streamdeck.id)[0]
    deck = get_active_streamdeck(streamdeck_model)
    update_key_image(deck, streamdeckkey, False)


"""
Updates the key behavior of the streamdeckkeys
Use after updating commands of streamdeckkeys in the database
"""


def update_key_behavior(streamdeck_id, active_folder_id):

    update_key_change_callback(streamdeck_id, active_folder_id)
