from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser

from .serializers import (
    StreamdeckKeySerializer, FolderSerializer,
    StreamdeckSerializer, CommandSerializer,
    StreamdeckKeyImageSerializer, HotkeysSerializer)
from .models import Streamdeck, StreamdeckKey, Folder, Command, Hotkeys
from .streamdeck_comm.streamdeck_interface import (change_folder,
                                                   delete_folders,
                                                   update_key_behavior,
                                                   update_key_display,
                                                   update_brightness,
                                                   check_connection)


@csrf_exempt
def streamdeck_list(request):
    if request.method == 'GET':
        streamdecks = Streamdeck.objects.all()
        serializer = StreamdeckSerializer(streamdecks, many=True)
        return JsonResponse(serializer.data, safe=False)


@csrf_exempt
def streamdeck_detail(request, id):
    try:
        streamdeck = Streamdeck.objects.get(id=id)
    except Streamdeck.DoesNotExist:
        return HttpResponse(f"Stream deck with id {id} not found", status=404)

    if request.method == 'GET':
        serializer = StreamdeckSerializer(streamdeck)
        return JsonResponse(serializer.data)

    if request.method == 'PATCH':
        data = JSONParser().parse(request)

        streamdeck.name = data.get("name", streamdeck.name)
        streamdeck.brightness = data.get("brightness", streamdeck.brightness)

        streamdeck.save()
        if check_connection(streamdeck):
            update_brightness(streamdeck)
        serializer = StreamdeckSerializer(streamdeck)

        return JsonResponse(serializer.data, safe=False)

    elif request.method == 'DELETE':
        streamdeck.delete()
        return HttpResponse(status=204)


@csrf_exempt
def streamdeck_folders(request, id):
    try:
        streamdeck = Streamdeck.objects.get(id=id)
    except Streamdeck.DoesNotExist:
        return HttpResponse(f"Stream deck with id {id} not found", status=404)

    if request.method == 'GET':
        folder_ids = StreamdeckKey.objects.filter(
            streamdeck=streamdeck).values("folder").distinct()
        folders = Folder.objects.filter(id__in=folder_ids)
        serializer = FolderSerializer(folders, many=True)
        return JsonResponse(serializer.data, safe=False)


def streamdeck_folder(request, deck_id, id):
    try:
        streamdeck = Streamdeck.objects.get(id=deck_id)
    except Streamdeck.DoesNotExist:
        return HttpResponse(f"Stream deck with id {deck_id} not found", status=404)

    try:
        folder_ids = StreamdeckKey.objects.filter(
            streamdeck=streamdeck).values("folder").distinct()
        folder = Folder.objects.filter(id__in=folder_ids).get(id=id)
    except Folder.DoesNotExist:
        return HttpResponse(f"Folder with id {id} not found", status=404)

    if request.method == 'GET':
        serializer = FolderSerializer(folder)
        return JsonResponse(serializer.data, safe=False)


@csrf_exempt
def key_detail(request, id):

    try:
        streamdeckKey = StreamdeckKey.objects.get(id=id)
    except StreamdeckKey.DoesNotExist:
        return HttpResponse(f"Stream deck key with id {id} not found", status=404)

    if request.method == 'GET':
        serializer = StreamdeckKeySerializer(streamdeckKey)
        return JsonResponse(serializer.data, safe=False)

    if request.method == 'PATCH':
        data = JSONParser().parse(request)

        streamdeckKey.text = data.get("text", streamdeckKey.text)
        streamdeckKey.clock = data.get("clock", streamdeckKey.clock)
        streamdeckKey.save()
        if check_connection(streamdeckKey.streamdeck):
            update_key_display(streamdeckKey)
        serializer = StreamdeckKeySerializer(streamdeckKey)

        return JsonResponse(serializer.data, safe=False)

    if request.method == 'DELETE':
        streamdeckKey.image_source = ""
        if check_connection(streamdeckKey.streamdeck):
            update_key_display(streamdeckKey)
        streamdeckKey.save()

        return HttpResponse(status=204)


@csrf_exempt
@api_view(['PUT'])
def key_image_upload(request, id):

    try:
        streamdeckKey = StreamdeckKey.objects.get(id=id)
    except StreamdeckKey.DoesNotExist:
        return HttpResponse(f"Stream deck key with id {id} not found", status=404)

    if request.method == 'PUT':
        serializer = StreamdeckKeyImageSerializer(
            streamdeckKey, data=request.data)

        if serializer.is_valid():
            serializer.save()

            if check_connection(streamdeckKey.streamdeck):
                update_key_display(streamdeckKey)
            return HttpResponse("Image uploaded successfully", serializer.data)

        return HttpResponse(status=404)


@csrf_exempt
def command_create(request, id):

    try:
        streamdeckKey = StreamdeckKey.objects.get(id=id)
    except StreamdeckKey.DoesNotExist:
        return HttpResponse(f"Stream deck key with id {id} not found", status=404)

    if request.method == 'PUT':
        data = JSONParser().parse(request)

        com_name = data["name"]
        com_command_string = data.get('command_string', "")
        com_following_command = data.get('following_command', None)
        com_type = data.get("command_type", 'shell')
        com_time_value = data.get("time_value", -1)
        com_directory = data.get("active_directory", ".")
        if (com_type, com_type) not in Command.COMMAND_CHOICES:
            return HttpResponse("Command type not valid", status=400)

        hotkeys = data.get("hotkeys", None)
        com_hotkeys = None

        hotkeysJson = data.get("hotkeys", None)
        if hotkeysJson:
            hotkeys = hotkeys_helper(hotkeysJson)
            hotkeys.save()
            com_hotkeys = hotkeys

        command = Command.objects.create(
            name=com_name, command_string=com_command_string,
            following_command=com_following_command,
            time_value=com_time_value,
            command_type=com_type, active_directory=com_directory)

        if com_hotkeys:
            command.hotkeys = com_hotkeys
        command.save()

        # command is attached to the last command in the queue
        if not streamdeckKey.command:
            streamdeckKey.command = command
            streamdeckKey.save()
        else:
            last_command = streamdeckKey.command
            while last_command.following_command:
                last_command = last_command.following_command
            last_command.following_command = command
            last_command.save()

        if check_connection(streamdeckKey.streamdeck):
            update_key_behavior(streamdeckKey)
        serializer = CommandSerializer(command)
        return JsonResponse(serializer.data, safe=False)


@csrf_exempt
def command_detail(request, key_id, id):

    try:
        streamdeckKey = StreamdeckKey.objects.get(id=key_id)
    except StreamdeckKey.DoesNotExist:
        return HttpResponse(f"Stream deck key with id {id} not found", status=404)

    # command needs to be attached to the key

    command = streamdeckKey.command
    ids = []
    while command:
        ids.append(command.id)
        command = command.following_command

    if id not in ids:
        return HttpResponse(f"Command with id {id} not found under this stream deck key", status=404)

    try:
        command = Command.objects.get(id=id)
    except Command.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = CommandSerializer(command)
        return JsonResponse(serializer.data, safe=False)

    if request.method == 'PATCH':
        data = JSONParser().parse(request)

        command.name = data.get("name", command.name)
        command.command_string = data.get(
            "command_string", command.command_string)
        command.active_directory = data.get(
            "active_directory", command.active_directory)
        command.time_value = data.get(
            "time_value", command.time_value
        )
        com_type = data.get("command_type", command.command_type)
        if (com_type, com_type) not in Command.COMMAND_CHOICES:
            return HttpResponse("command type not valid", status=400)
        command.command_type = com_type

        hotkeysJson = data.get("hotkeys", None)
        if hotkeysJson:
            hotkeys = hotkeys_helper(hotkeysJson)
            hotkeys.save()
            command.hotkeys = hotkeys

        command.save()
        serializer = CommandSerializer(command)

        return JsonResponse(serializer.data, safe=False)

    if request.method == 'DELETE':
        command.delete()
        return HttpResponse("command deleted successfully", status=204)


# convert received json to a hotkeys object
def hotkeys_helper(hotkeysListJson):
    hotkeys = Hotkeys.objects.create()
    for hotkey in hotkeysListJson:
        if "key1" in hotkey:
            key = hotkey["key1"]["key"]
            if hotkey["key1"]["location"] == 1:
                key = key + "_l"
            if hotkey["key1"]["location"] == 2:
                key = key + "_r"
            hotkeys.key1 = key

        if "key2" in hotkey:
            key = hotkey["key2"]["key"]
            if hotkey["key2"]["location"] == 1:
                key = key + "_l"
            if hotkey["key2"]["location"] == 2:
                key = key + "_r"
            hotkeys.key2 = key

        if "key3" in hotkey:
            key = hotkey["key3"]["key"]
            if hotkey["key3"]["location"] == 1:
                key = key + "_l"
            if hotkey["key3"]["location"] == 2:
                key = key + "_r"
            hotkeys.key3 = key

        if "key4" in hotkey:
            key = hotkey["key4"]["key"]
            if hotkey["key4"]["location"] == 1:
                key = key + "_l"
            if hotkey["key4"]["location"] == 2:
                key = key + "_r"
            hotkeys.key4 = key

        if "key5" in hotkey:
            key = hotkey["key5"]["key"]
            if hotkey["key5"]["location"] == 1:
                key = key + "_l"
            if hotkey["key5"]["location"] == 2:
                key = key + "_r"
            hotkeys.key5 = key
    return hotkeys


@csrf_exempt
def hotkeys_detail(request, key_id, command_id):

    try:
        streamdeckKey = StreamdeckKey.objects.get(id=key_id)
    except StreamdeckKey.DoesNotExist:
        return HttpResponse(f"Stream deck key with id {key_id} not found",  status=404)

    # command needs to be attached to the key

    command = streamdeckKey.command
    ids = []
    while command:
        ids.append(command.id)
        command = command.following_command

    if command_id not in ids:
        return HttpResponse(f"Command with id {command_id}not found under this key", status=404)

    try:
        command = Command.objects.get(id=command_id)
    except Command.DoesNotExist:
        return HttpResponse(status=404)

    try:
        hotkeys = Hotkeys.objects.get(id=command.hotkeys.id)
    except Hotkeys.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = HotkeysSerializer(hotkeys)
        return JsonResponse(serializer.data, safe=False)

    if request.method == 'PATCH':
        data = JSONParser().parse(request)

        hotkeys.key1 = data.get("key1", hotkeys.key1)
        hotkeys.key2 = data.get("key2", hotkeys.key2)
        hotkeys.key3 = data.get("key3", hotkeys.key3)
        hotkeys.key4 = data.get("key4", hotkeys.key4)
        hotkeys.key5 = data.get("key5", hotkeys.key5)

        try:
            hotkeys.save()
        except ValueError:
            return HttpResponse("Only Keycodes may be assigned to keys, "
                                "not strings", status=400)

        serializer = HotkeysSerializer(hotkeys)

        return JsonResponse(serializer.data, safe=False)


@csrf_exempt
def create_folder(request, key_id):
    try:
        streamdeckKey = StreamdeckKey.objects.get(id=key_id)
    except StreamdeckKey.DoesNotExist:
        return HttpResponse(f"Stream deck key with id {id} not found", status=404)

    if request.method == 'PUT':
        data = JSONParser().parse(request)

        if streamdeckKey.change_to_folder is not None:
            return HttpResponse("This stream deck key already leads to a folder!", status=403)
        folder_name = data["name"]

        folder = Folder.objects.create(name=folder_name)

        # set default folder image
        streamdeckKey.image_source = "assets/default-folder.png"
        streamdeckKey.change_to_folder = folder
        streamdeckKey.save()

        # create all keys of the folder
        key_count = streamdeckKey.streamdeck.streamdeck_model.key_count
        for i in range(key_count):
            if i == 0:
                new_key = StreamdeckKey.objects.create(
                    number=i, folder=folder,
                    streamdeck=streamdeckKey.streamdeck,
                    change_to_folder=streamdeckKey.folder,
                    image_source="assets/return-button.png")
            else:
                new_key = StreamdeckKey.objects.create(
                    number=i, folder=folder,
                    streamdeck=streamdeckKey.streamdeck)
            new_key.save()

        serializer = FolderSerializer(folder)
        return JsonResponse(serializer.data, safe=False)

    if request.method == 'DELETE':
        if streamdeckKey.change_to_folder:
            delete_folders(streamdeckKey.change_to_folder)
            return HttpResponse("folder deleted succesfully", status=204)
        else:
            return HttpResponse("this stream deck key does not lead to a folder", status=404)


@csrf_exempt
def change_to_folder(request, id):

    try:
        Folder.objects.get(id=id)
    except Folder.DoesNotExist:
        return HttpResponse(f"Folder with id {id} could not be found", status=404)

    if request.method == 'GET':
        change_folder(id)
        return HttpResponse(status=200)
