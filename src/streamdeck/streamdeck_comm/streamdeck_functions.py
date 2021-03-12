import os
import subprocess
from pathlib import Path
from io import BytesIO
import cairosvg
import time
import threading
import itertools

from datetime import datetime, timedelta
from timeit import default_timer as timer
from fractions import Fraction
from PIL import (Image, ImageSequence, ImageDraw,
                 ImageFont, UnidentifiedImageError)
from pynput.keyboard import Key, Controller
from StreamDeck.ImageHelpers import PILHelper
from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.Transport.Transport import TransportError
from streamdeck.models import (
    Streamdeck, StreamdeckModel, StreamdeckKey, Folder)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ASSETS_PATH = os.path.join(BASE_DIR, "assets")
MEDIA_PATH = os.path.join(BASE_DIR, "media")

FRAMES_PER_SECOND = 30

active_streamdeck = None
active_folder = "default"
decks = {}
animated_images = {}
clock_threads = {}
stopwatch_threads = {}
interval_shell_threads = {}
stop_animation = False
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
            if key_command.interval_time > 0:
                thread = threading.Thread(target=run_shell_interval,
                                          args=[model_streamdeckKey,
                                                key_command.interval_time])
                interval_shell_threads[key_command.id] = thread
                thread.start()
            else:
                try:
                    process = subprocess.Popen(
                        key_command.command_string.split(),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        cwd=key_command.active_directory)
                    print(process.communicate()[0].decode("utf-8"))
                except:
                    print("An error occured while running the shell-code")

            key_command = key_command.following_command
        elif key_command.command_type == 'hotkey':
            hotkey_function(key_command.hotkeys)
            key_command = key_command.following_command
        elif key_command.command_type == 'stopwatch':
            global stopwatch_threads
            if key_command.id not in stopwatch_threads:
                thread = threading.Thread(target=run_stopwatch, args=[
                    model_streamdeckKey])
                thread.start()
                stopwatch_threads[key_command.id] = thread
            else:
                thread = stopwatch_threads[key_command.id]
                del stopwatch_threads[key_command.id]
                thread.join()
            key_command = key_command.following_command

    # changes folder if this key is meant to
    if model_streamdeckKey.change_to_folder:
        change_to_folder(model_streamdeckKey.change_to_folder.id)


"""
run shell command every 'intervall' seconds and save result as text in key
"""


def run_shell_interval(model_streamdeckKey, interval):

    command = model_streamdeckKey.command
    while(True):
        try:
            process = subprocess.Popen(
                command.command_string.split(), stdout=subprocess.PIPE,
                cwd=command.active_directory)
        except:
            print("An error occured while running the shell-code")
        value = process.communicate()[0].decode("utf-8")
        model_streamdeckKey.text = value
        deck = decks[model_streamdeckKey.streamdeck.serial_number]
        update_key_image(deck, model_streamdeckKey, False)

        start_pause = datetime.now()
        while(command.id in interval_shell_threads
              and (datetime.now()-start_pause).seconds < interval):
            time.sleep(1)

        if command.id not in interval_shell_threads:
            break


"""
run_stopwatch
"""


def run_stopwatch(model_streamdeckKey):
    global decks
    deck = decks[model_streamdeckKey.streamdeck.serial_number]
    start = timer()
    command_id = model_streamdeckKey.command.id
    while (True):
        curtime = timer()
        model_streamdeckKey.text = str(timedelta(seconds=int(curtime - start)))
        update_key_image(deck, model_streamdeckKey, False)
        time.sleep(1)

        if command_id not in stopwatch_threads:
            break


"""
clock method for clock in format HH:MM
updates every minute
"""


def key_clock(deck, streamdeckkey):

    key_id = streamdeckkey.id
    while(True):
        current_time = datetime.now().strftime("%H:%M")
        streamdeckkey.text = current_time
        update_key_image(deck, streamdeckkey, True)

        # exit while loop if 60 seconds are over or the thread
        # for this clock needs to be stopped
        start_pause = datetime.now()
        while(key_id in clock_threads
              and (datetime.now()-start_pause).seconds < 60):
            time.sleep(1)

        if key_id not in clock_threads:
            break


"""
Presses given hotkeys on keyboard
"""


def hotkey_function(hotkeys):
    keys = [hotkeys.key1, hotkeys.key2,
            hotkeys.key3, hotkeys.key4, hotkeys.key5]
    parsedKeys = parse_keys(keys)
    keyboard = Controller()

    for key in parsedKeys:
        if key:
            keyboard.press(key)

    for key in reversed(parsedKeys):
        if key:
            keyboard.release(key)


def parse_keys(keys):
    parsedKeys = []
    key_dict = {
        "space": Key.space,
        "Enter": Key.enter,
        "Escape": Key.esc,
        "Shift": Key.shift,
        "Control": Key.ctrl,
        "Control_l": Key.ctrl_l,
        "Control_R": Key.ctrl_r,
        "Alt": Key.alt,
        "Alt_l": Key.alt_l,
        "Alt_r": Key.alt_r,
        "AltGraph": Key.alt_gr,
        "Backspace": Key.backspace,
        "CapsLock": Key.caps_lock,
        "Meta": Key.cmd,
        "Meta_l": Key.cmd_l,
        "Meta_r": Key.cmd_r,
        "Delete": Key.delete,
        "Insert": Key.insert,
        "Home": Key.home,
        "PageDown": Key.page_down,
        "PageUp": Key.page_up,
        "Pause": Key.pause,
        "PrintScreen": Key.print_screen,
        "ArrowDown": Key.down,
        "ArrowLeft": Key.left,
        "ArrowUp": Key.up,
        "ArrowRight": Key.right,
        "End": Key.end,
        "F1": Key.f1,
        "F2": Key.f2,
        "F3": Key.f3,
        "F4": Key.f4,
        "F5": Key.f5,
        "F6": Key.f6,
        "F7": Key.f7,
        "F8": Key.f8,
        "F9": Key.f9,
        "F10": Key.f10,
        "F11": Key.f11,
        "F12": Key.f12,
        "Next": Key.media_next,
        "Play/Pause": Key.media_play_pause,
        "Previous": Key.media_previous,
        "VolumeDown": Key.media_volume_down,
        "VolumeUp": Key.media_volume_up,
        "VolumeMute": Key.media_volume_mute,
    }

    for key in keys:
        if key in key_dict:
            parsedKeys.append(key_dict[key])
        else:
            parsedKeys.append(key)
    return parsedKeys


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
    global stop_animation
    stop_animation = True
    animated_images.clear()

    global clock_threads

    clock_thread_keys = list(clock_threads.keys())
    for dict_key in clock_thread_keys:
        clock_thread = clock_threads[dict_key]
        del clock_threads[dict_key]
        clock_thread.join()

    global stopwatch_threads

    stopwatch_threads_keys = list(stopwatch_threads.keys())
    for dict_key in stopwatch_threads_keys:
        stopwatch_thread = stopwatch_threads[dict_key]
        del stopwatch_threads[dict_key]
        stopwatch_thread.join()

    global interval_shell_threads

    interval_shell_keys = list(interval_shell_threads.keys())
    for dict_key in interval_shell_keys:
        shell_thread = interval_shell_threads[dict_key]
        del interval_shell_threads[dict_key]
        shell_thread.join()

    for key in keys:
        update_key_image(None, key, False)

    streamdeck_serialnumber = keys[0].streamdeck.serial_number

    deck = decks[streamdeck_serialnumber]
    stop_animation = False
    threading.Thread(target=animate, args=[
                     FRAMES_PER_SECOND, deck, animated_images]).start()

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

    global active_folder

    # don't update key image if the key is not currently
    # shown on the streamdeck
    if not active_folder == model_streamdeckkey.folder.name:
        return

    if not deck:
        deck = decks[model_streamdeckkey.streamdeck.serial_number]

    # handle keys with clock
    if model_streamdeckkey.clock and not state:
        if model_streamdeckkey.id not in clock_threads:
            thread = threading.Thread(target=key_clock, args=[
                                      deck, model_streamdeckkey])
            thread.start()
            clock_threads[model_streamdeckkey.id] = thread
        pass

    if not model_streamdeckkey.clock:
        if model_streamdeckkey.id in clock_threads:
            clock_threads[model_streamdeckkey.id].join()
            del clock_threads[model_streamdeckkey.id]

    key_style = get_key_style(model_streamdeckkey)

    # Generate the custom key with the requested image and label.
    if(not key_style["icon"]):
        key_style["icon"] = PILHelper.create_image(deck)
    image = render_key_image(
        deck, key_style["icon"], key_style["font"], key_style["label"],
        model_streamdeckkey.number)
    # Use a scoped-with on the deck to ensure we're the only thread using it
    # right now.
    if image:
        with deck:
            # Update requested key with the generated image.
            # (If its not animated)
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


def render_key_image(
        deck, icon_filename, font_filename, label_text, key_number):
    # Resize the source image asset to best-fit the dimensions of a single key,
    # leaving a margin at the bottom so that we can draw the key title
    # afterwards.
    blank_image_flag = False
    try:
        icon = Image.open(icon_filename)
    except AttributeError:
        blank_image_flag = True
        icon = icon_filename
    except UnidentifiedImageError:
        out = BytesIO()
        cairosvg.svg2png(url=icon_filename, write_to=out)
        icon = Image.open(out)

    if(not blank_image_flag and icon.is_animated):
        # create frames for animation
        frames = create_animation_frames(deck, icon)
        animated_images[key_number] = frames
        return None
    else:
        image = PILHelper.create_scaled_image(
            deck, icon, margins=[0, 0, 20, 0])
        # Load a custom TrueType font and use it to overlay the key index
        # draw key label onto the image a few pixels from the
        # bottom of the key.
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(font_filename, 14)
        draw.text((image.width / 2, image.height - 10), text=label_text,
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
Extracts out the individual animation frames of image (if
any) and returns an infinite generator that returns the next animation frame,
in the StreamDeck device's native image format.
"""


def create_animation_frames(deck, image):
    icon_frames = list()

    # Iterate through each animation frame of the source image
    for frame in ImageSequence.Iterator(image):
        # Create new key image of the correct dimensions, black background.
        frame_image = PILHelper.create_scaled_image(deck, frame)

        # Preconvert the generated image to the native format of the StreamDeck
        # so we don't need to keep converting it when showing it on the device.
        native_frame_image = PILHelper.to_native_format(deck, frame_image)

        # Store the rendered animation frame for later user.
        icon_frames.append(native_frame_image)

    # Return an infinite cycle generator that returns the next animation frame
    # each time it is called.
    return itertools.cycle(icon_frames)


"""
Helper unction that will run a periodic loop which updates the
images on each Key
"""


def animate(fps, deck, key_images):
    # Convert frames per second to frame time in seconds.
    #
    # Frame time often cannot be fully expressed by a float type,
    # meaning that we have to use fractions.
    frame_time = Fraction(1, fps)

    # Get a starting absolute time reference point.
    #
    # We need to use an absolute time clock, instead of relative sleeps
    # with a constant value, to avoid drifting.
    #
    # Drifting comes from an overhead of scheduling the sleep itself -
    # it takes some small amount of time for `time.sleep()` to execute.
    next_frame = Fraction(time.monotonic())

    # Periodic loop that will render every frame at the set FPS until
    # the StreamDeck device we're using is closed.
    while not stop_animation:
        try:
            # Use a scoped-with on the deck to ensure we're the only
            # thread using it right now.
            with deck:
                # Update the key images with the next animation frame.
                try:
                    for key, frames in key_images.items():
                        deck.set_key_image(key, next(frames))
                except RuntimeError:
                    break
        except TransportError as err:
            print("TransportError: {0}".format(err))
            # Something went wrong while communicating with the device
            # (closed?) - don't re-schedule the next animation frame.
            break

        # Set the next frame absolute time reference point.
        #
        # We are running at the fixed `fps`, so this is as simple as
        # adding the frame time we calculated earlier.
        next_frame += frame_time

        # Knowing the start of the next frame we can calculate how long
        # we have to sleep until its start.
        sleep_interval = float(next_frame) - time.monotonic()

        # Schedule the next periodic frame update.
        #
        # `sleep_interval` can be a negative number when current FPS
        # setting is too high for the combination of host and
        # StreamDeck to handle. If this is the case, we skip sleeping
        # immediately render the next frame to try to catch up.
        if sleep_interval >= 0:
            time.sleep(sleep_interval)


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

    global animated_images
    # Kick off the key image animating thread
    threading.Thread(target=animate, args=[
                     FRAMES_PER_SECOND, deck, animated_images]).start()
    deck.set_key_callback(key_change_callback)
