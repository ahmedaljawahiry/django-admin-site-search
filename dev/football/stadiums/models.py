"""Models for the stadiums app"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from dev.football.core.models import BaseModel
from dev.football.stadiums.enums import PitchSurfaceType


class Stadium(BaseModel):
    """Model representing a Football Stadium, e.g. The Emirates Stadium"""

    name = models.CharField(max_length=120, help_text=_("The name of the stadium"))
    key = models.SlugField(
        max_length=120,
        help_text=_("Unique key, used in URLs and code references"),
        unique=True,
    )
    capacity = models.IntegerField(help_text=_("The full capacity of the stadium"))

    def __str__(self):
        """Returns the Stadium's name"""
        return self.name


class Pitch(BaseModel):
    """Model representing a Football Pitch"""

    stadium = models.OneToOneField(
        Stadium,
        on_delete=models.CASCADE,
        help_text=_("The stadium that houses this pitch"),
    )
    surface_type = models.CharField(
        max_length=20,
        choices=[(t.name, t.value) for t in PitchSurfaceType],
        help_text=_("The type of playing surface"),
    )
    width = models.PositiveSmallIntegerField(
        help_text=_("The width of the playing surface, in CM")
    )
    length = models.PositiveSmallIntegerField(
        help_text=_("The length of the playing surface, in CM")
    )
