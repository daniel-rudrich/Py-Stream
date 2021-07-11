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

active_folder = 0
decks = {}


def check_deck_connection(model_streamdeck):
    """
    Check if needed streamdeck is connected

    :param model_streamdeck: stream deck model entity
    """

    serial_number = model_streamdeck.serial_number

    if serial_number in decks:
        deck = decks[serial_number]
        return deck.connected()


def run_commands(model_streamdeckKey):
    """
    Run attached commands of a streamdeck key

    :param model_streamdeckKey : stream deck key with commands
    """
    global decks
    deck = decks[model_streamdeckKey.streamdeck.serial_number]
    run_key_command(deck, model_streamdeckKey)
    # changes folder if this key is meant to
    if model_streamdeckKey.change_to_folder:
        change_to_folder(model_streamdeckKey.change_to_folder.id)


def change_to_folder(folder_id):
    """
    Stop all threads of the old folder and load all the keys of the new active folder

    :param folder_id: id of folder
    """
    folder = Folder.objects.get(id=folder_id)
    global active_folder
    active_folder = folder_id
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


def update_key_change_callback(model_streamdeck_id, folder_id):
    """
    Updates the behavior of all streamdeck keys.
    This method should be used after a command of a streamdeck key was updated in the database

    :param model_streamdeck_id: id of active stream deck model entity
    :param folder_id: id of active folder
    """
    # set global variables to currently active streamdeck and folder
    active_streamdeck = Streamdeck.objects.get(id=model_streamdeck_id)
    global active_folder
    active_folder = folder_id
    deck = decks[active_streamdeck.serial_number]
    deck.set_key_callback(key_change_callback)


def key_change_callback(deck, key, state):
    """
    This method is called when a physical key is pressed

    :param deck: stream deck needed for the stream deck library
    :param key: number of pressed key
    :param state: run command if true
    """
    list_key = get_active_keys(active_folder)

    if state:
        run_commands(list_key[key])


def get_streamdecks():
    """
    Retrieves all connected streamdecks
    """
    streamdecks = DeviceManager().enumerate()
    return streamdecks


def get_active_keys(folder_id):
    """
    Get all keys of folder with folder_id

    :param folder_id: id of folder
    :returns list of all active keys
    """
    list_key = []
    folder = Folder.objects.get(id=folder_id)
    keys = list(
        StreamdeckKey.objects.filter(folder=folder))
    list_key.extend(keys)
    return list_key


def get_deck(model_streamdeckKey):
    """
    Return deck of stream deck key

    :param model_streamdeckKey: stream deck key to find stream deck
    """
    global decks
    return decks[model_streamdeckKey.streamdeck.serial_number]


def update_streamdeck(model_streamdeck):
    """
    Update brightness of stream deck

    :params model_streamdeck: stream deck model entity
    """

    deck = decks[model_streamdeck.serial_number]
    brightness = int(model_streamdeck.brightness)
    deck.set_brightness(brightness)


def streamdeck_database_init(deck):
    """
    Check for stream deck in database.
    Create a new one with corresponding StreamdeckModel if it doesn't exist yet

    :params deck: stream deck
    """
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


def get_serial_number(deck):
    """
    Remove unwanted characters from the end of the serial number
    and return sanatized serial number

    :params deck: stream deck
    :returns correct serial number of stream deck
    """
    serialnumber = deck.get_serial_number()
    serialnumber = serialnumber.replace("\x00", "").replace("\x01", "")
    return serialnumber


def key_in_folder(model_streamdeckKey):
    """
    Check if key is in active folder

    :param model_streamdeckKey: stream deck key
    """
    global active_folder
    return active_folder == model_streamdeckKey.folder.id


def init_streamdeck(deck):
    """
    Initializes a streamdeck connection and all its keys

    :param deck: stream deck
    """
    deck.open()
    deck.reset()

    decks[get_serial_number(deck)] = deck
    print("Opened '{}' device (serial number: '{}')".format(
        deck.deck_type(), get_serial_number(deck)))

    streamdeck_database_init(deck)
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
        # Get all active keys
        global active_folder
        active_folder = active_streamdeck.default_folder.id
        list_key = get_active_keys(active_folder)

    # Load all keys onto the streamdeck
    for key in list_key:
        update_key_image(deck, key, False)

    start_animated_images(deck)

    deck.set_key_callback(key_change_callback)
