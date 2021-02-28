import os
import subprocess
from pathlib import Path
from io import BytesIO
import cairosvg

from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
from pynput.keyboard import Key, Controller, KeyCode
from StreamDeck.ImageHelpers import PILHelper
from StreamDeck.DeviceManager import DeviceManager
from streamdeck.models import (
    Streamdeck, StreamdeckModel, StreamdeckKey, Folder, Hotkeys)

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
Runs the command of a streamdeck key in a shell
and prints the outcome
"""


def run_key_command(model_streamdeckKey):

    key_command = model_streamdeckKey.command
    while key_command:
        if key_command.command_type == 'shell':
            process = subprocess.Popen(
                key_command.command_string.split(), stdout=subprocess.PIPE,
                cwd=key_command.active_directory)
            print(process.communicate()[0])
            key_command = key_command.following_command
        elif key_command.command_type == 'hotkey':
            hotkey_function(key_command.hotkeys)
            key_command = key_command.following_command

    # changes folder if this key is meant to
    if model_streamdeckKey.change_to_folder:
        change_to_folder(model_streamdeckKey.change_to_folder.id)


"""
Presses given hotkeys on keyboard
"""


def hotkey_function(hotkeys):
    keycodes = [hotkeys.key1, hotkeys.key2,
                hotkeys.key3, hotkeys.key4, hotkeys.key5]
    keyboard = Controller()

    for code in reversed(keycodes):
        if code:
            keyboard.press(KeyCode.from_vk(code))

    for code in keycodes:
        if code:
            keyboard.release(KeyCode.from_vk(code))


def parse_keys(keystring):
    splitKeys = keystring.split("+")
    keys = []
    key_dict = {
        "space": Key.space,
        "enter": Key.enter,
        "esc": Key.esc,
        "shift": Key.shift,
        "ctrl": Key.ctrl,
        "ctrl_l": Key.ctrl_l,
        "ctrl_r": Key.ctrl_r,
        "alt": Key.alt,
        "alt_l": Key.alt_l,
        "alt_r": Key.alt_r,
        "alt_gr": Key.alt_gr,
        "backspace": Key.backspace,
        "caps_lock": Key.caps_lock,
        "cmd": Key.cmd,
        "cmd_l": Key.cmd_l,
        "cmd_r": Key.cmd_r,
        "del": Key.delete,
        "insert": Key.insert,
        "home": Key.home,
        "page_down": Key.page_down,
        "page_up": Key.page_up,
        "pause": Key.pause,
        "print_screen": Key.print_screen,
        "down": Key.down,
        "left": Key.left,
        "up": Key.up,
        "right": Key.right,
        "end": Key.end,
        "f1": Key.f1,
        "f2": Key.f2,
        "f3": Key.f3,
        "f4": Key.f4,
        "f5": Key.f5,
        "f6": Key.f6,
        "f7": Key.f7,
        "f8": Key.f8,
        "f9": Key.f9,
        "f10": Key.f10,
        "f11": Key.f11,
        "f12": Key.f12,
        "media_next": Key.media_next,
        "media_play_pause": Key.media_play_pause,
        "media_previous": Key.media_previous,
        "media_volume_down": Key.media_volume_down,
        "media_volume_up": Key.media_volume_up,
        "media_volume_mute": Key.media_volume_mute,
    }

    for key in splitKeys:
        if key in key_dict:
            keys.append(key_dict[key])
        else:
            keys.append(key)
    return keys


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

    for key in keys:
        update_key_image(None, key, False)

    update_key_change_callback(keys[0].streamdeck.id, folder_id)


"""
returns everything needed to add a streamkey_model as actual
key to the streamdeck
"""


def get_key_style(model_streamdeckKey):

    if not model_streamdeckKey.image_source:
        icon = None
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
    if not deck:
        deck = decks[model_streamdeckkey.streamdeck.serial_number]

    key_style = get_key_style(model_streamdeckkey)
    # Generate the custom key with the requested image and label.
    if(not key_style["icon"]):
        key_style["icon"] = PILHelper.create_image(deck)
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
    deck = decks[active_streamdeck.serial_number]
    deck.set_key_callback(key_change_callback)


"""
Generates a custom tile with run-time generated text and custom image via the
PIL module.
"""


def render_key_image(deck, icon_filename, font_filename, label_text):
    # Resize the source image asset to best-fit the dimensions of a single key,
    # leaving a margin at the bottom so that we can draw the key title
    # afterwards.
    try:
        icon = Image.open(icon_filename)
    except AttributeError:
        icon = icon_filename
    except UnidentifiedImageError:
        out = BytesIO()
        cairosvg.svg2png(url=icon_filename, write_to=out)
        icon = Image.open(out)

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
    if not Streamdeck.objects.filter(serial_number=deck.get_serial_number()):
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
                                  serial_number=deck.get_serial_number(),
                                  brightness=30,
                                  streamdeck_model=streamdeckmodel,
                                  default_folder=new_folder
                                  )


"""
Initializes a streamdeck connection and all its keys
"""


def init_streamdeck(deck):
    deck.open()
    deck.reset()

    decks[deck.get_serial_number()] = deck
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

    global active_decks
    deck.set_key_callback(key_change_callback)
