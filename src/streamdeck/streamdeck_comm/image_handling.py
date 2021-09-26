import os
import threading
import cairosvg
import itertools
import time
import base64

from pathlib import Path
from datetime import datetime
from io import BytesIO
from fractions import Fraction
from PIL import (Image, ImageSequence, ImageDraw,
                 ImageFont, UnidentifiedImageError)
from StreamDeck.ImageHelpers import PILHelper
from StreamDeck.Transport.Transport import TransportError
from streamdeck.models import (StreamdeckKey, Folder)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ASSETS_PATH = os.path.join(BASE_DIR, "assets")
MEDIA_PATH = os.path.join(BASE_DIR, "media")

FRAMES_PER_SECOND = 10

animated_images = {}
clock_threads = {}
stop_animation = {}


def get_key_style(model_streamdeckKey):
    """
    Returns everything needed to add a streamdeckkey_model as actual key to the streamdeck

    :param model_streamdeckKey: stream deck key
    :returns: all stream deck key text information
    """

    if not model_streamdeckKey.image_source:
        icon = None
    else:
        icon = os.path.join(MEDIA_PATH, model_streamdeckKey.image_source.name)

    if model_streamdeckKey.font:
        font = os.path.join(ASSETS_PATH, model_streamdeckKey.font)
    else:
        font = "arial.ttf"

    return {
        "name": model_streamdeckKey.number,
        "icon": icon,
        "font": font,
        "text_size": model_streamdeckKey.text_size,
        "text_color": model_streamdeckKey.text_color,
        "text_position": model_streamdeckKey.text_position,
        "label": model_streamdeckKey.text,
        "underlined": model_streamdeckKey.text_underlined
    }


def update_key_image(deck, model_streamdeckKey, clock):
    """
    Creates a new key image based on the key index, style and
    current key state and updates the image on the StreamDeck.

    :param deck: active stream deck
    :param model_streamdeckKey: stream deck key
    :param clock: if false, remove clock from stream deck key
    :param text_color: color of displayed text in stream deck key
    """

    # handle keys with clock
    if model_streamdeckKey.clock and not clock:
        # the clock thread needs to be restarted or else text style changes will not
        # be recognized by the clock thread
        delete_clock_thread(model_streamdeckKey)
        add_clock_thread(deck, model_streamdeckKey)

    if not model_streamdeckKey.clock:
        delete_clock_thread(model_streamdeckKey)

    # Generate the custom key with the requested image and label.
    image = render_key_image(deck, model_streamdeckKey)
    # Use a scoped-with on the deck to ensure we're the only thread using it
    # right now.
    if image:
        with deck:
            # Update requested key with the generated image.
            # (If its not animated)
            deck.set_key_image(model_streamdeckKey.number, image)


def add_clock_thread(deck, model_streamdeckKey):
    """
    Adds clock thread to global dict clock_threads and starts it

    :param deck: active stream deck
    :param model_streamdeckKey: stream deck key
    """
    if model_streamdeckKey.id not in clock_threads:
        thread = threading.Thread(target=key_clock, args=[
                                  deck, model_streamdeckKey])
        thread.start()
        clock_threads[model_streamdeckKey.id] = thread
    pass


def delete_clock_thread(model_streamdeckKey):
    """
    Remove clock thread from global dict clock_threads

    :param model_streamdeckKey: stream deck key
    """
    if model_streamdeckKey.id in clock_threads:
        thread = clock_threads[model_streamdeckKey.id]
        del clock_threads[model_streamdeckKey.id]
        thread.join()

    pass


def key_clock(deck, model_streamdeckKey):
    """
    Run clock in format HH:MM on key

    :param deck: active stream deck
    :param model_streamdeckKey: stream deck key
    """
    key_id = model_streamdeckKey.id
    while(True):
        current_time = datetime.now().strftime("%H:%M")
        model_streamdeckKey.text = current_time
        update_key_image(deck, model_streamdeckKey, True)

        # exit while loop when the minute switches
        while(key_id in clock_threads
              and datetime.now().strftime("%H:%M") == current_time):
            time.sleep(1)

        if key_id not in clock_threads:
            break


def render_key_image(deck, model_streamdeckKey, image_object=False):
    """
    Generates a custom tile with run-time generated text and custom image via the
    PIL module. Adapted from stream deck library examples

    :param deck: active stream deck
    :param model_streamdeckKey: stream deck key
    :param image_object: if true method returns Image object instead of memoryview

    :rtype: memoryview
    :returns: rendered image for the stream deck key
    """

    # Resize the source image asset to best-fit the dimensions of a single key,
    # leaving a margin at the bottom so that we can draw the key title
    # afterwards.
    blank_image_flag = False

    key_style = get_key_style(model_streamdeckKey)

    # Generate the custom key with the requested image and label.
    if(not key_style["icon"]):
        key_style["icon"] = PILHelper.create_image(deck)

    try:
        icon = Image.open(key_style["icon"])
    except AttributeError:
        blank_image_flag = True
        icon = key_style["icon"]
    except UnidentifiedImageError:
        # should only occur for svgs
        out = BytesIO()
        cairosvg.svg2png(url=key_style["icon"], write_to=out)
        icon = Image.open(out)

    if(not blank_image_flag and getattr(icon, "is_animated", False)):
        frames = create_animation_frames(deck, icon, key_style)
        animated_images[key_style["name"]] = frames
        return None
    else:
        global stop_animation
        if key_style["name"] in animated_images:
            stop_animation[key_style["name"]] = True
            time.sleep(.5)
            del stop_animation[key_style["name"]]
            del animated_images[key_style["name"]]
        image = PILHelper.create_scaled_image(
            deck, icon, margins=[0, 0, 0, 0])
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(key_style["font"], key_style["text_size"])

        text_positions = {
            "bottom": (image.width / 2, image.height - 10),
            "center": (image.width / 2, image.height - 30),
            # fontsize/5 is used as padding as otherwise the text will not be fully shown
            "top": (image.width / 2, image.height - 60 + key_style["text_size"]/5)
        }

        draw.text(text_positions[key_style["text_position"]], text=key_style["label"],
                  font=font, anchor="ms", fill=key_style["text_color"])

        if key_style["underlined"]:
            width = draw.textsize(key_style["label"], font=font)[0]
            lx, ly = text_positions[key_style["text_position"]]
            ly = ly + 5
            draw.line((lx - width/2, ly, lx + width/2, ly), fill=key_style["text_color"])

        if image_object:
            # this is used to display the image in a browser
            buf = BytesIO()
            image.save(buf, format='JPEG')
            img_str = base64.b64encode(buf.getvalue())
            return img_str
        else:
            return PILHelper.to_native_format(deck, image)


def create_animation_frames(deck, image, key_style):
    """
    TAKEN AND MODIFIED FROM STREAM DECK LIBRARY EXAMPLES by Dean Camera
    Extracts out the individual animation frames of image (if
    any) and returns an infinite generator that returns the next animation frame,
    in the StreamDeck device's native image format.

    :param deck: active stream deck
    :param image: image which needs to be animated
    :param label_text: text of stream deck key
    :param font_filename: filename of font file
    :returns Return an infinite cycle generator that returns the next animation frame each time it is called.
    """

    icon_frames = list()
    # Iterate through each animation frame of the source image
    for frame in ImageSequence.Iterator(image):
        # Create new key image of the correct dimensions, black background.
        frame_image = PILHelper.create_scaled_image(deck, frame)

        draw = ImageDraw.Draw(frame_image)
        font = ImageFont.truetype(key_style["font"], key_style["text_size"])

        text_positions = {
            "bottom": (frame_image.width / 2, frame_image.height - 10),
            "center": (frame_image.width / 2, frame_image.height - 30),
            # fontsize/5 is used as padding as otherwise the text will not be fully shown
            "top": (frame_image.width / 2, frame_image.height - 60 + key_style["text_size"]/5)
        }

        draw.text(text_positions[key_style["text_position"]], text=key_style["label"],
                  font=font, anchor="ms", fill=key_style["text_color"])

        if key_style["underlined"]:
            width = draw.textsize(key_style["label"], font=font)[0]
            lx, ly = text_positions[key_style["text_position"]]
            ly = ly + 5
            draw.line((lx - width/2, ly, lx + width/2, ly), fill=key_style["text_color"])

        # Preconvert the generated image to the native format of the StreamDeck
        # so we don't need to keep converting it when showing it on the device.
        native_frame_image = PILHelper.to_native_format(deck, frame_image)

        # Store the rendered animation frame for later user.
        icon_frames.append(native_frame_image)

    # Return an infinite cycle generator that returns the next animation frame
    # each time it is called.
    return itertools.cycle(icon_frames)


def animate(fps, deck, key_images, key_number):
    """
    TAKEN AND MODIFIED FROM STREAM DECK LIBRARY EXAMPLES by Dean Camera
    Helper function that will run a periodic loop which updates the
    images on each Key

    :param fps: fps of animated image
    :param deck: active stream deck
    :param key_images: images of key which will be looped
    """

    # Convert frames per second to frame time in seconds.
    #
    # Frame time often cannot be fully expressed by a float type,
    # meaning that we have to use fractions.
    frame_time = Fraction(1, fps)

    # Get a starting absolute time reference point.
    # We need to use an absolute time clock, instead of relative sleeps
    # with a constant value, to avoid drifting.
    # Drifting comes from an overhead of scheduling the sleep itself -
    # it takes some small amount of time for `time.sleep()` to execute.
    next_frame = Fraction(time.monotonic())

    # Periodic loop that will render every frame at the set FPS until
    # the StreamDeck device we're using is closed.
    while not stop_animation[key_number]:
        try:
            # Use a scoped-with on the deck to ensure we're the only
            # thread using it right now.
            with deck:
                # Update the key images with the next animation frame.
                try:
                    deck.set_key_image(key_number, next(key_images[key_number]))
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


def start_animated_images(deck, folder_id):
    """
    Start threads of animated image in current folder

    :param deck: active stream deck
    :param folder_id: id of folder
    """
    global animated_images
    global stop_animation

    folder = Folder.objects.get(id=folder_id)
    list_key = list(
        StreamdeckKey.objects.filter(folder=folder))

    for key in list_key:
        if key.number in animated_images:
            stop_animation[key.number] = False
            threading.Thread(target=animate, args=[
                FRAMES_PER_SECOND, deck, animated_images, key.number]).start()


def create_full_deck_sized_image(deck, key_spacing, image_filename):
    """
    TAKEN FROM STREAM DECK LIBRARY EXAMPLES by Dean Camera
    Generates an image that is correctly sized to fit across all keys of
    a given Stream Deck

    :param deck: active stream deck
    :param key_spacing: space between stream deck keys
    :param image_filename: filename of image

    :rtype PIL Image object
    :returns deck sized image
    """
    key_rows, key_cols = deck.key_layout()
    key_width, key_height = deck.key_image_format()['size']
    spacing_x, spacing_y = key_spacing

    # Compute total size of the full StreamDeck image, based on the number of
    # buttons along each axis. This doesn't take into account the spaces between
    # the buttons that are hidden by the bezel.
    key_width *= key_cols
    key_height *= key_rows

    # Compute the total number of extra non-visible pixels that are obscured by
    # the bezel of the StreamDeck.
    spacing_x *= key_cols - 1
    spacing_y *= key_rows - 1

    # Compute final full deck image size, based on the number of buttons and
    # obscured pixels.
    full_deck_image_size = (key_width + spacing_x, key_height + spacing_y)

    # Resize the image to suit the StreamDeck's full image size (note: will not
    # preserve the correct aspect ratio).
    image = Image.open(os.path.join(MEDIA_PATH, image_filename)).convert("RGBA")
    return image.resize(full_deck_image_size, Image.LANCZOS)


def crop_key_image_from_deck_sized_image(deck, image, key_spacing, key):
    """
    TAKEN FROM STREAM DECK LIBRARY EXAMPLES by Dean Camera
    Crops out a key-sized image from a larger deck-sized image, at the location
    occupied by the given key index.

    :param deck: active stream deck
    :param image: deck sized image
    :param key_spacing: space between stream deck keys
    :param key: key index
    :returns key-sized PIL image for the key
    """
    key_rows, key_cols = deck.key_layout()
    key_width, key_height = deck.key_image_format()['size']
    spacing_x, spacing_y = key_spacing

    # Determine which row and column the requested key is located on.
    row = key // key_cols
    col = key % key_cols

    # Compute the starting X and Y offsets into the full size image that the
    # requested key should display.
    start_x = col * (key_width + spacing_x)
    start_y = row * (key_height + spacing_y)

    # Compute the region of the larger deck image that is occupied by the given
    # key, and crop out that segment of the full image.
    region = (start_x, start_y, start_x + key_width, start_y + key_height)
    segment = image.crop(region)

    # Create a new key-sized image, and paste in the cropped section of the
    # larger image.
    key_image = PILHelper.create_image(deck)
    key_image.paste(segment)

    return PILHelper.to_native_format(deck, key_image)


def clear_image_threads():
    """
    Stops all running threads and clears all thread dictionaries
    """
    global stop_animation

    stop_animation = stop_animation.fromkeys(stop_animation, True)
    animated_images.clear()

    global clock_threads

    clock_thread_keys = list(clock_threads.keys())
    for dict_key in clock_thread_keys:
        clock_thread = clock_threads[dict_key]
        del clock_threads[dict_key]
        clock_thread.join()
