from .models import StreamdeckKey, Command, Folder, Streamdeck, StreamdeckModel
from rest_framework import serializers


class StreamdeckKeySerializer(serializers.ModelSerializer):
    streamdeck = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = StreamdeckKey
        fields = ['id', 'number', 'text', 'image_source',
                  'folder', 'streamdeck', 'command', 'change_to_folder']
        depth = 5


class CommandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Command
        fields = ['id', 'name', 'command_string',
                  'value', 'following_command']
        depth = 5


class FolderSerializer(serializers.ModelSerializer):

    keys = StreamdeckKeySerializer(many=True, read_only=True)

    class Meta:
        model = Folder
        fields = ['id', 'name', 'keys']
        depth = 1


class StreamdeckSerializer(serializers.ModelSerializer):

    class Meta:
        model = Streamdeck
        fields = ['id', 'name', 'serial_number',
                  'brightness', 'streamdeck_model', 'default_folder']
        depth = 1


class StreamdeckModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = StreamdeckModel
        fields = ['id', 'name', 'key_count', 'keys_per_row']
