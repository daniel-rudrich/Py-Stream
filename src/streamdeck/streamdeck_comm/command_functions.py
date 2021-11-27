import time
import threading
import platform
import subprocess
import shlex

from datetime import datetime, timedelta
from timeit import default_timer as timer
from .image_handling import update_key_image

# keys of thread dictionary are all of the form key: (commandId, serial_number)
interval_shell_threads = {}
timer_threads = {}
stopwatch_threads = {}


def run_key_command(deck, model_streamdeckKey):
    """
    Runs commands that are attached to a stream deck key

    :param deck: the active stream deck
    :param model_streamdeckKey: stream deck key which commands shall be run
    """
    key_command = model_streamdeckKey.command
    while key_command:
        if key_command.command_type == 'shell':
            handle_shell_command(deck, model_streamdeckKey)
        elif key_command.command_type == 'hotkey':
            # hotkeys cannot be executed on a raspberrypi without display
            if platform.uname() != "raspberrypi":
                hotkey_function(key_command.hotkeys)
        elif key_command.command_type == 'stopwatch':
            handle_stopwatch_command(deck, model_streamdeckKey)
        elif key_command.command_type == 'timer':
            handle_timer_command(deck, model_streamdeckKey)
        elif key_command.command_type == 'write':
            if platform.uname() != "raspberrypi":
                write_command_function(model_streamdeckKey)
        key_command = key_command.following_command


def handle_shell_command(deck, model_streamdeckKey):
    """
    Handles threading of shell commands

    :param deck: active stream deck
    :param model_streamdeckKey: stream deck key with shell command
    """
    key_command = model_streamdeckKey.command
    serial_number = model_streamdeckKey.streamdeck.serial_number
    if key_command.time_value > 0:
        global interval_shell_threads
        if key_command.id not in interval_shell_threads:
            thread = threading.Thread(target=run_shell_interval,
                                      args=[deck,
                                            model_streamdeckKey,
                                            key_command.time_value])
            interval_shell_threads[(key_command.id, serial_number)] = thread
            thread.start()
        else:
            thread = interval_shell_threads[(key_command.id, serial_number)]
            del interval_shell_threads[(key_command.id, serial_number)]
            thread.join()
    else:
        try:
            process = subprocess.Popen(
                shlex.split(key_command.command_string),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                cwd=key_command.active_directory)
            print(process.communicate()[0].decode("utf-8"))
        except Exception as e:
            print("Error: %s" % str(e))


def handle_stopwatch_command(deck, model_streamdeckKey):
    """
    Handles threading of stopwatch command

    :param deck: active stream deck
    :param model_streamdeckKey: stream deck key with stopwatch command
    """
    global stopwatch_threads

    key_command = model_streamdeckKey.command
    serial_number = model_streamdeckKey.streamdeck.serial_number

    if (key_command.id, serial_number) not in stopwatch_threads:
        thread = threading.Thread(target=run_stopwatch, args=[
            deck, model_streamdeckKey])
        thread.start()
        stopwatch_threads[(key_command.id, serial_number)] = thread
    else:
        thread = stopwatch_threads[(key_command.id, serial_number)]
        del stopwatch_threads[(key_command.id, serial_number)]
        thread.join()


def handle_timer_command(deck, model_streamdeckKey):
    """
    Handles threading of timer command

    :param deck: active stream deck
    :param model_streamdeckKey: stream deck key with timer command
    """
    global timer_threads

    key_command = model_streamdeckKey.command
    serial_number = model_streamdeckKey.streamdeck.serial_number

    if (key_command.id, serial_number) not in timer_threads:
        thread = threading.Thread(target=run_timer,
                                  args=[deck,
                                        model_streamdeckKey,
                                        key_command.time_value
                                        ])
        thread.start()
        timer_threads[(key_command.id, serial_number)] = thread
    else:
        thread = timer_threads[(key_command.id, serial_number)]
        del timer_threads[(key_command.id, serial_number)]
        thread.join()


def write_command_function(model_streamdeckKey):
    """
    Writes text of command where the current cursor is positioned

    :param model_streamdeckKey: stream deck key with write command
    """

    command = model_streamdeckKey.command
    text = command.command_string

    from pynput.keyboard import Controller
    keyboard = Controller()
    keyboard.type(text)


def run_shell_interval(deck, model_streamdeckKey, interval):
    """
    Run shell command every 'interval' seconds and save result as text in key

    :param deck: active stream deck
    :param model_streamdeckKey: stream deck key with shell intervall command
    :param interval: time between each shell command execution
    """
    command = model_streamdeckKey.command
    old_text = model_streamdeckKey.text
    serial_number = model_streamdeckKey.streamdeck.serial_number
    while(True):
        try:
            process = subprocess.Popen(
                shlex.split(command.command_string), stdout=subprocess.PIPE,
                shell=True,
                cwd=command.active_directory)
        except Exception as e:
            print("Error: %s" % str(e))
            break
        value = process.communicate()[0].decode("utf-8")
        model_streamdeckKey.text = value
        update_key_image(deck, model_streamdeckKey, False)

        start_pause = datetime.now()
        while((command.id, serial_number) in interval_shell_threads
              and (datetime.now()-start_pause).seconds < interval):
            time.sleep(1)

        if (command.id, serial_number) not in interval_shell_threads:
            model_streamdeckKey.text = old_text
            update_key_image(deck, model_streamdeckKey, False)
            break


def run_stopwatch(deck, model_streamdeckKey):
    """
    Runs stopwatch on streamdeck key counting up seconds

    :param deck: active stream deck
    :param model_streamdeckKey: stream deck key with stopwatch command
    """
    start = timer()
    command_id = model_streamdeckKey.command.id
    serial_number = model_streamdeckKey.streamdeck.serial_number
    while (True):
        curtime = timer()
        model_streamdeckKey.text = str(timedelta(seconds=int(curtime - start)))
        update_key_image(deck, model_streamdeckKey, False)
        time.sleep(1)

        if (command_id, serial_number) not in stopwatch_threads:
            break


def run_timer(deck, model_streamdeckKey, timer_time):
    """
    Runs timer counting down from specified time

    :param deck: active stream deck
    :param model_streamdeckKey: stream deck key with time command
    :param timer_time: start time
    """
    curtime = timer_time
    command_id = model_streamdeckKey.command.id
    serial_number = model_streamdeckKey.streamdeck.serial_number

    while (curtime >= 0):
        model_streamdeckKey.text = str(timedelta(seconds=int(curtime)))
        update_key_image(deck, model_streamdeckKey, False)
        curtime = curtime - 1
        time.sleep(1)

        if (command_id, serial_number) not in timer_threads:
            break
    switch = 1
    old_color = model_streamdeckKey.text_color
    while (True):
        if switch == 1:
            color = '#FFFFFF'
            switch = 0
        else:
            color = '#FF0000'
            switch = 1
        model_streamdeckKey.text_color = color
        update_key_image(deck, model_streamdeckKey, False)
        time.sleep(1)
        if (command_id, serial_number) not in timer_threads:
            model_streamdeckKey.text_color = old_color
            break


def hotkey_function(hotkeys):
    """
    Presses given hotkeys on keyboard

    :param hotkeys: hotkeys to press
    """
    from pynput.keyboard import Controller
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
    """
    Parse javascript key texts to pynput keycodes

    :param keys: keys coming as javascript key texts
    :returns: list of pynput keys
    """
    from pynput.keyboard import Key
    parsedKeys = []
    key_dict = {
        "space": Key.space,
        "Enter": Key.enter,
        "Escape": Key.esc,
        "Shift": Key.shift,
        "Control": Key.ctrl,
        "Control_l": Key.ctrl_l,
        "Control_R": Key.ctrl_r,
        "Shift_l": Key.shift,
        "Shift_R": Key.shift,
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


def check_for_active_command(serial_number):
    """
    Checks wether there is an active command thread or not

    :param serial_number: serial number of active stream deck
    :returns: bool
    """

    for int_thread_key in interval_shell_threads.keys():
        if int_thread_key[1] == serial_number:
            if interval_shell_threads[int_thread_key].is_alive():
                return True

    for timer_thread_key in timer_threads.keys():
        if timer_thread_key[1] == serial_number:
            if timer_threads[timer_thread_key].is_alive():
                return True

    for stopwatch_thread_key in stopwatch_threads.keys():
        if stopwatch_thread_key[1] == serial_number:
            if stopwatch_threads[stopwatch_thread_key].is_alive():
                return True

    return False


def clear_command_threads(serial_number):
    """
    Stops all running threads and clears all thread dictionaries

    :param serial_number: serial number of active stream deck
    """
    global stopwatch_threads

    stopwatch_threads_keys = list(stopwatch_threads.keys())
    for dict_key in stopwatch_threads_keys:
        if dict_key[1] == serial_number:
            stopwatch_thread = stopwatch_threads[dict_key]
            del stopwatch_threads[dict_key]
            stopwatch_thread.join()

    global interval_shell_threads

    interval_shell_keys = list(interval_shell_threads.keys())
    for dict_key in interval_shell_keys:
        if dict_key[1] == serial_number:
            shell_thread = interval_shell_threads[dict_key]
            del interval_shell_threads[dict_key]
            shell_thread.join()

    global timer_threads

    timer_thread_keys = list(timer_threads.keys())
    for dict_key in timer_thread_keys:
        if dict_key[1] == serial_number:
            timer_thread = timer_threads[dict_key]
            del timer_threads[dict_key]
            timer_thread.join()
