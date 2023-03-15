from django.contrib import admin

from dev.football.core.admin import BaseAdmin
from dev.football.stadiums.models import Stadium, Pitch


@admin.register(Stadium)
class StadiumAdmin(BaseAdmin):
    """Admin for the Stadium model"""

    pass


@admin.register(Pitch)
class PitchAdmin(BaseAdmin):
    """Admin for the Pitch model"""

    pass
