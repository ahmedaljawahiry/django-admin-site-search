"""URL conf for a project where the admin site is the index URL"""

from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("", admin.site.urls),
]
