import os
import subprocess
import threading
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from StreamDeck.ImageHelpers import PILHelper
from StreamDeck.DeviceManager import DeviceManager
from streamdeck.models import (
    Streamdeck, StreamdeckModel, StreamdeckKey, Folder)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ASSETS_PATH = os.path.join(BASE_DIR, "assets")
MEDIA_PATH = os.path.join(BASE_DIR, "media")

active_streamdeck = None
active_folder = "default"


def run_key_command(streamdeckKey):

    key_command = streamdeckKey.command
    if key_command:
        process = subprocess.Popen(
            key_command.command_string.split(), stdout=subprocess.PIPE)
        print(process.communicate()[0])


def update_key_change_callback(model_streamdeck_id, folder_id):
    # set global variables to currently active streamdeck and folder
    global active_streamdeck
    active_streamdeck = Streamdeck.objects.get(id=model_streamdeck_id)
    global active_folder
    active_folder = Folder.objects.get(id=folder_id).name

    # get the streamdeck coresponding to the streamdeck model
    decks = get_streamdecks()
    for deck in decks:
        if deck.get_serial_number() == active_streamdeck.serial_number:
            # set key_callback function with newly set acive streamdeck and
            # folder
            deck.set_key_callback(key_change_callback)

# returns everything needed to add a streamkey_model as actual
# key to the streamdeck


def get_key_style(streamdeckKey):

    if not streamdeckKey.image_source:
        icon = os.path.join(MEDIA_PATH, "blank.png")
    else:
        icon = os.path.join(MEDIA_PATH, streamdeckKey.image_source)
    return {
        "name": streamdeckKey.number,
        "icon": icon,
        "font": os.path.join(ASSETS_PATH, "Roboto-Regular.ttf"),
        "label": streamdeckKey.text
    }

# Generates a custom tile with run-time generated text and custom image via the
# PIL module.


def render_key_image(deck, icon_filename, font_filename, label_text):
    # Resize the source image asset to best-fit the dimensions of a single key,
    # leaving a margin at the bottom so that we can draw the key title
    # afterwards.
    icon = Image.open(icon_filename)
    image = PILHelper.create_scaled_image(deck, icon, margins=[0, 0, 20, 0])
    # Load a custom TrueType font and use it to overlay the key index, draw key
    # label onto the image a few pixels from the bottom of the key.
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(font_filename, 14)
    draw.text((image.width / 2, image.height - 5), text=label_text,
              font=font, anchor="ms", fill="white")

    return PILHelper.to_native_format(deck, image)

# Creates a new key image based on the key index, style and current key state
# and updates the image on the StreamDeck.


def update_key_image(deck, key, state):
    # Determine what icon and label to use on the generated key.
    key_style = get_key_style(key)
    # Generate the custom key with the requested image and label.
    image = render_key_image(
        deck, key_style["icon"], key_style["font"], key_style["label"])
    # Use a scoped-with on the deck to ensure we're the only thread using it
    # right now.
    with deck:
        # Update requested key with the generated image.
        deck.set_key_image(key.number, image)

# method which is called when pressing a key


def key_change_callback(deck, key, state):
    list_key = get_active_keys(active_streamdeck, active_folder)

    if state:
        run_key_command(list_key[key])


def get_streamdecks():
    streamdecks = DeviceManager().enumerate()
    return streamdecks


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


def init_streamdeck(deck):
    deck.open()
    deck.reset()

    print("Opened '{}' device (serial number: '{}')".format(
        deck.deck_type(), deck.get_serial_number()))

    """
    Check for Streamdeck in database.
    Create a new one with corresponding StreamdeckModel if it doesn't exist yet
    """

    if not Streamdeck.objects.filter(serial_number=deck.get_serial_number()):
        """
        Check for StreamdeckModel in database.
        Create a new one if it doesn't exist yet
        """
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
        deck.set_brightness(30)
        Streamdeck.objects.create(name=deck.deck_type(),
                                  serial_number=deck.get_serial_number(),
                                  brightness=30,
                                  streamdeck_model=streamdeckmodel
                                  )

    global active_streamdeck
    active_streamdeck = Streamdeck.objects.filter(
        serial_number=deck.get_serial_number())[0]

    """
    Get all keys from the default folder of the streamdeck.
    Create the keys and the folder if necessary
    """
    list_key = []
    keys = StreamdeckKey.objects.filter(streamdeck=active_streamdeck.id)
    if not keys:
        """
        Initialize folder and keys
        """
        new_folder = Folder.objects.create(name='default')

        for i in range(deck.key_count()):
            new_key = StreamdeckKey.objects.create(
                number=i,
                text="",
                folder=new_folder,
                streamdeck=active_streamdeck
            )
            list_key.append(new_key)
    else:
        """
        Get default folder id and all the corresponding keys
        (seems to complicated maybe add streamdeck as foreignkey to folder)
        """
        list_key = get_active_keys(active_streamdeck, 'default')

    """
    Load all keys onto the streamdeck
    """
    for key in list_key:
        update_key_image(deck, key, False)

    """test_key = StreamdeckKey.objects.filter(id=list_key[0].id)
    test_command = Command.objects.create(
        name="Test", command_string="echo test")
    test_key.update(command=test_command)"""
    deck.set_key_callback(key_change_callback)
    """
    the streamdeck only closes here for testing purposes.
    in reality it should close when the application is stopped
    """
    # deck.close()

    for t in threading.enumerate():
        if t is threading.currentThread():
            continue
        if t.is_alive():
            t.join()


def streamdeck_init():
    streamdecks = get_streamdecks()
    for deck in streamdecks:
        init_streamdeck(deck)


if __name__ == "__main__":
    streamdeck_init()
