from .models import StreamdeckKey, Command, Folder, Streamdeck, StreamdeckModel
from rest_framework import serializers


class StreamdeckKeySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = StreamdeckKey
        fields = ['url', 'id', 'number', 'text', 'image_source',
                  'folder', 'streamdeck', 'command', 'change_to_folder']


class CommandSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Command
        fields = ['url', 'id', 'name', 'command_string',
                  'value', 'following_command']


class FolderSerializer(serializers.HyperlinkedModelSerializer):

    keys = StreamdeckKeySerializer(many=True, read_only=True)
    change_keys = StreamdeckKeySerializer(many=True, read_only=True)

    class Meta:
        model = Folder
        fields = ['url', 'id', 'name', 'keys', 'change_keys']


class StreamdeckSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Streamdeck
        fields = ['url', 'id', 'name', 'serial_number',
                  'brightness', 'streamdeck_model']


class StreamdeckModelSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = StreamdeckModel
        fields = ['url', 'id', 'name', 'key_count', 'keys_per_row']
