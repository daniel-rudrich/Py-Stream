from django.db import models
import os


def get_image_path(instance, filename):
    return os.path.join('images', str(instance.id), filename)


def get_image_path_streamdeck(instance, filename):
    return os.path.join('images/streamdeck', str(instance.id), filename)


class StreamdeckKey(models.Model):

    POSITION_CHOICES = (
        ("center", "center"),
        ("top", "top"),
        ("bottom", "bottom")
    )

    number = models.IntegerField()
    text = models.CharField(blank=True, max_length=10)
    font = models.CharField(blank=True, max_length=30)
    text_size = models.IntegerField(default=14)
    text_position = models.CharField(choices=POSITION_CHOICES, default="bottom", max_length=6)
    text_color = models.CharField(default="#FFFFFF", max_length=20)
    text_bold = models.BooleanField(default=False)
    text_italic = models.BooleanField(default=False)
    text_underlined = models.BooleanField(default=False)
    image_source = models.FileField(
        upload_to=get_image_path, blank=True, null=True)
    folder = models.ForeignKey(
        'Folder', related_name='keys', on_delete=models.CASCADE)
    streamdeck = models.ForeignKey('Streamdeck', on_delete=models.CASCADE)
    command = models.ForeignKey(
        'Command', blank=True, null=True, on_delete=models.SET_NULL)
    change_to_folder = models.ForeignKey(
        'Folder', blank=True, null=True, related_name='change_keys',
        on_delete=models.SET_NULL)
    clock = models.BooleanField(default=False)


class Command(models.Model):
    name = models.CharField(max_length=100, default='Command')
    command_string = models.TextField(blank=True, null=True)
    active_directory = models.TextField(default='.')
    time_value = models.IntegerField(blank=True, null=True, default=0)
    hotkeys = models.ForeignKey(
        'Hotkeys', blank=True, null=True, on_delete=models.SET_NULL)
    following_command = models.ForeignKey(
        'self', blank=True, null=True, on_delete=models.SET_NULL)

    COMMAND_CHOICES = (
        ("shell", "shell"),
        ("hotkey", "hotkey"),
        ("stopwatch", "stopwatch"),
        ("timer", "timer")
    )

    command_type = models.CharField(max_length=9,
                                    choices=COMMAND_CHOICES,
                                    default="shell")


class Hotkeys(models.Model):
    key1 = models.CharField(max_length=10, blank=True, null=True)
    key2 = models.CharField(max_length=10, blank=True, null=True)
    key3 = models.CharField(max_length=10, blank=True, null=True)
    key4 = models.CharField(max_length=10, blank=True, null=True)
    key5 = models.CharField(max_length=10, blank=True, null=True)


class Folder(models.Model):
    name = models.CharField(max_length=100)


class StreamdeckModel(models.Model):
    name = models.CharField(max_length=100)
    key_count = models.IntegerField()
    keys_per_row = models.IntegerField()


class Streamdeck(models.Model):
    name = models.CharField(max_length=100, blank=True)
    serial_number = models.CharField(max_length=50)
    brightness = models.IntegerField(default=30)
    streamdeck_model = models.ForeignKey(
        'StreamdeckModel', on_delete=models.CASCADE)
    default_folder = models.ForeignKey(
        'Folder', on_delete=models.CASCADE, null=True)
    full_deck_image = models.FileField(
        upload_to=get_image_path_streamdeck, blank=True, null=True)
