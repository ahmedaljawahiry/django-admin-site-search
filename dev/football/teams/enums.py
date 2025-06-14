"""Enums for the football app"""

from enum import Enum

from django.utils.translation import gettext_lazy as _


class TeamType(Enum):
    """Type of Team"""

    CLUB = _("Club")
    NATIONAL = _("National")


class SquadType(Enum):
    """Type of Squad"""

    SENIOR_MEN = _("Senior men's team")
    SENIOR_WOMEN = _("Senior women's team")
    ACADEMY = _("Academy")
    CHARITY = _("Charity team")
