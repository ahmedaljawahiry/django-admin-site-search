"""URL conf for a project where the admin site is on a custom URL"""

from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("custom/", admin.site.urls),
]
