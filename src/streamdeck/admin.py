from django.contrib import admin
from .models import StreamdeckKey, Streamdeck, Folder, Command, StreamdeckModel

# Register your models here.
admin.site.register(StreamdeckKey)
admin.site.register(Streamdeck)
admin.site.register(Folder)
admin.site.register(Command)
admin.site.register(StreamdeckModel)
