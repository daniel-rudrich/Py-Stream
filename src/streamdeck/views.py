# from django.shortcuts import render
from rest_framework import viewsets, permissions
from .serializers import StreamdeckKeySerializer, FolderSerializer, StreamdeckSerializer, CommandSerializer, StreamdeckModelSerializer
from .models import Streamdeck, StreamdeckKey, Folder, Command, StreamdeckModel
from .streamdeck_comm.streamdeck_functions import streamdeck_init

# Create your views here.


class StreamdeckKeyViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows StreamdeckKeys to be viewed or edited
    """
    streamdeck_init()  # This method is used here for testing purposes
    queryset = StreamdeckKey.objects.all().order_by('id')
    serializer_class = StreamdeckKeySerializer
    permissions_classes = [permissions.IsAuthenticated]


class StreamdeckViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Folder to be viewed or edited
    """
    queryset = Streamdeck.objects.all().order_by('id')
    serializer_class = StreamdeckSerializer
    permissions_classes = [permissions.IsAuthenticated]


class CommandViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Folder to be viewed or edited
    """
    queryset = Command.objects.all().order_by('id')
    serializer_class = CommandSerializer
    permissions_classes = [permissions.IsAuthenticated]


class StreamdeckModelViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Folder to be viewed or edited
    """
    queryset = StreamdeckModel.objects.all().order_by('id')
    serializer_class = StreamdeckModelSerializer
    permissions_classes = [permissions.IsAuthenticated]


class FolderViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Folder to be viewed or edited
    """
    queryset = Folder.objects.all().order_by('id')
    serializer_class = FolderSerializer
    permissions_classes = [permissions.IsAuthenticated]
