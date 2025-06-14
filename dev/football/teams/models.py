"""Models for the teams app"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from dev.football.core.models import BaseModel
from dev.football.teams.enums import SquadType, TeamType


class Team(BaseModel):
    """Model representing a Football Team, e.g. Arsenal FC or England"""

    name = models.CharField(
        max_length=120, help_text=_("The official name of the football team")
    )
    key = models.SlugField(
        max_length=120,
        help_text=_("Unique key, used in URLs and code references"),
        unique=True,
    )
    type = models.CharField(
        max_length=10,
        choices=[(t.name, t.value) for t in TeamType],
        help_text=_("The type of team"),
    )
    website = models.URLField(help_text=_("Link to the official website"))
    motto = models.CharField(
        max_length=255, help_text=_("The official motto/slogan of the club")
    )
    description = models.TextField(
        help_text=_("A description of the team and it's history")
    )
    stadium = models.ForeignKey(
        "stadiums.Stadium",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text=_("The stadium that the team currently plays in, as home"),
    )

    def __str__(self):
        """Returns the Team's name"""
        return self.name


class Squad(BaseModel):
    """Model representing a squad of players, e.g. Men's first team"""

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        help_text=_("The team that owns this squad"),
    )
    type = models.CharField(
        max_length=20,
        choices=[(t.name, t.value) for t in SquadType],
        help_text=_("The type of squad"),
    )
    players = models.ManyToManyField(
        "players.Player",
        help_text=_("Football players in this team/squad"),
        blank=True,
    )
