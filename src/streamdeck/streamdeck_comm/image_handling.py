import os
import threading
import cairosvg
import itertools
import time

from pathlib import Path
from datetime import datetime
from io import BytesIO
from fractions import Fraction
from PIL import (Image, ImageSequence, ImageDraw,
                 ImageFont, UnidentifiedImageError)
from StreamDeck.ImageHelpers import PILHelper
from StreamDeck.Transport.Transport import TransportError

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ASSETS_PATH = os.path.join(BASE_DIR, "assets")
MEDIA_PATH = os.path.join(BASE_DIR, "media")

FRAMES_PER_SECOND = 10

animated_images = {}
clock_threads = {}
stop_animation = False


def get_key_style(model_streamdeckKey):
    """
    Returns everything needed to add a streamdeckkey_model as actual key to the streamdeck

    :param model_streamdeckKey: stream deck key
    :returns: name, icon, font and label of a stream deck key as dictionary
    """

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


def update_key_image(deck, model_streamdeckKey, clock, text_color="white"):
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
        add_clock_thread(deck, model_streamdeckKey)

    if not model_streamdeckKey.clock:
        delete_clock_thread(model_streamdeckKey)

    key_style = get_key_style(model_streamdeckKey)

    # Generate the custom key with the requested image and label.
    if(not key_style["icon"]):
        key_style["icon"] = PILHelper.create_image(deck)
    image = render_key_image(
        deck, key_style["icon"], key_style["font"], key_style["label"],
        model_streamdeckKey.number, text_color)
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
        clock_threads[model_streamdeckKey.id].join()
        del clock_threads[model_streamdeckKey.id]
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


def render_key_image(
        deck, icon_filename, font_filename, label_text,
        key_number, text_color='white'):
    """
    Generates a custom tile with run-time generated text and custom image via the
    PIL module. Adapted from stream deck library examples

    :param deck: active stream deck
    :param icon_filename: filename of image or actual image
    :param font_filename: filename of font file
    :param label_text: text of stream deck key
    :param key_number: number of stream deck key on actual stream deck
    :param text_color: color of text on stream deck key
    """

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
        # should only occur for svgs
        out = BytesIO()
        cairosvg.svg2png(url=icon_filename, write_to=out)
        icon = Image.open(out)

    if(not blank_image_flag and getattr(icon, "is_animated", False)):
        # create frames for animation
        frames = create_animation_frames(deck, icon, label_text, font_filename)
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
                  font=font, anchor="ms", fill=text_color)

        return PILHelper.to_native_format(deck, image)


def create_animation_frames(deck, image, label_text, font_filename):
    """
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
        font = ImageFont.truetype(font_filename, 14)
        draw.text((frame_image.width / 2, frame_image.height - 10),
                  text=label_text, font=font, anchor="ms", fill='white')
        # Preconvert the generated image to the native format of the StreamDeck
        # so we don't need to keep converting it when showing it on the device.
        native_frame_image = PILHelper.to_native_format(deck, frame_image)

        # Store the rendered animation frame for later user.
        icon_frames.append(native_frame_image)

    # Return an infinite cycle generator that returns the next animation frame
    # each time it is called.
    return itertools.cycle(icon_frames)


def animate(fps, deck, key_images):
    """
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


def start_animated_images(deck):
    """
    Start threads of animated image

    :param deck: active stream deck
    """
    global animated_images
    global stop_animation
    stop_animation = False
    threading.Thread(target=animate, args=[
                     FRAMES_PER_SECOND, deck, animated_images]).start()


def clear_image_threads():
    """
    Stops all running threads and clears all thread dictionaries
    """
    global stop_animation
    stop_animation = True
    animated_images.clear()

    global clock_threads

    clock_thread_keys = list(clock_threads.keys())
    for dict_key in clock_thread_keys:
        clock_thread = clock_threads[dict_key]
        del clock_threads[dict_key]
        clock_thread.join()
