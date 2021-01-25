import os
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


"""
returns everything needed to add a streamkey_model as actual
key to the streamdeck
"""


def get_key_style(model_streamdeckKey):

    if not model_streamdeckKey.image_source:
        icon = os.path.join(MEDIA_PATH, "blank.png")
    else:
        icon = os.path.join(MEDIA_PATH, model_streamdeckKey.image_source.name)
    return {
        "name": model_streamdeckKey.number,
        "icon": icon,
        "font": os.path.join(ASSETS_PATH, "Roboto-Regular.ttf"),
        "label": model_streamdeckKey.text
    }


"""
 Creates a new key image based on the key index, style and current key state
 and updates the image on the StreamDeck.
"""


def update_key_image(deck, model_streamdeckkey, state):
    # Determine what icon and label to use on the generated key.
    key_style = get_key_style(model_streamdeckkey)
    # Generate the custom key with the requested image and label.
    image = render_key_image(
        deck, key_style["icon"], key_style["font"], key_style["label"])
    # Use a scoped-with on the deck to ensure we're the only thread using it
    # right now.
    with deck:
        # Update requested key with the generated image.
        deck.set_key_image(model_streamdeckkey.number, image)


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
    deck = get_active_streamdeck(active_streamdeck)
    deck.set_key_callback(key_change_callback)


"""
Generates a custom tile with run-time generated text and custom image via the
PIL module.
"""


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


"""
This method is called when a physical key is pressed
"""


def key_change_callback(deck, key, state):
    list_key = get_active_keys(active_streamdeck, active_folder)

    if state:
        run_key_command(list_key[key])


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
Get the active streamdeck fitting the streamdeck model
"""


def get_active_streamdeck(model_streamdeck):
    decks = get_streamdecks()
    return decks[0]
    """
    funktioniert erstmal nicht, aber da wir erstmal nur 1 deck gleichzeitig haben ists egal :D
    for deck in decks:
        print(deck.get_serial_number())
        if deck.get_serial_number() == model_streamdeck.serial_number:
            return deck"""


"""
Check for Streamdeck in database.
Create a new one with corresponding StreamdeckModel if it doesn't exist
yet
"""


def streamdeck_database_init(deck):
    if not Streamdeck.objects.filter(serial_number=deck.get_serial_number()):
        print(deck.get_serial_number())
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

        Streamdeck.objects.create(name=deck.deck_type(),
                                  serial_number=deck.get_serial_number(),
                                  brightness=30,
                                  streamdeck_model=streamdeckmodel
                                  )


"""
Initializes a streamdeck connection and all its keys
"""


def init_streamdeck(deck):
    deck.open()
    deck.reset()

    print("Opened '{}' device (serial number: '{}')".format(
        deck.deck_type(), deck.get_serial_number()))

    streamdeck_database_init(deck)

    global active_streamdeck
    active_streamdeck = Streamdeck.objects.filter(
        serial_number=deck.get_serial_number())[0]

    deck.set_brightness(active_streamdeck.brightness)

    # Get all keys from the default folder of the streamdeck.
    # Create the keys and the folder if necessary

    list_key = []
    keys = StreamdeckKey.objects.filter(streamdeck=active_streamdeck.id)
    if not keys:
        # Initialize folder and keys
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
        # Get default folder id and all the corresponding keys
        # (seems to complicated maybe add streamdeck as foreignkey to folder)
        list_key = get_active_keys(active_streamdeck, 'default')

    # Load all keys onto the streamdeck
    for key in list_key:
        update_key_image(deck, key, False)

    deck.set_key_callback(key_change_callback)
