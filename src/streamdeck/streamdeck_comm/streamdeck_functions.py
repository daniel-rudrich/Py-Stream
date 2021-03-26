import os
from pathlib import Path
from StreamDeck.DeviceManager import DeviceManager
from streamdeck.models import (
    Streamdeck, StreamdeckModel, StreamdeckKey, Folder)

from .image_handling import (
    update_key_image, start_animated_images, clear_image_threads)
from .command_functions import run_key_command, clear_command_threads
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ASSETS_PATH = os.path.join(BASE_DIR, "assets")
MEDIA_PATH = os.path.join(BASE_DIR, "media")

active_streamdeck = None
active_folder = "default"
decks = {}
"""
Check if needed streamdeck is connected
"""


def check_deck_connection(model_streamdeck):
    serial_number = model_streamdeck.serial_number

    if serial_number in decks:
        deck = decks[serial_number]
        return deck.connected()


"""
Runs the command of a streamdeck key
"""


def run_commands(model_streamdeckKey):
    global decks
    deck = decks[model_streamdeckKey.streamdeck.serial_number]
    run_key_command(deck, model_streamdeckKey)
    # changes folder if this key is meant to
    if model_streamdeckKey.change_to_folder:
        change_to_folder(model_streamdeckKey.change_to_folder.id)


"""
Load all the keys of the new active folder
"""


def change_to_folder(folder_id):
    folder = Folder.objects.get(id=folder_id)
    global active_folder
    active_folder = folder.name
    keys = StreamdeckKey.objects.filter(folder=folder)

    if not check_deck_connection(keys[0].streamdeck):
        pass

    # stop all threads of the current folder before changing
    clear_image_threads()

    clear_command_threads()

    streamdeck_serialnumber = keys[0].streamdeck.serial_number
    deck = decks[streamdeck_serialnumber]

    for key in keys:
        update_key_image(deck, key, False)

    start_animated_images(deck)

    update_key_change_callback(keys[0].streamdeck.id, folder_id)


"""
Updates the behavior of all streamdeck keys.
This method should be used after a command to
streamdeck key was updated in the database
"""


def update_key_change_callback(model_streamdeck_id, folder_id):
    # set global variables to currently active streamdeck and folder
    global active_streamdeck
    active_streamdeck = Streamdeck.objects.get(id=model_streamdeck_id)
    global active_folder
    active_folder = Folder.objects.get(id=folder_id).name
    deck = decks[active_streamdeck.serial_number]
    deck.set_key_callback(key_change_callback)


"""
This method is called when a physical key is pressed
"""


def key_change_callback(deck, key, state):
    list_key = get_active_keys(active_streamdeck, active_folder)

    if state:
        run_commands(list_key[key])


"""
Retrieves all connected streamdecks
"""


def get_streamdecks():
    streamdecks = DeviceManager().enumerate()
    return streamdecks


"""
Get default folder id and all the corresponding keys
(seems to complicated maybe add streamdeck as foreignkey to folder)
"""


def get_active_keys(model_deck, foldername):
    list_key = []
    folder_ids = StreamdeckKey.objects.filter(
        streamdeck=model_deck).values("folder").distinct()
    default_folder = Folder.objects.filter(
        id__in=folder_ids, name=foldername).values('id')[0]['id']
    default_keys = list(
        StreamdeckKey.objects.filter(folder=default_folder))
    list_key.extend(default_keys)
    return list_key


"""
return deck with serialnumber
"""


def get_deck(model_streamdeckKey):
    global decks
    return decks[model_streamdeckKey.streamdeck.serial_number]


"""
Update brightness of streamdeck
"""


def update_streamdeck(model_streamdeck):
    deck = decks[model_streamdeck.serial_number]
    brightness = int(model_streamdeck.brightness)
    deck.set_brightness(brightness)


"""
Check for Streamdeck in database.
Create a new one with corresponding StreamdeckModel if it doesn't exist
yet
"""


def streamdeck_database_init(deck):
    if not Streamdeck.objects.filter(serial_number=get_serial_number(deck)):
        # Check for StreamdeckModel in database.
        # Create a new one if it doesn't exist yet

        if not StreamdeckModel.objects.filter(
                name=deck.deck_type()):

            keys_per_row = deck.key_count()/deck.KEY_ROWS
            StreamdeckModel.objects.create(
                name=deck.deck_type(),
                key_count=deck.key_count(),
                keys_per_row=keys_per_row
            )

        streamdeckmodel = StreamdeckModel.objects.filter(
            name=deck.deck_type())[0]

        new_folder = Folder.objects.create(name='default')
        Streamdeck.objects.create(name=deck.deck_type(),
                                  serial_number=get_serial_number(deck),
                                  brightness=30,
                                  streamdeck_model=streamdeckmodel,
                                  default_folder=new_folder
                                  )


"""
Remove unwanted characters from the end of the serial number
and return sanatized serial number
"""


def get_serial_number(deck):
    serialnumber = deck.get_serial_number()
    serialnumber = serialnumber.replace("\x00", "").replace("\x01", "")
    return serialnumber


"""
return wether key is in active folder
"""


def key_in_folder(model_streamdeckKey):
    global active_folder
    return active_folder == model_streamdeckKey.folder.name


"""
Initializes a streamdeck connection and all its keys
"""


def init_streamdeck(deck):
    deck.open()
    deck.reset()

    decks[get_serial_number(deck)] = deck
    print("Opened '{}' device (serial number: '{}')".format(
        deck.deck_type(), get_serial_number(deck)))

    streamdeck_database_init(deck)
    global active_streamdeck
    active_streamdeck = Streamdeck.objects.filter(
        serial_number=get_serial_number(deck))[0]

    deck.set_brightness(active_streamdeck.brightness)

    # Get all keys from the default folder of the streamdeck.
    # Create the keys and the folder if necessary

    list_key = []
    keys = StreamdeckKey.objects.filter(streamdeck=active_streamdeck.id)
    if not keys:
        # Initialize folder and keys
        default_folder = active_streamdeck.default_folder

        for i in range(deck.key_count()):
            new_key = StreamdeckKey.objects.create(
                number=i,
                text="",
                folder=default_folder,
                streamdeck=active_streamdeck
            )
            list_key.append(new_key)
    else:
        # Get default folder id and all the corresponding keys
        # (seems to complicated maybe add streamdeck as foreignkey to folder)
        list_key = get_active_keys(active_streamdeck, 'default')

    # Load all keys onto the streamdeck
    for key in list_key:
        update_key_image(deck, key, False)

    start_animated_images(deck)

    deck.set_key_callback(key_change_callback)
