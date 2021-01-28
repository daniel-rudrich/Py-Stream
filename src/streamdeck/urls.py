from django.urls import path
from streamdeck import views


urlpatterns = [
    path('streamdecks', views.streamdeck_list),
    path('streamdecks/<int:id>', views.streamdeck_detail),
    path('streamdeck/<int:id>/folders', views.streamdeck_folders),
    path('streamdeck/<int:deck_id>/folders/<int:id>', views.streamdeck_folder),
    path('key/<int:id>', views.key_detail),
    path('key/<int:id>/command', views.command_create),
    path('key/<int:key_id>/command/<int:id>', views.command_detail),
    path('key/<int:key_id>/folder', views.create_folder),
    path('change_folder/<int:id>', views.change_to_folder)
]
