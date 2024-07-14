from django.contrib import admin

from dev.football.core.admin import BaseAdmin
from dev.football.teams.models import Squad, Team


@admin.register(Team)
class TeamAdmin(BaseAdmin):
    """Admin for the Team model"""

    search_fields = ("name", "description", "=key")


@admin.register(Squad)
class SquadAdmin(BaseAdmin):
    """Admin for the Squad model"""

    search_fields = ("team__name", "players__name")
