from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [

    url(r'^$', views.upload_file),
    url(r'^chord$', views.get_file, name='register'),

]