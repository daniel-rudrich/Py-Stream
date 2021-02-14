# from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser

from .serializers import (
    StreamdeckKeySerializer, FolderSerializer,
    StreamdeckSerializer, CommandSerializer,
    StreamdeckKeyImageSerializer)
from .models import Streamdeck, StreamdeckKey, Folder, Command
from .streamdeck_comm.streamdeck_interface import (change_folder,
                                                   update_key_behavior,
                                                   update_key_display,
                                                   update_brightness,
                                                   check_connection)

# Create your views here.


@csrf_exempt
def streamdeck_list(request):
    """
    List all streamdecks
    """
    if request.method == 'GET':
        streamdecks = Streamdeck.objects.all()
        serializer = StreamdeckSerializer(streamdecks, many=True)
        return JsonResponse(serializer.data, safe=False)


@csrf_exempt
def streamdeck_detail(request, id):
    """
    Retrieve, update or delete a code snippet
    """
    try:
        streamdeck = Streamdeck.objects.get(id=id)
    except Streamdeck.DoesNotExist:
        return HttpResponse(status=404)

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
    """
    List all folder of a streamdeck
    """
    try:
        streamdeck = Streamdeck.objects.get(id=id)
    except Streamdeck.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        folder_ids = StreamdeckKey.objects.filter(
            streamdeck=streamdeck).values("folder").distinct()
        folders = Folder.objects.filter(id__in=folder_ids)
        serializer = FolderSerializer(folders, many=True)
        return JsonResponse(serializer.data, safe=False)


def streamdeck_folder(request, deck_id, id):
    try:
        Streamdeck.objects.get(id=deck_id)
    except Streamdeck.DoesNotExist:
        return HttpResponse(status=404)

    try:
        folder = Folder.objects.get(id=id)
    except Folder.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = FolderSerializer(folder)
        return JsonResponse(serializer.data, safe=False)


@csrf_exempt
def key_detail(request, id):

    try:
        streamdeckKey = StreamdeckKey.objects.get(id=id)
    except StreamdeckKey.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        serializer = StreamdeckKeySerializer(streamdeckKey)
        return JsonResponse(serializer.data, safe=False)

    if request.method == 'PATCH':
        data = JSONParser().parse(request)

        streamdeckKey.text = data.get("text", streamdeckKey.text)
        streamdeckKey.save()
        if check_connection(streamdeckKey.streamdeck):
            update_key_display(streamdeckKey)
        serializer = StreamdeckKeySerializer(streamdeckKey)

        return JsonResponse(serializer.data, safe=False)


@csrf_exempt
@api_view(['PUT'])
def key_image_upload(request, id):

    try:
        streamdeckKey = StreamdeckKey.objects.get(id=id)
    except StreamdeckKey.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'PUT':
        serializer = StreamdeckKeyImageSerializer(
            streamdeckKey, data=request.data)

        if serializer.is_valid():
            serializer.save()

            if check_connection(streamdeckKey.streamdeck):
                update_key_display(streamdeckKey)
            return HttpResponse(serializer.data)

        return HttpResponse(status=404)


@csrf_exempt
def command_create(request, id):

    try:
        streamdeckKey = StreamdeckKey.objects.get(id=id)
    except StreamdeckKey.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'PUT':
        data = JSONParser().parse(request)

        com_name = data["name"]
        com_command_string = data['command_string']
        com_value = data.get('value', None)
        com_following_command = data.get('following_command', None)

        command = Command.objects.create(
            name=com_name, command_string=com_command_string,
            value=com_value, following_command=com_following_command)

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
        return HttpResponse("streamdeckKey could not be found", status=404)

    # command needs to be attached to the key

    command = streamdeckKey.command
    ids = []
    while command:
        ids.append(command.id)
        command = command.following_command

    if id not in ids:
        return HttpResponse("command not found under this key", status=404)

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
        command.value = data.get("value", command.value)

        following_command_id = data.get("following_command", None)
        if following_command_id:
            try:
                following_command = Command.objects.get(
                    id=following_command_id)
            except Command.DoesNotExist:
                return HttpResponse("The following_command id doe not lead to an existing command", status=404)
            if following_command:
                command.following_command = following_command

        command.save()
        serializer = CommandSerializer(command)

        return JsonResponse(serializer.data, safe=False)

    if request.method == 'DELETE':
        command.delete()
        return HttpResponse(status=204)


@csrf_exempt
def create_folder(request, key_id):
    try:
        streamdeckKey = StreamdeckKey.objects.get(id=key_id)
    except StreamdeckKey.DoesNotExist:
        return HttpResponse("streamdeckKey could not be found", status=404)

    if request.method == 'PUT':
        data = JSONParser().parse(request)

        folder_name = data["name"]

        folder = Folder.objects.create(name=folder_name)

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
                    image_source="images/return-button.png")
            else:
                new_key = StreamdeckKey.objects.create(
                    number=i, folder=folder,
                    streamdeck=streamdeckKey.streamdeck)
            new_key.save()

        serializer = FolderSerializer(folder)
        return JsonResponse(serializer.data, safe=False)

    if request.method == 'DELETE':
        if streamdeckKey.change_to_folder:
            streamdeckKey.change_to_folder.delete()
            return HttpResponse(status=204)
        else:
            return HttpResponse(status=404)


@csrf_exempt
def change_to_folder(request, id):

    try:
        Folder.objects.get(id=id)
    except Folder.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        change_folder(id)
        return HttpResponse(status=200)
