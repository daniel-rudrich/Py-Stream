import time
from StreamDeck.DeviceManager import DeviceManager
from streamdeck.models import (
    Streamdeck, StreamdeckModel, StreamdeckKey, Folder)

from .image_handling import (
    update_key_image, start_animated_images, clear_image_threads,
    create_full_deck_sized_image, crop_key_image_from_deck_sized_image)
from .command_functions import run_key_command, clear_command_threads

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

    active_streamdeck = Streamdeck.objects.filter(
        serial_number=streamdeck_serialnumber)[0]
    deck = decks[streamdeck_serialnumber]

    # load image that covers the whole deck if existing else
    # load images of all single stream deck keys
    if not active_streamdeck.full_deck_image:
        # Load all keys onto the streamdeck
        for key in keys:
            update_key_image(deck, key, False)
        start_animated_images(deck, folder_id)
    else:
        update_full_deck_image(deck, active_streamdeck.full_deck_image.name)
        pass

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
    folder = Folder.objects.get(id=folder_id)
    list_key = list(
        StreamdeckKey.objects.filter(folder=folder))
    return list_key


def get_deck(streamdeck_serialnumber):
    """
    Return deck of stream deck key

    :param model_streamdeckKey: stream deck key to find stream deck
    :returns stream deck or None if there is no active stream deck corresponding to the key
    """
    global decks
    key = streamdeck_serialnumber
    if key in decks:
        return decks[key]
    else:
        return None


def delete_folder(folder):
    """
    Deletes a folder and all its subfolders

    :param folder: folder object
    """

    keys = get_active_keys(folder.id)
    for key in keys:
        if key.change_to_folder is not None and key.number != 0:
            delete_folder(key.change_to_folder)

    folder.delete()


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


def check_connected_decks():
    """
    Checks for connected stream decks, initializes newly connected ones and
    cleanes up after stream decks disconnect
    """

    while True:

        global decks
        connected_decks = get_streamdecks()

        # if the number of "active" stream decks is different to the number of connected stream decks
        # all "active" stream decks will be closed and all connected stream decks will be initialized

        if len(decks) != len(connected_decks):
            # remove all "active" stream decks
            for deck in decks.items():
                deck[1].close()
            clear_command_threads()
            clear_image_threads()
            decks.clear()

            # initialize all connected stream decks
            for streamdeck in connected_decks:
                init_streamdeck(streamdeck)

        time.sleep(3)


def update_full_deck_image(deck, image_filename):
    """
    Project full size image onto Stream deck

    :param deck: stream deck
    :param image_filename: filename of image
    """

    # load all key images if there is not a full sized image to be set

    if image_filename == "":
        list_key = get_active_keys(active_folder)
        for key in list_key:
            update_key_image(deck, key, False)
        start_animated_images(deck, active_folder)
    else:
        key_spacing = (36, 36)
        full_image = create_full_deck_sized_image(deck, key_spacing, image_filename)

        clear_image_threads()

        clear_command_threads()

        key_images = dict()
        for k in range(deck.key_count()):
            key_images[k] = crop_key_image_from_deck_sized_image(deck, full_image, key_spacing, k)

        # Draw the individual key images to each of the keys.
        for k in range(deck.key_count()):
            key_image = key_images[k]

            # Show the section of the main image onto the key.
            deck.set_key_image(k, key_image)


def init_streamdeck(deck):
    """
    Initializes a streamdeck connection and all its keys

    :param deck: stream deck
    """
    deck.open()
    deck.reset()

    serial_number = get_serial_number(deck)
    decks[serial_number] = deck
    print("Opened '{}' device (serial number: '{}')".format(
        deck.deck_type(), serial_number))

    streamdeck_database_init(deck)
    active_streamdeck = Streamdeck.objects.filter(
        serial_number=serial_number)[0]

    deck.set_brightness(active_streamdeck.brightness)

    # Get all keys from the default folder of the streamdeck.
    # Create the keys and the folder if necessary
    global active_folder

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
        active_folder = default_folder.id
    else:
        # Get all active keys
        active_folder = active_streamdeck.default_folder.id
        list_key = get_active_keys(active_folder)

    # load image that covers the whole deck if existing else
    # load images of all single stream deck keys
    if not active_streamdeck.full_deck_image:
        # Load all keys onto the streamdeck
        for key in list_key:
            update_key_image(deck, key, False)
        start_animated_images(deck, active_folder)
    else:
        update_full_deck_image(deck, active_streamdeck.full_deck_image.name)
        pass

    deck.set_key_callback(key_change_callback)
