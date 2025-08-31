from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),   # root page
    path("upload_selfie/", views.upload_selfie, name="upload_selfie"),
    path("my_photos/", views.my_photos, name="my_photos"),
]

