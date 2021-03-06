"""capstone URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
import ChordialMusic.views
from ChordialMusic import views

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^$', include('ChordialMusic.urls')),
    url(r'^chord$', views.get_file, name='chord'),
    url(r'^download_chord$', views.download_file, name='download'),
    url(r'^default_path$', views.get_temp_file_path, name='download'),
    url(r'^get_chords$', views.get_chords, name='get_chords'),
    url(r'^update_rating$', views.update_rating, name='update_rating'),
]
