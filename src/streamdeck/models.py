from django.db import models
import os


def get_image_path(instance, filename):
    return os.path.join('images', str(instance.id), filename)


class StreamdeckKey(models.Model):
    number = models.IntegerField()
    text = models.CharField(blank=True, max_length=10)
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
    interval_time = models.IntegerField(blank=True, null=True, default=-1)
    hotkeys = models.ForeignKey(
        'Hotkeys', blank=True, null=True, on_delete=models.SET_NULL)
    following_command = models.ForeignKey(
        'self', blank=True, null=True, on_delete=models.SET_NULL)

    COMMAND_CHOICES = (
        ("shell", "shell"),
        ("hotkey", "hotkey"),
        ("stopwatch", "stopwatch")
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
