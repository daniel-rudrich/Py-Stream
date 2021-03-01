from .models import StreamdeckKey, Command, Folder, Streamdeck, StreamdeckModel, Hotkeys
from rest_framework import serializers
from .svgimagefield import SVGAndImageFormField
from rest_framework.fields import ImageField


class StreamdeckKeySerializer(serializers.ModelSerializer):
    streamdeck = serializers.PrimaryKeyRelatedField(read_only=True)
    Commands = serializers.SerializerMethodField()

    class Meta:
        model = StreamdeckKey
        fields = ['id', 'number', 'text', 'image_source',
                  'folder', 'streamdeck', 'Commands', 'change_to_folder']
        depth = 5

    def get_Commands(self, obj):
        commands_list = []
        command = obj.command
        while command:
            commands_list.append(CommandSerializer(command).data)
            command = command.following_command
        return commands_list


class StreamdeckKeyImageSerializer(serializers.ModelSerializer):
    image_source = ImageField(
        required=False, _DjangoImageField=SVGAndImageFormField)

    class Meta:
        model = StreamdeckKey
        fields = ['image_source']


class CommandSerializer(serializers.ModelSerializer):
    following_command = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Command
        fields = ['id', 'name', 'command_string',
                  'hotkeys', 'following_command', 'active_directory',
                  'command_type']
        depth = 5


class HotkeysSerializer(serializers.ModelSerializer):

    class Meta:
        model = Hotkeys
        fields = ['key1', 'key2', 'key3', 'key4', 'key5']


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
