from django.db import models
import os


def get_image_path(instance, filename):
    return os.path.join('images', str(instance.id), filename)


class StreamdeckKey(models.Model):
    number = models.IntegerField()
    text = models.CharField(blank=True, max_length=50)
    image_source = models.ImageField(
        upload_to=get_image_path, blank=True, null=True)
    folder = models.ForeignKey(
        'Folder', related_name='keys', on_delete=models.CASCADE)
    streamdeck = models.ForeignKey('Streamdeck', on_delete=models.CASCADE)
    command = models.ForeignKey(
        'Command', blank=True, null=True, on_delete=models.SET_NULL)
    change_to_folder = models.ForeignKey(
        'Folder', blank=True, null=True, related_name='change_keys',
        on_delete=models.SET_NULL)


class Command(models.Model):
    name = models.CharField(max_length=100, default='Command')
    command_string = models.TextField()
    value = models.IntegerField(blank=True, null=True)
    following_command = models.ForeignKey(
        'self', blank=True, null=True, on_delete=models.SET_NULL)


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
