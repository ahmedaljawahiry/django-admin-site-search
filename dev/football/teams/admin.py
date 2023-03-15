from django.contrib import admin

from dev.football.core.admin import BaseAdmin
from dev.football.teams.models import Team, Squad


@admin.register(Team)
class TeamAdmin(BaseAdmin):
    """Admin for the Team model"""

    pass


@admin.register(Squad)
class SquadAdmin(BaseAdmin):
    """Admin for the Squad model"""

    pass
