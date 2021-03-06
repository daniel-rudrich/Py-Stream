"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import sys
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from config.views import home
from streamdeck.streamdeck_comm.streamdeck_interface import streamdecks_init

urlpatterns = [
    path('', home),
    path('admin/', admin.site.urls),
    path('api/', include('streamdeck.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
    + static(settings.FRONTEND_URL, document_root=settings.FRONTEND_ROOT)

# initialize connection to streamdeck
if 'runserver' in sys.argv:
    streamdecks_init()
