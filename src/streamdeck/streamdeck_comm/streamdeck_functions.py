import time
import threading
from StreamDeck.DeviceManager import DeviceManager
from streamdeck.models import (
    Streamdeck, StreamdeckModel, StreamdeckKey, Folder)
from functools import partial
from .image_handling import (
    update_key_image, start_animated_images, clear_image_threads,
    create_full_deck_sized_image, crop_key_image_from_deck_sized_image)
from .command_functions import check_for_active_command, run_key_command, clear_command_threads

# the dictionary keys are always the serial_number of the stream deck
active_folder = {}
decks = {}
screensaver_threads = {}
stop_screensaver = {}
screensaver_current_times = {}


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
        change_to_folder(model_streamdeckKey.change_to_folder.id, model_streamdeckKey.streamdeck.serial_number)


def change_to_folder(folder_id, deck_serial_number):
    """
    Stop all threads of the old folder and load all the keys of the new active folder

    :param folder_id: id of folder
    """

    folder = Folder.objects.get(id=folder_id)
    keys = StreamdeckKey.objects.filter(folder=folder)

    global active_folder
    active_folder[deck_serial_number] = folder_id

    if not check_deck_connection(keys[0].streamdeck):
        pass

    # stop all threads of the current folder before changing
    clear_image_threads(deck_serial_number)

    clear_command_threads(deck_serial_number)

    active_streamdeck = Streamdeck.objects.filter(
        serial_number=deck_serial_number)[0]
    deck = decks[deck_serial_number]

    # load image that covers the whole deck if existing else
    # load images of all single stream deck keys
    if not active_streamdeck.full_deck_image:
        # Load all keys onto the streamdeck
        for key in keys:
            update_key_image(deck, key, False)
        start_animated_images(deck, folder_id, deck_serial_number)
    else:
        update_full_deck_image(deck, active_streamdeck.full_deck_image.name)
        pass

    # update_key_change_callback(keys[0].streamdeck.id, folder_id)


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
    active_folder[active_streamdeck.serial_number] = folder_id
    deck = decks[active_streamdeck.serial_number]
    deck.set_key_callback(partial(_key_change_callback, active_streamdeck.serial_number))


def _key_change_callback(serial_number, deck, key, state):
    """
    Wrapper for the key_change_callback function which holds all functionalities
    as the serialnumber can be used here
    :param serial_number: serial number of stream deck
    :param deck: stream deck needed for the stream deck library
    :param key: number of pressed key
    :param state: run command if true
    """
    reset_screensaver_time(serial_number)
    list_key = get_active_keys(active_folder[serial_number])
    if state:
        run_commands(list_key[key])


def key_change_callback(deck, key, state):
    """
    This method is called when a physical key is pressed
    :param deck: stream deck needed for the stream deck library
    :param key: number of pressed key
    :param state: state of key
    """
    pass


def reset_screensaver_time(serial_number):
    """
    Sets the screensaver time back to 0 of stream deck

    :param serial_number: serial number of stream deck
    """

    global screensaver_current_times
    screensaver_current_times[serial_number] = 0


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
    with deck:
        serialnumber = deck.get_serial_number()
        serialnumber = serialnumber.replace("\x00", "").replace("\x01", "")
        return serialnumber


def key_in_folder(model_streamdeckKey):
    """
    Check if key is in active folder

    :param model_streamdeckKey: stream deck key
    """
    serial_number = model_streamdeckKey.streamdeck.serial_number
    global active_folder
    return active_folder[serial_number] == model_streamdeckKey.folder.id


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
                serial_number = get_serial_number(deck)
                clear_image_threads(serial_number)
                clear_command_threads(serial_number)

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
    serial_number = get_serial_number(deck)

    if image_filename == "":
        list_key = get_active_keys(active_folder[serial_number])
        for key in list_key:
            update_key_image(deck, key, False)
        start_animated_images(deck, active_folder[serial_number], serial_number)
    else:
        key_spacing = (36, 36)
        full_image = create_full_deck_sized_image(deck, key_spacing, image_filename)

        clear_command_threads(serial_number)
        clear_image_threads(serial_number)

        key_images = dict()
        for k in range(deck.key_count()):
            key_images[k] = crop_key_image_from_deck_sized_image(deck, full_image, key_spacing, k)

        # Draw the individual key images to each of the keys.
        for k in range(deck.key_count()):
            key_image = key_images[k]

            # Show the section of the main image onto the key.
            deck.set_key_image(k, key_image)


def screensaver_function(deck, model_streamdeck):
    """
    Runs the screensaver functionality. Should not be run on the main thread

    :param deck: Deck for the screensaver
    :param model_streamdeck: streamdeck object of the database
    """
    s_time = int(model_streamdeck.screensaver_time)
    serial_number = model_streamdeck.serial_number

    global screensaver_current_times
    global stop_screensaver

    while not stop_screensaver[serial_number]:

        # count idle time until the screensaver time is reached
        while screensaver_current_times[serial_number] < s_time and not stop_screensaver[serial_number]:
            screensaver_current_times[serial_number] = screensaver_current_times[serial_number] + 1
            time.sleep(1)

        if stop_screensaver[serial_number]:
            break

        if check_for_active_command(serial_number):
            screensaver_current_times[serial_number] = 0
            continue
        # stop animated images and clock images
        clear_image_threads(serial_number)

        # display screensaver image on the streamdeck
        update_full_deck_image(deck, model_streamdeck.screensaver_image.name)

        # stop the screensaver when the time is set to 0 again
        while screensaver_current_times[serial_number] > 0 and not stop_screensaver[serial_number]:
            time.sleep(1)

        # load all key images onto the stream deck again and start the relevant
        # image threads
        update_full_deck_image(deck, model_streamdeck.full_deck_image.name)


def reset_screensaver(model_streamdeck):
    """
    Restart screensaver function to retrieve updated screensaver times

    :param model_streamdeck: stream deck from the database
    """
    serial_number = model_streamdeck.serial_number
    deck = decks[serial_number]

    global stop_screensaver
    stop_screensaver[serial_number] = True
    global screensaver_current_times
    screensaver_current_times[serial_number] = 0

    global screensaver_threads

    if(screensaver_threads[serial_number] is not None):
        screensaver_threads[serial_number].join()

    stop_screensaver[serial_number] = False
    # start screensaver thread
    screensaver_threads[serial_number] = threading.Thread(target=screensaver_function, args=[
        deck, model_streamdeck])
    screensaver_threads[serial_number].start()


def init_screensaver(deck, streamdeck_model):
    thread = threading.Thread(target=screensaver_function, args=[
        deck, streamdeck_model])

    serial_number = streamdeck_model.serial_number
    global stop_screensaver
    stop_screensaver[serial_number] = False

    global screensaver_current_times
    screensaver_current_times[serial_number] = 0

    global screensaver_threads
    screensaver_threads[serial_number] = thread
    screensaver_threads[serial_number].start()


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
        active_folder[serial_number] = default_folder.id
    else:
        # Get all active keys
        active_folder[serial_number] = active_streamdeck.default_folder.id
        list_key = get_active_keys(active_folder[serial_number])

    # load image that covers the whole deck if existing else
    # load images of all single stream deck keys
    if not active_streamdeck.full_deck_image:
        # Load all keys onto the streamdeck
        for key in list_key:
            update_key_image(deck, key, False)
        start_animated_images(deck, active_folder[serial_number], serial_number)
    else:
        update_full_deck_image(deck, active_streamdeck.full_deck_image.name)
        pass

    init_screensaver(deck, active_streamdeck)

    # a partial function is used so the serial number can be used in the callback function
    # the serial number is needed to differentiate between multiple stream decks
    deck.set_key_callback(partial(_key_change_callback, serial_number))
