from django.urls import path
from streamdeck import views


urlpatterns = [
    path('streamdecks', views.streamdeck_list),
    path('streamdecks/<int:id>', views.streamdeck_detail),
    path('streamdecks/<int:id>/image_upload', views.streamdeck_image),
    path('streamdecks/<int:id>/image_delete', views.streamdeck_delete_image),
    path('streamdecks/<int:id>/screensaver_image_upload', views.screensaver_image),
    path('streamdecks/<int:id>/screensaver_image_delete', views.screensaver_delete_image),
    path('streamdecks/<int:id>/folders', views.streamdeck_folders),
    path('streamdecks/<int:deck_id>/folders/<int:id>',
         views.streamdeck_folder),
    path('key/<int:id>', views.key_detail),
    path('key/<int:id>/run_commands', views.run_key_commands),
    path('key/<int:id>/image_upload', views.key_image_upload),
    path('key/<int:id>/image', views.key_image),
    path('key/<int:id>/command', views.command_create),
    path('key/<int:key_id>/command/<int:id>', views.command_detail),
    path('key/<int:key_id>/folder', views.create_folder),
]
